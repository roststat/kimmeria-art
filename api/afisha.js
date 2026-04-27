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
  res.setHeader('Access-Control-Allow-Origin', 'https://art-kimmeria.ru');
  res.setHeader('Access-Control-Allow-Methods', 'POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-admin-password');

  if (req.method === 'OPTIONS') return res.status(200).end();

  if (!checkAdmin(req, res)) return;

  const { id } = req.query;

  try {
    // POST /api/afisha — добавить программу в афишу главной
    if (req.method === 'POST') {
      const {
        slug, title, description, date, time, date_label,
        format, location, price, image_url, ticket_url, age,
      } = req.body;

      if (!slug || !title || !date) {
        return res.status(400).json({ error: 'slug, title, date required' });
      }

      // Upsert — если уже есть, обновляем дату/цену
      const { rows: [event] } = await pool.query(`
        INSERT INTO events
          (slug, title, description, date, time, date_label, format, location,
           price, image_url, ticket_url, age, status, source)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,'published','admin')
        ON CONFLICT (slug) DO UPDATE SET
          date       = EXCLUDED.date,
          time       = EXCLUDED.time,
          date_label = EXCLUDED.date_label,
          price      = EXCLUDED.price,
          status     = 'published',
          updated_at = now()
        RETURNING id, slug, title, date, status
      `, [
        slug,
        title,
        description || '',
        date,
        time || '19:00',
        date_label || '',
        format || 'мероприятие',
        location || 'Арт-пространство «Киммерия», ул. Игнатенко, 5',
        price || 'По запросу',
        image_url || '',
        ticket_url || null,
        age || null,
      ]);

      return res.status(200).json({ ok: true, event });
    }

    // DELETE /api/afisha?id=slug — снять с публикации
    if (req.method === 'DELETE' && id) {
      await pool.query(
        `UPDATE events SET status='draft', updated_at=now() WHERE slug=$1`,
        [id]
      );
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'Unknown action' });

  } catch (err) {
    console.error('DB error:', err.message);
    return res.status(500).json({ error: 'Database error: ' + err.message });
  }
}
