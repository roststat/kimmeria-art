#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор HTML-страниц мероприятий из _events/*.md
Запускается автоматически GitHub Actions при каждом коммите в _events/
"""

import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENTS_DIR = os.path.join(SITE_DIR, "_events")

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}
WEEKDAYS_RU = {
    0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг",
    4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}

# ──────────────────────────────────────────────
# Парсинг Markdown frontmatter
# ──────────────────────────────────────────────

def parse_md(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Разделяем frontmatter и тело
    m = re.match(r'^---\n(.*?)\n---\n?(.*)', content, re.DOTALL)
    if not m:
        print(f"[WARN] Нет frontmatter в {path}")
        return {}, ""

    frontmatter = m.group(1)
    body = m.group(2).strip()

    data = {}
    current_key = None
    current_lines = []
    in_list = False

    for line in frontmatter.split("\n"):
        # Список (gallery)
        if line.startswith("  - "):
            if current_key:
                if current_key not in data:
                    data[current_key] = []
                data[current_key].append(line[4:].strip().strip('"'))
            continue

        kv = re.match(r'^(\w+):\s*(.*)', line)
        if kv:
            if current_key and current_key not in data:
                data[current_key] = "\n".join(current_lines).strip()
            current_key = kv.group(1)
            val = kv.group(2).strip().strip('"')
            if val:
                data[current_key] = val
            else:
                current_lines = []
        else:
            if current_key and isinstance(data.get(current_key), str):
                current_lines.append(line)

    return data, body


# ──────────────────────────────────────────────
# Форматирование дат
# ──────────────────────────────────────────────

def parse_date(date_str):
    from datetime import datetime
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except Exception:
            pass
    raise ValueError(f"Не могу распарсить дату: {date_str}")

def format_date_ru(dt):
    return f"{dt.day} {MONTHS_RU[dt.month]} {dt.year}"

def format_weekday(dt):
    return WEEKDAYS_RU[dt.weekday()]


# ──────────────────────────────────────────────
# Генерация HTML страницы
# ──────────────────────────────────────────────

def build_details(data, dt):
    rows = []
    for key, label in [("director", "Режиссёр"), ("country_year", "Страна / год"), ("cast", "В ролях"), ("host", "Ведёт")]:
        if data.get(key):
            rows.append(f'      <li><strong>{label}</strong> {data[key]}</li>')
    rows.append(f'      <li><strong>Дата</strong> {format_date_ru(dt)}, {format_weekday(dt).lower()} (завершено)</li>')
    rows.append(f'      <li><strong>Время</strong> {data.get("time", "19:00")}</li>')
    rows.append(f'      <li><strong>Место</strong> г. Ялта, ул. Кирова, 83б, 2 эт.</li>')
    if data.get("age"):
        rows.append(f'      <li><strong>Возраст</strong> {data["age"]}</li>')
    return "\n".join(rows)


def build_body_text(body):
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    return "\n".join(f"      <p>{' '.join(p.split())}</p>" for p in paragraphs)


def build_gallery(gallery, title):
    if not gallery:
        return ""
    imgs = "\n".join(
        f'        <img src="{p}" alt="{title} фото {i+1}" onclick="openLightbox(this.src)" loading="lazy">'
        for i, p in enumerate(gallery)
    )
    return f"""
    <div class="event-gallery">
      <h2 class="event-gallery-title">Фотоотчёт</h2>
      <div class="gallery-grid-2">
{imgs}
      </div>
    </div>"""


def build_page(data, body, dt):
    slug = data.get("slug", "")
    title = data.get("title", "")
    fmt = data.get("format", "Мероприятие")
    age = data.get("age", "")
    tag = f"{fmt} · {age}" if age else fmt
    cover = data.get("cover", "")
    price_main = data.get("price_main", "650 ₽")
    price_member = data.get("price_member", "500 ₽ членам клуба")
    og_desc = data.get("description_card", "")
    gallery = data.get("gallery", [])
    if isinstance(gallery, str):
        gallery = [gallery]

    date_str = format_date_ru(dt)
    weekday = format_weekday(dt)
    details = build_details(data, dt)
    body_text = build_body_text(body if body else data.get("description_full", ""))
    gallery_html = build_gallery(gallery, title)

    cover_bg = f"url('{cover}')" if cover else "none"
    cover_img = f'<img src="{cover}" alt="{title}" onclick="openLightbox(this.src)">' if cover else ""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — {fmt} — Киммерия Арт</title>
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Киммерия-Арт">
  <meta property="og:url" content="https://art-kimmeria.ru/{slug}/">
  <meta property="og:title" content="{title} — {fmt}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:image" content="https://art-kimmeria.ru{cover}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} — {fmt}">
  <meta name="twitter:description" content="{og_desc}">
  <meta name="twitter:image" content="https://art-kimmeria.ru{cover}">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'Inter', sans-serif; background: #ffffff; color: #111111; font-size: 16px; line-height: 1.6; overflow-x: hidden; }}
    nav {{ position: fixed; top: 0; left: 0; right: 0; z-index: 100; height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-bottom: 1px solid #e8e8e8; }}
    .nav-logo {{ font-size: 17px; font-weight: 700; color: #111111; text-decoration: none; letter-spacing: 0.06em; text-transform: uppercase; }}
    .nav-back {{ font-size: 13px; font-weight: 600; color: #111111; text-decoration: none; padding: 8px 16px; border-radius: 100px; border: 1px solid #e8e8e8; transition: background 0.15s; }}
    .nav-back:hover {{ background: #f5f5f5; }}
    .event-hero {{ padding-top: 60px; position: relative; overflow: hidden; background: #0d0d0d; }}
    .event-hero-bg {{ position: absolute; inset: -40px; background-size: cover; background-position: center; filter: blur(28px); opacity: 0.55; transform: scale(1.08); }}
    .event-hero-inner {{ position: relative; z-index: 1; display: grid; grid-template-columns: auto 1fr; gap: 48px; align-items: center; max-width: 1200px; margin: 0 auto; padding: 48px; }}
    .event-hero-poster {{ flex-shrink: 0; max-height: 480px; max-width: 340px; display: flex; align-items: center; }}
    .event-hero-poster img {{ display: block; width: 100%; height: auto; object-fit: contain; border-radius: 8px; box-shadow: 0 24px 64px rgba(0,0,0,0.6); cursor: zoom-in; }}
    .event-hero-text {{ color: #ffffff; }}
    .event-hero-tag {{ display: inline-block; background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.25); color: #ffffff; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 5px 12px; border-radius: 100px; margin-bottom: 14px; }}
    .event-hero-title {{ font-size: 44px; font-weight: 700; color: #ffffff; line-height: 1.1; margin-bottom: 12px; }}
    .event-hero-date {{ font-size: 15px; font-weight: 500; color: rgba(255,255,255,0.75); }}
    .lightbox {{ display: none; position: fixed; inset: 0; z-index: 1000; background: rgba(0,0,0,0.92); align-items: center; justify-content: center; cursor: zoom-out; }}
    .lightbox.open {{ display: flex; }}
    .lightbox img {{ max-width: 92vw; max-height: 92vh; object-fit: contain; border-radius: 4px; cursor: default; }}
    .lightbox-close {{ position: absolute; top: 20px; right: 24px; font-size: 32px; color: #fff; cursor: pointer; background: none; border: none; opacity: 0.7; }}
    .lightbox-close:hover {{ opacity: 1; }}
    .event-past-banner {{ background: #111111; color: #ffffff; text-align: center; padding: 12px 48px; font-size: 12px; font-weight: 600; letter-spacing: 0.06em; }}
    .event-main {{ display: grid; grid-template-columns: 1fr 360px; gap: 48px; max-width: 1200px; margin: 0 auto; padding: 60px 48px; align-items: start; }}
    .event-section-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666; font-weight: 600; margin-bottom: 12px; }}
    .event-description {{ font-size: 20px; font-weight: 500; line-height: 1.6; color: #111; margin-bottom: 32px; max-width: 620px; }}
    .event-details-list {{ list-style: none; margin-bottom: 40px; }}
    .event-details-list li {{ font-size: 16px; color: #666; padding: 12px 0; border-bottom: 1px solid #e8e8e8; display: flex; gap: 16px; align-items: baseline; }}
    .event-details-list li strong {{ color: #111; font-weight: 600; min-width: 90px; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }}
    .event-body-text {{ font-size: 15px; color: #444; line-height: 1.8; max-width: 580px; margin-bottom: 40px; }}
    .event-body-text p {{ margin-bottom: 16px; }}
    .event-gallery {{ margin-bottom: 40px; max-width: 620px; }}
    .event-gallery-title {{ font-size: 20px; font-weight: 600; color: #111; margin-bottom: 16px; }}
    .gallery-grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }}
    .gallery-grid-2 img {{ width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: 8px; cursor: zoom-in; }}
    .event-sidebar {{ position: sticky; top: 80px; background: #fff; border: 1px solid #e8e8e8; border-radius: 16px; padding: 32px; }}
    .sidebar-date-block {{ margin-bottom: 24px; border-bottom: 1px solid #e8e8e8; padding-bottom: 24px; }}
    .sidebar-date-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666; font-weight: 600; margin-bottom: 6px; }}
    .sidebar-date {{ font-size: 24px; font-weight: 700; line-height: 1.3; color: #111; }}
    .sidebar-time {{ font-size: 16px; color: #666; margin-top: 6px; }}
    .sidebar-place-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666; font-weight: 600; margin-bottom: 4px; margin-top: 20px; }}
    .sidebar-place {{ font-size: 16px; color: #111; line-height: 1.5; }}
    .sidebar-price-block {{ margin-top: 24px; border-top: 1px solid #e8e8e8; padding-top: 24px; margin-bottom: 24px; }}
    .sidebar-price-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666; font-weight: 600; margin-bottom: 12px; }}
    .sidebar-price-main {{ font-size: 36px; font-weight: 700; color: #111; line-height: 1; margin-bottom: 6px; }}
    .sidebar-price-member {{ font-size: 13px; color: #666; font-weight: 500; }}
    .btn-past {{ display: block; width: 100%; padding: 14px 24px; text-align: center; background: #f5f5f5; color: #666; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; border: 1px solid #e8e8e8; border-radius: 100px; cursor: default; }}
    .btn-secondary {{ display: block; width: 100%; padding: 14px 24px; text-align: center; background: #fff; color: #111; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; text-decoration: none; border: 1px solid #e8e8e8; border-radius: 100px; transition: background 0.15s; margin-top: 10px; }}
    .btn-secondary:hover {{ background: #f5f5f5; }}
    .btn-share {{ display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px 24px; background: #fff; color: #111; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; border: 1px solid #e8e8e8; border-radius: 100px; cursor: pointer; transition: background 0.15s; margin-top: 10px; position: relative; }}
    .btn-share:hover {{ background: #f5f5f5; }}
    .share-popup {{ position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%) translateY(4px); background: #111; color: #fff; font-size: 12px; padding: 6px 14px; border-radius: 100px; white-space: nowrap; pointer-events: none; opacity: 0; transition: all 0.2s; }}
    .share-popup.visible {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
    .event-back-section {{ padding: 0 48px 60px; }}
    .event-back-link {{ font-size: 13px; font-weight: 600; color: #111; text-decoration: none; padding: 8px 16px; border-radius: 100px; border: 1px solid #e8e8e8; display: inline-block; transition: background 0.15s; }}
    .event-back-link:hover {{ background: #f5f5f5; }}
    footer {{ background: #111; padding: 40px 48px; display: flex; justify-content: space-between; align-items: center; }}
    .footer-logo {{ font-size: 17px; font-weight: 700; color: #fff; }}
    .footer-links {{ display: flex; gap: 20px; }}
    .footer-links a {{ font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.15s; }}
    .footer-links a:hover {{ color: #fff; }}
    .footer-copy {{ font-size: 12px; color: rgba(255,255,255,0.3); }}
    .nav-burger {{ display: none; flex-direction: column; justify-content: center; gap: 5px; width: 40px; height: 40px; background: none; border: none; cursor: pointer; padding: 8px; border-radius: 8px; }}
    .nav-burger span {{ display: block; width: 22px; height: 2px; background: #111; border-radius: 2px; transition: all 0.25s; }}
    .nav-burger.open span:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
    .nav-burger.open span:nth-child(2) {{ opacity: 0; }}
    .nav-burger.open span:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}
    .mobile-menu {{ display: none; position: fixed; top: 60px; left: 0; right: 0; bottom: 0; background: #fff; z-index: 99; padding: 24px 20px; flex-direction: column; gap: 4px; overflow-y: auto; }}
    .mobile-menu.open {{ display: flex; }}
    .mobile-menu a {{ font-size: 20px; font-weight: 600; color: #111; text-decoration: none; padding: 14px 16px; border-radius: 12px; transition: background 0.15s; }}
    .mobile-menu a:hover {{ background: #f5f5f5; }}
    .mobile-menu-divider {{ height: 1px; background: #e8e8e8; margin: 8px 0; }}
    @media (max-width: 900px) {{
      nav {{ padding: 0 20px; }} .nav-back {{ display: none; }} .nav-burger {{ display: flex; }}
      .event-hero-inner {{ grid-template-columns: 1fr; gap: 24px; padding: 32px 20px; }}
      .event-hero-poster {{ max-width: 220px; margin: 0 auto; }}
      .event-hero-text {{ text-align: center; }}
      .event-hero-title {{ font-size: 28px; }}
      .event-main {{ grid-template-columns: 1fr; padding: 36px 20px; gap: 32px; }}
      .event-sidebar {{ position: static; }}
      footer {{ padding: 28px 20px; flex-direction: column; gap: 16px; text-align: center; }}
      .footer-links {{ flex-wrap: wrap; justify-content: center; }}
      .event-back-section {{ padding: 0 20px 40px; }}
      .gallery-grid-2 {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 600px) {{
      nav {{ padding: 0 16px; }}
      .event-hero-poster {{ max-width: 160px; }}
      .event-hero-title {{ font-size: 22px; }}
      .event-hero-inner {{ padding: 24px 16px; }}
      .event-main {{ padding: 24px 16px; }} .event-sidebar {{ padding: 24px; }}
      .event-back-section {{ padding: 0 16px 32px; }} footer {{ padding: 24px 16px; }}
    }}
  </style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">Киммерия-Арт</a>
  <button class="nav-burger" id="navBurger" onclick="toggleMenu()" aria-label="Меню">
    <span></span><span></span><span></span>
  </button>
  <a href="/#events" class="nav-back">← Все события</a>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <a href="/" onclick="closeMenu()">Главная</a>
  <a href="/kinoklub/" onclick="closeMenu()">Киноклуб</a>
  <div class="mobile-menu-divider"></div>
  <a href="/#events" onclick="closeMenu()">← Все события</a>
</div>
<div class="event-hero">
  <div class="event-hero-bg" style="background-image: {cover_bg};"></div>
  <div class="event-hero-inner">
    <div class="event-hero-poster">{cover_img}</div>
    <div class="event-hero-text">
      <div class="event-hero-tag">{tag}</div>
      <h1 class="event-hero-title">{title}</h1>
      <div class="event-hero-date">{date_str} · {weekday} · {data.get("time", "19:00")}</div>
    </div>
  </div>
</div>
<div class="event-past-banner">Мероприятие завершено</div>
<div class="event-main">
  <div class="event-content">
    <p class="event-section-label">О мероприятии</p>
    <div class="event-description">{data.get("description_card", "")}</div>
    <ul class="event-details-list">
{details}
    </ul>
    <div class="event-body-text">
{body_text}
    </div>
{gallery_html}
  </div>
  <div class="event-sidebar">
    <div class="sidebar-date-block">
      <div class="sidebar-date-label">Когда</div>
      <div class="sidebar-date">{date_str}<br>{weekday}</div>
      <div class="sidebar-time">Начало в {data.get("time", "19:00")}</div>
      <div class="sidebar-place-label">Где</div>
      <div class="sidebar-place">г. Ялта<br>ул. Кирова, 83б, 2 эт.</div>
    </div>
    <div class="sidebar-price-block">
      <div class="sidebar-price-label">Стоимость была</div>
      <div class="sidebar-price-main">{price_main}</div>
      <div class="sidebar-price-member">{price_member}</div>
    </div>
    <div class="btn-past">Мероприятие завершено</div>
    <a href="/#events" class="btn-secondary">← Все события</a>
    <button class="btn-share" onclick="shareEvent(this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:15px;height:15px"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
      Поделиться
      <span class="share-popup">Ссылка скопирована!</span>
    </button>
  </div>
</div>
<div class="event-back-section">
  <a href="/#events" class="event-back-link">← Все события</a>
</div>
<footer>
  <div class="footer-logo">Киммерия-Арт</div>
  <div class="footer-links">
    <a href="https://vk.com/kimmeria_art" target="_blank">ВКонтакте</a>
    <a href="https://t.me/kimmeria_art" target="_blank">Telegram</a>
    <a href="/kinoklub/">Киноклуб</a>
    <a href="/#join">О клубе</a>
  </div>
  <div class="footer-copy">© 2025 Киммерия-Арт · Ялта</div>
</footer>
<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <button class="lightbox-close" onclick="closeLightbox()">&#x2715;</button>
  <img id="lightboxImg" src="" alt="" onclick="event.stopPropagation()">
</div>
<script>
function openLightbox(src) {{ document.getElementById('lightboxImg').src = src; document.getElementById('lightbox').classList.add('open'); document.body.style.overflow = 'hidden'; }}
function closeLightbox() {{ document.getElementById('lightbox').classList.remove('open'); document.body.style.overflow = ''; }}
document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeLightbox(); }});
function shareEvent(btn) {{
  var url = window.location.href;
  var popup = btn.querySelector('.share-popup');
  if (navigator.share) {{ navigator.share({{ title: '{title}', url: url }}).catch(function(){{}}); return; }}
  function showPopup() {{ popup.classList.add('visible'); setTimeout(function() {{ popup.classList.remove('visible'); }}, 2000); }}
  if (navigator.clipboard) {{ navigator.clipboard.writeText(url).then(showPopup).catch(function() {{ showPopup(); }}); }}
  else {{ showPopup(); }}
}}
function toggleMenu() {{ var b = document.getElementById('navBurger'), m = document.getElementById('mobileMenu'); b.classList.toggle('open'); m.classList.toggle('open'); document.body.style.overflow = m.classList.contains('open') ? 'hidden' : ''; }}
function closeMenu() {{ document.getElementById('navBurger').classList.remove('open'); document.getElementById('mobileMenu').classList.remove('open'); document.body.style.overflow = ''; }}
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────
# Вставка карточки в index.html
# ──────────────────────────────────────────────

SVG_PLACEHOLDER = '<div style="width:100%;height:100%;background:#1a1a1a;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:48px;height:64px;opacity:0.25"><rect width="60" height="80" rx="4" fill="#888"/><path d="M18 30 L42 42 L18 54 Z" fill="#fff"/></svg></div>'

def build_index_card(data, dt, slug):
    fmt = data.get("format", "Мероприятие")
    title = data.get("title", "")
    cover = data.get("cover", "")
    date_iso = dt.strftime("%Y-%m-%d")
    date_ru = format_date_ru(dt)
    desc = data.get("description_card", "")
    card_desc = desc if len(desc) <= 120 else desc[:120].rsplit(" ", 1)[0] + "…"
    price_main = data.get("price_main", "650")
    price_short = re.sub(r"[^\d]", "", price_main) or "650"
    price_member = data.get("price_member", "500 ₽ членам клуба")
    price_member_short = re.sub(r"[^\d]", "", price_member.split()[0]) or "500"

    photo_html = f'<img src="{cover}" alt="{title}">' if cover else SVG_PLACEHOLDER

    return f"""
    <!-- {title} -->
    <div class="event-card past hidden" data-tab="past" data-format="{fmt.lower()}" data-date="{date_iso}" onclick="location.href='/{slug}/'">
      <div class="event-photo-wrap">
        {photo_html}
        <span class="event-badge">{fmt}</span>
        <button class="event-share-btn" onclick="shareCard(event,this)" title="Поделиться">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          <span class="event-share-toast">Скопировано</span>
        </button>
      </div>
      <div class="event-body">
        <div class="event-date-line">{date_ru}</div>
        <h3 class="event-title">{title}</h3>
        <p class="event-desc">{card_desc}</p>
        <div class="event-bottom">
          <span class="event-location">Ул. Кирова, 83б, Ялта</span>
          <div>
            <div class="event-price" style="opacity:0.5">{price_short} / {price_member_short} ₽</div>
            <span class="event-past-tag">Завершено</span>
          </div>
        </div>
      </div>
    </div>
"""

def insert_index_card(card_html, dt, slug):
    index_path = os.path.join(SITE_DIR, "index.html")
    with open(index_path, encoding="utf-8") as f:
        content = f.read()

    # Пропускаем если карточка уже есть
    if f"location.href='/{slug}/'" in content:
        print(f"  Карточка уже есть в index.html, пропускаю")
        return

    date_str = dt.strftime("%Y-%m-%d")
    end_marker = "  </div>\n</section>"
    insert_before = None

    for m in re.finditer(r'    <!-- .+? -->\n    <div class="event-card past', content):
        snippet = content[m.start():m.start()+200]
        dm = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', snippet)
        if dm and dm.group(1) <= date_str:
            insert_before = m.start()
            break

    if insert_before is not None:
        content = content[:insert_before] + card_html + content[insert_before:]
    else:
        content = content.replace(end_marker, card_html + end_marker, 1)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Карточка добавлена в index.html")


# ──────────────────────────────────────────────
# Вставка в архив киноклуба
# ──────────────────────────────────────────────

def insert_archive_item(data, dt, slug):
    kinoklub_path = os.path.join(SITE_DIR, "kinoklub", "index.html")
    with open(kinoklub_path, encoding="utf-8") as f:
        content = f.read()

    if f'href="/{slug}/"' in content:
        print(f"  Запись уже есть в киноклубе, пропускаю")
        return

    title = data.get("title", "")
    cover = data.get("cover", "")
    desc = data.get("description_card", "")
    archive_desc = desc if len(desc) <= 100 else desc[:100].rsplit(" ", 1)[0] + "…"
    date_ru = format_date_ru(dt)

    thumb = f'<div class="archive-thumb"><img src="{cover}" alt="{title}" loading="lazy"></div>' if cover else \
            '<div class="archive-thumb archive-thumb--placeholder"><svg viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:40px;height:53px;opacity:0.3"><rect width="60" height="80" rx="4" fill="#888"/><path d="M18 30 L42 42 L18 54 Z" fill="#fff"/></svg></div>'

    item_html = f"""
        <li><a href="/{slug}/" class="archive-item">
          {thumb}
          <div class="archive-body">
            <div class="archive-date">{date_ru}</div>
            <div class="archive-title">{title}</div>
            <div class="archive-desc">{archive_desc}</div>
          </div>
        </a></li>
"""
    end_marker = "      </ul>\n    </div>"
    insert_before = None

    for m in re.finditer(r'(<li><a href="[^"]*" class="archive-item">)', content):
        snippet = content[m.start():m.start()+400]
        dm = re.search(r'<div class="archive-date">(\d+) ([а-яё]+) (\d+)</div>', snippet)
        if dm:
            day, month_ru, year = int(dm.group(1)), dm.group(2), int(dm.group(3))
            month_num = next((k for k, v in MONTHS_RU.items() if v == month_ru), 0)
            try:
                from datetime import datetime
                item_dt = datetime(year, month_num, day)
                if item_dt <= dt:
                    insert_before = m.start()
                    break
            except Exception:
                pass

    if insert_before is not None:
        content = content[:insert_before] + item_html + content[insert_before:]
    else:
        content = content.replace(end_marker, item_html + end_marker, 1)

    with open(kinoklub_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Запись добавлена в архив киноклуба")


# ──────────────────────────────────────────────
# Главная функция
# ──────────────────────────────────────────────

def main():
    if not os.path.exists(EVENTS_DIR):
        print("Папка _events/ не найдена, выходим")
        return

    md_files = [f for f in os.listdir(EVENTS_DIR) if f.endswith(".md")]
    if not md_files:
        print("Нет файлов в _events/")
        return

    for fname in sorted(md_files):
        path = os.path.join(EVENTS_DIR, fname)
        print(f"\nОбрабатываю: {fname}")

        data, body = parse_md(path)
        if not data.get("slug") or not data.get("title") or not data.get("date"):
            print(f"  [SKIP] Нет slug/title/date")
            continue

        slug = data["slug"]
        dt = parse_date(data["date"])

        # Создать папку и страницу
        event_dir = os.path.join(SITE_DIR, slug)
        page_path = os.path.join(event_dir, "index.html")
        os.makedirs(event_dir, exist_ok=True)

        page_html = build_page(data, body, dt)
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"  Страница: /{slug}/index.html")

        # Карточка на главную
        card_html = build_index_card(data, dt, slug)
        insert_index_card(card_html, dt, slug)

        # Архив киноклуба
        fmt = data.get("format", "").lower()
        add_to_kinoklub = str(data.get("add_to_kinoklub", "false")).lower() in ("true", "yes", "1")
        if add_to_kinoklub or any(w in fmt for w in ["кинопоказ", "документальн"]):
            insert_archive_item(data, dt, slug)

    print("\nГотово!")

if __name__ == "__main__":
    main()
