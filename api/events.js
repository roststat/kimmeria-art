import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 3,
});

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'public, max-age=60');

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { rows } = await pool.query(`
      SELECT
        slug, title, description, description_short, date, date_label,
        format, location, price, image_url, custom_banner, ticket_url, status
      FROM events
      WHERE status = 'published'
      ORDER BY date ASC
    `);

    const events = rows.map(r => ({
      id:          r.slug,
      title:       r.title,
      description: r.description_short || r.description,
      date:        r.date,
      date_label:  r.date_label,
      format:      r.format,
      location:    r.location,
      price:       r.price,
      image:       r.custom_banner || r.image_url,
      url:         `https://art-kimmeria.ru/programmy/${r.slug}/`,
      ticket_url:  r.ticket_url || null,
    }));

    return res.status(200).json(events);
  } catch (err) {
    console.error('DB error:', err.message);
    return res.status(500).json({ error: 'Database error' });
  }
}
