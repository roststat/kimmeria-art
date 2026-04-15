// Запуск: node migrate.js
// Применяет схему и переносит events.json в Neon

const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

// Читаем .env вручную (без dotenv)
const envFile = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
const dbUrl = envFile.match(/DATABASE_URL=(.+)/)?.[1]?.trim();

if (!dbUrl) {
  console.error('DATABASE_URL не найден в .env');
  process.exit(1);
}

const events = JSON.parse(fs.readFileSync(path.join(__dirname, 'events.json'), 'utf8'));

async function main() {
  const client = new Client({ connectionString: dbUrl });
  await client.connect();
  console.log('Подключились к Neon');

  // Создаём таблицы
  const schema = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
  await client.query(schema);
  console.log('Схема применена');

  // Переносим мероприятия из events.json
  let inserted = 0;
  let skipped = 0;

  for (const e of events) {
    // Парсим дату и время из date_label
    const timeMatch = e.date_label?.match(/(\d{2}:\d{2})/);
    const time = timeMatch ? timeMatch[1] : '19:00';

    try {
      await client.query(`
        INSERT INTO events (
          slug, status, title, description, date, time, date_label,
          format, location, price, image_url, source
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        ON CONFLICT (slug) DO NOTHING
      `, [
        e.id,
        'published',
        e.title,
        e.description,
        e.date,
        time,
        e.date_label,
        e.format,
        e.location,
        e.price,
        e.image,
        'legacy'
      ]);
      inserted++;
      console.log(`✓ ${e.id}`);
    } catch (err) {
      console.error(`✗ ${e.id}: ${err.message}`);
      skipped++;
    }
  }

  console.log(`\nГотово: ${inserted} перенесено, ${skipped} пропущено`);
  await client.end();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
