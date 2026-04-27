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

function generateToken() {
  return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-admin-password');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const { action, token, id } = req.query;

  try {
    // GET /api/schedules?token=xxx — публичный, для виджета
    if (req.method === 'GET' && token) {
      const { rows: [schedule] } = await pool.query(
        'SELECT * FROM schedules WHERE token = $1', [token]
      );
      if (!schedule) return res.status(404).json({ error: 'Not found' });

      const { rows: items } = await pool.query(
        `SELECT * FROM schedule_items WHERE schedule_id = $1 ORDER BY event_date ASC, sort_order ASC`,
        [schedule.id]
      );

      return res.status(200).json({ schedule, items });
    }

    // GET /api/schedules — список всех (только для админа)
    if (req.method === 'GET') {
      if (!checkAdmin(req, res)) return;
      const { rows } = await pool.query(
        'SELECT * FROM schedules ORDER BY created_at DESC'
      );
      return res.status(200).json(rows);
    }

    // POST /api/schedules — создать расписание
    if (req.method === 'POST' && !action) {
      if (!checkAdmin(req, res)) return;
      const { title, client_name } = req.body;
      if (!title || !client_name) return res.status(400).json({ error: 'title and client_name required' });

      const token = generateToken();
      const { rows: [schedule] } = await pool.query(
        'INSERT INTO schedules (token, title, client_name) VALUES ($1, $2, $3) RETURNING *',
        [token, title, client_name]
      );
      return res.status(201).json(schedule);
    }

    // POST /api/schedules?action=add-item — добавить программу в расписание
    if (req.method === 'POST' && action === 'add-item') {
      if (!checkAdmin(req, res)) return;
      const { schedule_id, program_slug, program_title, program_image, event_date, event_time, price } = req.body;
      if (!schedule_id || !program_slug || !event_date) {
        return res.status(400).json({ error: 'schedule_id, program_slug, event_date required' });
      }

      const { rows: [item] } = await pool.query(
        `INSERT INTO schedule_items
          (schedule_id, program_slug, program_title, program_image, event_date, event_time, price)
         VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *`,
        [schedule_id, program_slug, program_title || '', program_image || '', event_date, event_time || '19:00', price || 'По запросу']
      );
      return res.status(201).json(item);
    }

    // PUT /api/schedules?id=xxx — обновить программу в расписании
    if (req.method === 'PUT' && id) {
      if (!checkAdmin(req, res)) return;
      const { event_date, event_time, price } = req.body;
      const { rows: [item] } = await pool.query(
        `UPDATE schedule_items SET event_date=$1, event_time=$2, price=$3 WHERE id=$4 RETURNING *`,
        [event_date, event_time, price, id]
      );
      return res.status(200).json(item);
    }

    // DELETE /api/schedules?id=xxx&action=item — удалить программу из расписания
    if (req.method === 'DELETE' && action === 'item' && id) {
      if (!checkAdmin(req, res)) return;
      await pool.query('DELETE FROM schedule_items WHERE id=$1', [id]);
      return res.status(200).json({ ok: true });
    }

    // DELETE /api/schedules?id=xxx — удалить расписание целиком
    if (req.method === 'DELETE' && id) {
      if (!checkAdmin(req, res)) return;
      await pool.query('DELETE FROM schedules WHERE id=$1', [id]);
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'Unknown action' });

  } catch (err) {
    console.error('DB error:', err.message);
    return res.status(500).json({ error: 'Database error' });
  }
}
