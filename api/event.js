import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 3,
});

function formatDateRu(dateStr, time) {
  const months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
  const days = ['Воскресенье','Понедельник','Вторник','Среда','Четверг','Пятница','Суббота'];
  const d = new Date(dateStr);
  const dayName = days[d.getDay()];
  return {
    full: `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}, ${dayName}`,
    short: `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`,
    label: `${d.getDate()} ${months[d.getMonth()]} · ${time || '19:00'}`,
    day: dayName,
  };
}

function renderPage(e) {
  const date = formatDateRu(e.date, e.time);
  const img = e.custom_banner || e.image_url || '';
  const today = new Date(); today.setHours(0,0,0,0);
  const isPast = new Date(e.date) < today;
  const programUrl = `https://art-kimmeria.ru/programmy/${e.slug}/`;
  const eventUrl   = `https://art-kimmeria.ru/event/${e.slug}/`;

  const ticketBtn = e.ticket_url && !isPast
    ? `<a href="${e.ticket_url}" class="btn-primary" target="_blank" rel="noopener">Купить билет</a>`
    : isPast
    ? `<div class="btn-past">Мероприятие завершено</div>`
    : `<div class="btn-past">Билеты скоро</div>`;

  return `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${e.title} — Киммерия-Арт</title>
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Киммерия-Арт">
  <meta property="og:url" content="${eventUrl}">
  <meta property="og:title" content="${e.title} · ${date.short}">
  <meta property="og:description" content="${e.description || ''}">
  <meta property="og:image" content="${img}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; background: #ffffff; color: #111111; font-size: 16px; line-height: 1.6; overflow-x: hidden; }
    nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-bottom: 1px solid #e8e8e8; }
    .nav-logo { font-size: 17px; font-weight: 700; color: #111111; text-decoration: none; letter-spacing: 0.06em; text-transform: uppercase; }
    .nav-back { font-size: 13px; font-weight: 600; color: #111111; text-decoration: none; padding: 8px 16px; border-radius: 100px; border: 1px solid #e8e8e8; transition: background 0.15s; }
    .nav-back:hover { background: #f5f5f5; }
    .event-hero { padding-top: 60px; position: relative; overflow: hidden; background: #0d0d0d; }
    .event-hero-bg { position: absolute; inset: -40px; background-size: cover; background-position: center; filter: blur(28px); opacity: 0.55; transform: scale(1.08); }
    .event-hero-inner { position: relative; z-index: 1; display: grid; grid-template-columns: auto 1fr; gap: 48px; align-items: center; max-width: 1200px; margin: 0 auto; padding: 48px; }
    .event-hero-poster { flex-shrink: 0; max-height: 580px; max-width: 380px; }
    .event-hero-poster img { display: block; width: 100%; height: auto; object-fit: contain; border-radius: 8px; box-shadow: 0 24px 64px rgba(0,0,0,0.6); }
    .event-hero-text { color: #ffffff; }
    .event-trailer { margin-top: 40px; margin-bottom: 8px; }
    .event-trailer .section-label { margin-bottom: 16px; }
    .trailer-wrap { position: relative; width: 100%; max-width: 720px; aspect-ratio: 16/9; background: #000; border-radius: 12px; overflow: hidden; }
    .trailer-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: none; border-radius: 12px; }
    .event-hero-tag { display: inline-block; background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.25); color: #ffffff; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 5px 12px; border-radius: 100px; margin-bottom: 14px; }
    .event-hero-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
    .event-hero-tags .event-hero-tag { margin-bottom: 0; }
    .event-hero-tag--premiere { background: rgba(220, 38, 38, 0.85); border-color: rgba(220,38,38,0.6); }
    .event-hero-title { font-size: 44px; font-weight: 700; color: #ffffff; line-height: 1.1; margin-bottom: 12px; }
    .event-hero-date { font-size: 15px; font-weight: 500; color: rgba(255,255,255,0.75); }
    .event-main { display: grid; grid-template-columns: 1fr 360px; gap: 48px; max-width: 1200px; margin: 0 auto; padding: 60px 48px; align-items: start; }
    .section-label { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666666; font-weight: 600; margin-bottom: 12px; }
    .event-description { font-size: 20px; font-weight: 500; line-height: 1.65; color: #111111; margin-bottom: 28px; max-width: 620px; }
    .event-text { font-size: 16px; color: #444444; line-height: 1.85; margin-bottom: 20px; max-width: 620px; }
    .event-details-list { list-style: none; margin-bottom: 40px; }
    .event-details-list li { font-size: 16px; color: #666666; padding: 12px 0; border-bottom: 1px solid #e8e8e8; display: flex; gap: 16px; align-items: baseline; }
    .event-details-list li:first-child { border-top: 1px solid #e8e8e8; }
    .event-details-list li strong { color: #111111; font-weight: 600; min-width: 130px; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }
    .event-sidebar { position: sticky; top: 80px; background: #ffffff; border: 1px solid #e8e8e8; border-radius: 16px; padding: 32px; }
    .sidebar-label { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666666; font-weight: 600; margin-bottom: 6px; }
    .sidebar-value { font-size: 22px; font-weight: 700; color: #111111; line-height: 1.3; }
    .sidebar-note { font-size: 14px; color: #666666; margin-top: 6px; }
    .sidebar-divider { border: none; border-top: 1px solid #e8e8e8; margin: 20px 0; }
    .sidebar-place { font-size: 15px; color: #111111; line-height: 1.6; }
    .sidebar-place small { display: block; font-size: 13px; color: #999999; margin-top: 2px; }
    .sidebar-price-main { font-size: 32px; font-weight: 700; color: #111111; margin-bottom: 16px; }
    .sidebar-age { text-align: center; margin-top: 12px; font-size: 12px; color: #666666; }
    .btn-primary { display: block; width: 100%; padding: 16px 24px; text-align: center; background: #111111; color: #ffffff; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; text-decoration: none; border-radius: 100px; transition: opacity 0.15s; }
    .btn-primary:hover { opacity: 0.85; }
    .btn-past { display: block; width: 100%; padding: 14px 24px; text-align: center; background: #f5f5f5; color: #666666; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; border: 1px solid #e8e8e8; border-radius: 100px; }
    .btn-secondary { display: block; width: 100%; padding: 14px 24px; text-align: center; background: #ffffff; color: #111111; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; text-decoration: none; border: 1px solid #e8e8e8; border-radius: 100px; transition: background 0.15s; margin-top: 10px; }
    .btn-secondary:hover { background: #f5f5f5; }
    .btn-program { display: block; width: 100%; padding: 14px 24px; text-align: center; background: #f0faf8; color: #1a4a3a; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; text-decoration: none; border: 1px solid #c8e8e0; border-radius: 100px; transition: background 0.15s; margin-top: 10px; }
    .btn-program:hover { background: #e0f4f0; }
    .btn-share { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px 24px; background: #ffffff; color: #111111; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; border: 1px solid #e8e8e8; border-radius: 100px; cursor: pointer; transition: background 0.15s; margin-top: 10px; position: relative; }
    .btn-share:hover { background: #f5f5f5; }
    .btn-share svg { width: 15px; height: 15px; flex-shrink: 0; }
    .share-popup { position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%) translateY(4px); background: #111111; color: #ffffff; font-size: 12px; padding: 6px 14px; border-radius: 100px; white-space: nowrap; pointer-events: none; opacity: 0; transition: all 0.2s; }
    .share-popup.visible { opacity: 1; transform: translateX(-50%) translateY(0); }
    .back-section { max-width: 1200px; margin: 0 auto; padding: 0 48px 60px; }
    .back-link { font-size: 13px; font-weight: 600; color: #111111; text-decoration: none; padding: 8px 16px; border-radius: 100px; border: 1px solid #e8e8e8; display: inline-block; transition: background 0.15s; }
    .back-link:hover { background: #f5f5f5; }
    footer { background: #111111; padding: 40px 48px; display: flex; justify-content: space-between; align-items: center; }
    .footer-logo { font-size: 17px; font-weight: 700; color: #ffffff; letter-spacing: -0.01em; }
    .footer-links { display: flex; gap: 20px; }
    .footer-links a { font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.15s; }
    .footer-links a:hover { color: #ffffff; }
    .footer-copy { font-size: 12px; color: rgba(255,255,255,0.3); }
    @media (max-width: 900px) {
      nav { padding: 0 20px; } .nav-back { display: none; }
      .event-hero-inner { grid-template-columns: 1fr; padding: 32px 20px; justify-items: center; text-align: center; }
      .event-hero-poster { max-width: 260px; }
      .event-hero-text { width: 100%; text-align: left; }
      .event-hero-tags { justify-content: center; }
      .event-hero-title { font-size: 28px; }
      .event-main { grid-template-columns: 1fr; padding: 32px 20px; gap: 24px; }
      .event-sidebar { position: static; }
      footer { padding: 28px 20px; flex-direction: column; gap: 16px; text-align: center; }
      .back-section { padding: 0 20px 40px; }
    }
    @media (max-width: 600px) {
      .event-hero-title { font-size: 22px; }
      .event-description { font-size: 17px; }
    }
    .overlay { display: none; position: fixed; inset: 0; z-index: 500; background: rgba(0,0,0,0.55); backdrop-filter: blur(4px); align-items: center; justify-content: center; padding: 20px; }
    .overlay.open { display: flex; }
    .popup { background: #fff; border-radius: 24px; max-width: 460px; width: 100%; padding: 44px 40px; position: relative; box-shadow: 0 24px 80px rgba(0,0,0,0.2); animation: popIn 0.25s cubic-bezier(0.34,1.56,0.64,1); }
    @keyframes popIn { from { opacity:0; transform: scale(0.9) translateY(16px); } to { opacity:1; transform: scale(1) translateY(0); } }
    .popup-close { position: absolute; top: 16px; right: 20px; background: none; border: none; font-size: 26px; color: #aaa; cursor: pointer; line-height: 1; }
    .popup-close:hover { color: #111; }
    .popup-title { font-size: 24px; font-weight: 700; color: #111; margin-bottom: 6px; }
    .popup-sub { font-size: 14px; color: #888; margin-bottom: 28px; line-height: 1.5; }
    .reg-form { display: flex; flex-direction: column; gap: 12px; }
    .reg-form input { width: 100%; padding: 15px 18px; font-family: 'Inter', sans-serif; font-size: 15px; color: #111; background: #f7f7f7; border: 1.5px solid #e8e8e8; border-radius: 12px; outline: none; transition: border-color 0.15s, background 0.15s; }
    .reg-form input:focus { border-color: #111; background: #fff; }
    .reg-form input::placeholder { color: #aaa; }
    .form-consent { display: flex; align-items: flex-start; gap: 10px; cursor: pointer; }
    .form-consent input[type="checkbox"] { flex-shrink: 0; width: 16px; height: 16px; margin-top: 3px; cursor: pointer; }
    .form-consent span { font-size: 12px; color: #888; line-height: 1.55; }
    .form-consent a { color: #111; }
    .btn-submit { width: 100%; padding: 16px 24px; background: #111111; color: #ffffff; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; border: none; border-radius: 100px; cursor: pointer; transition: opacity 0.15s; }
    .btn-submit:hover { opacity: 0.85; }
    .btn-submit:disabled { opacity: 0.5; cursor: default; }
    .form-error { font-size: 13px; color: #cc3333; display: none; margin-top: 4px; }
    .btn-register { display: block; width: 100%; padding: 16px 24px; text-align: center; background: #111111; color: #ffffff; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; border: none; border-radius: 100px; cursor: pointer; transition: opacity 0.15s; margin-bottom: 0; }
    .btn-register:hover { opacity: 0.85; }
  </style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">Киммерия-Арт</a>
  <a href="/#events" class="nav-back">← Все события</a>
</nav>

<div class="event-hero">
  <div class="event-hero-bg" style="background-image: url('${img}');"></div>
  <div class="event-hero-inner">
    ${img ? `<div class="event-hero-poster"><img src="${img}" alt="${e.title}"></div>` : ''}
    <div class="event-hero-text">
      <div class="event-hero-tags">
        <div class="event-hero-tag">${e.format || 'Мероприятие'}${e.age ? ' · ' + e.age : ''}</div>
        ${e.is_premiere ? `<div class="event-hero-tag event-hero-tag--premiere">⭐ Премьера</div>` : ''}
      </div>
      <h1 class="event-hero-title">${e.title}</h1>
      <div class="event-hero-date">${date.full} · ${e.time || '19:00'}</div>
    </div>
  </div>
</div>

<div class="event-main">
  <div class="event-content">
    <p class="section-label">О мероприятии</p>
    <p class="event-description">${e.description || ''}</p>
    ${e.description_full ? `<p class="event-text">${e.description_full}</p>` : ''}

    ${e.trailer_html ? `
    <div class="event-trailer">
      <p class="section-label">Трейлер</p>
      <div class="trailer-wrap">${e.trailer_html}</div>
    </div>` : ''}

    <ul class="event-details-list">
      <li><strong>Дата</strong>${date.full}</li>
      <li><strong>Время</strong>${e.time || '19:00'}</li>
      <li><strong>Место</strong>${e.location || 'Арт-пространство «Киммерия», ул. Игнатенко, 5, Ялта'}</li>
      ${e.age ? `<li><strong>Возраст</strong>${e.age}</li>` : ''}
    </ul>

  </div>

  <aside class="event-sidebar">
    <div class="sidebar-label">Когда</div>
    <div class="sidebar-value">${date.short}</div>
    <div class="sidebar-note">Начало в ${e.time || '19:00'} · ${date.day}</div>
    <hr class="sidebar-divider">
    <div class="sidebar-label">Где</div>
    <div class="sidebar-place">${e.location || 'Арт-пространство «Киммерия»'}<small>Ялта, Крым</small></div>
    <hr class="sidebar-divider">
    <div class="sidebar-label">Стоимость</div>
    <div class="sidebar-price-main">${e.price || 'По запросу'}</div>
    ${e.ticket_url && !isPast
      ? `<a href="${e.ticket_url}" class="btn-primary" target="_blank" rel="noopener">Купить билет</a>`
      : isPast
      ? `<div class="btn-past">Мероприятие завершено</div>`
      : `<button class="btn-register" onclick="openRegForm()">Записаться на мероприятие</button>`}
    <a href="/#events" class="btn-secondary">← Все события</a>
    <button class="btn-share" onclick="shareEvent(this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
      Поделиться
      <span class="share-popup">Ссылка скопирована!</span>
    </button>
    ${e.age ? `<div class="sidebar-age">${e.age}</div>` : ''}
  </aside>
</div>

<div class="back-section">
  <a href="/#events" class="back-link">← Все события</a>
</div>

<div id="site-footer"></div>

<div class="overlay" id="regOverlay" onclick="if(event.target===this)closeRegForm()">
  <div class="popup">
    <button class="popup-close" onclick="closeRegForm()">×</button>
    <div class="popup-title">Записаться на мероприятие</div>
    <p class="popup-sub">${e.title} · ${date.short}</p>
    <form class="reg-form" id="regForm" onsubmit="submitRegForm(event)">
      <input type="text" name="name" placeholder="Имя и фамилия" required maxlength="80">
      <input type="tel" name="phone" placeholder="Номер телефона" required maxlength="20">
      <label class="form-consent">
        <input type="checkbox" name="consent" required>
        <span>Согласен на <a href="/privacy/" target="_blank">обработку персональных данных</a></span>
      </label>
      <button type="submit" class="btn-submit" id="regSubmitBtn">Отправить заявку →</button>
      <div class="form-error" id="regFormError"></div>
    </form>
  </div>
</div>

<script>
var TG_TOKEN = '8555296982:AAE2LCN_eeCy33jGJfyWh7guxS2ia2yq68A';
var TG_CHAT  = '214662526';
var GS_URL   = 'https://script.google.com/macros/s/AKfycbz4rkLWsDP4Oz7C6FvOqMKoqqb9E3MJvP7iQUCvQ-M5AiFm2Ml5816rxXWmSiS4d49d/exec';

function openRegForm() {
  document.getElementById('regOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeRegForm() {
  document.getElementById('regOverlay').classList.remove('open');
  document.body.style.overflow = '';
}
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeRegForm(); });

function submitRegForm(e) {
  e.preventDefault();
  var form = document.getElementById('regForm');
  var btn  = document.getElementById('regSubmitBtn');
  var err  = document.getElementById('regFormError');
  var name  = form.name.value.trim();
  var phone = form.phone.value.trim();
  var digits = phone.replace(/\\D/g, '');
  if (!digits || digits.length < 10) {
    err.textContent = 'Введите корректный номер телефона';
    err.style.display = 'block';
    form.phone.focus();
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Отправляем…';
  err.style.display = 'none';

  var pageUrl = window.location.href;
  var text = '🎬 Новая заявка на кинопоказ\\n\\n'
           + '📽 ${e.title}\\n'
           + '📅 ${date.short} · ${e.time || '19:00'}\\n\\n'
           + '👤 ' + name + '\\n'
           + '📞 ' + phone + '\\n\\n'
           + '🔗 ' + pageUrl;

  var gsParams = new URLSearchParams({
    name: name, phone: phone,
    event: '${e.slug}',
    page: pageUrl
  });

  fetch(GS_URL + '?' + gsParams.toString(), { method: 'GET', mode: 'no-cors' }).catch(function(){});
  fetch('https://api.telegram.org/bot' + TG_TOKEN + '/sendMessage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: TG_CHAT, text: text })
  }).catch(function(){});

  window.location.href = '/spasibo/';
}

function shareEvent(btn) {
  var url = window.location.href;
  var popup = btn.querySelector('.share-popup');
  function show() { popup.classList.add('visible'); setTimeout(function(){ popup.classList.remove('visible'); }, 2000); }
  if (navigator.share) { navigator.share({ title: '${e.title} — Киммерия-Арт', url: url }).catch(function(){}); return; }
  if (navigator.clipboard) { navigator.clipboard.writeText(url).then(show).catch(fb); }
  function fb() { var t=document.createElement('textarea'); t.value=url; document.body.appendChild(t); t.select(); try{document.execCommand('copy');show();}catch(e){} document.body.removeChild(t); }
}
</script>
<script src="/footer.js"></script>
</body>
</html>`;
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'public, max-age=60, stale-while-revalidate=300');

  const { slug } = req.query;
  if (!slug) return res.status(400).send('slug required');

  try {
    const { rows: [e] } = await pool.query(
      `SELECT slug, title, description, description_short, description_full,
              date, time, date_label, format, location, price, image_url,
              custom_banner, ticket_url, age, trailer_html, is_premiere, status
       FROM events WHERE slug = $1 AND status = 'published'`, [slug]
    );

    if (!e) return res.status(404).send('<!DOCTYPE html><html><body><h1>404 — Мероприятие не найдено</h1><a href="/">На главную</a></body></html>');

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(renderPage(e));
  } catch (err) {
    console.error(err);
    return res.status(500).send('Server error');
  }
}
