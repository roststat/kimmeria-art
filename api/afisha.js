import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 3,
});

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'kimmeria';

function checkAdmin(req, res) {
  const auth = req.headers['x-admin-password'];
  if (auth !== ADMIN_PASSWORD) {
    res.status(401).json({ error: 'Unauthorized' });
    return false;
  }
  return true;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-admin-password');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const { id } = req.query;

  try {
    // GET /api/afisha?id=slug — получить данные программы (публичный)
    if (req.method === 'GET' && id) {
      const { rows: [event] } = await pool.query(
        `SELECT slug, title, description, description_short, date, time, date_label,
                format, location, price, image_url, custom_banner, ticket_url, age, status
         FROM events WHERE slug = $1`, [id]
      );
      return res.status(200).json(event || null);
    }

    if (!checkAdmin(req, res)) return;

    // POST /api/afisha — добавить/обновить программу в афише главной
    if (req.method === 'POST') {
      const {
        slug, title, description, description_short, date, time, date_label,
        format, location, price, image_url, custom_banner, ticket_url, age,
      } = req.body;

      if (!slug || !title || !date) {
        return res.status(400).json({ error: 'slug, title, date required' });
      }

      const { rows: [event] } = await pool.query(`
        INSERT INTO events
          (slug, title, description, description_short, date, time, date_label, format,
           location, price, image_url, custom_banner, ticket_url, age, status, source)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,'published','admin')
        ON CONFLICT (slug) DO UPDATE SET
          date             = EXCLUDED.date,
          time             = EXCLUDED.time,
          date_label       = EXCLUDED.date_label,
          price            = EXCLUDED.price,
          status           = 'published',
          updated_at       = now()
        RETURNING id, slug, title, date, status
      `, [
        slug, title,
        description || '',
        description_short || '',
        date, time || '19:00', date_label || '',
        format || 'мероприятие',
        location || 'Арт-пространство «Киммерия», ул. Игнатенко, 5',
        price || 'По запросу',
        image_url || '',
        custom_banner || null,
        ticket_url || null,
        age || null,
      ]);

      return res.status(200).json({ ok: true, event });
    }

    // PATCH /api/afisha?id=slug — синхронизировать метаданные программы
    if (req.method === 'PATCH' && id) {
      const { title, description, description_short, image_url, custom_banner, price, format, age } = req.body;

      // Upsert — создаём запись если нет, иначе обновляем только метаданные
      await pool.query(`
        INSERT INTO events (slug, title, description, description_short, image_url, custom_banner,
                            price, format, age, date, time, date_label, location, status, source)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,'1970-01-01','00:00','','','draft','program')
        ON CONFLICT (slug) DO UPDATE SET
          title            = EXCLUDED.title,
          description      = EXCLUDED.description,
          description_short= EXCLUDED.description_short,
          image_url        = COALESCE(NULLIF(EXCLUDED.image_url,''), events.image_url),
          custom_banner    = COALESCE(EXCLUDED.custom_banner, events.custom_banner),
          price            = EXCLUDED.price,
          format           = EXCLUDED.format,
          age              = EXCLUDED.age,
          updated_at       = now()
      `, [id, title||'', description||'', description_short||'',
          image_url||'', custom_banner||null, price||'', format||'', age||null]);

      return res.status(200).json({ ok: true });
    }

    // PATCH /api/afisha?id=slug&action=banner — обновить только кастомный баннер
    if (req.method === 'PATCH' && id && req.query.action === 'banner') {
      const { custom_banner } = req.body;
      await pool.query(
        `UPDATE events SET custom_banner=$1, updated_at=now() WHERE slug=$2`,
        [custom_banner || null, id]
      );
      return res.status(200).json({ ok: true });
    }

    // DELETE /api/afisha?id=slug — снять с публикации
    if (req.method === 'DELETE' && id) {
      await pool.query(
        `UPDATE events SET status='draft', updated_at=now() WHERE slug=$1`, [id]
      );
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'Unknown action' });

  } catch (err) {
    console.error('DB error:', err.message);
    return res.status(500).json({ error: 'Database error: ' + err.message });
  }
}
