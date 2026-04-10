#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт добавления мероприятия на сайт Киммерия-Арт.

Использование:
  python add_event.py event.txt

event.txt — текстовый файл с описанием мероприятия (см. event_example.txt).
"""

import os
import re
import sys
import shutil
from datetime import datetime

SITE_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────
# Парсинг файла с данными мероприятия
# ──────────────────────────────────────────────

def parse_event_file(path):
    data = {}
    current_key = None
    current_lines = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            # Строка вида "КЛЮЧ: значение"
            m = re.match(r'^([A-ZА-ЯЁ_]+):\s*(.*)', line)
            if m:
                if current_key:
                    data[current_key] = "\n".join(current_lines).strip()
                current_key = m.group(1).strip()
                current_lines = [m.group(2).strip()] if m.group(2).strip() else []
            else:
                if current_key:
                    current_lines.append(line)

    if current_key:
        data[current_key] = "\n".join(current_lines).strip()

    return data


def validate(data):
    required = ["SLUG", "НАЗВАНИЕ", "ДАТА", "ВРЕМЯ", "ФОРМАТ", "ОПИСАНИЕ_КАРТОЧКИ",
                "ОПИСАНИЕ_СТРАНИЦЫ", "ОБЛОЖКА"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        print(f"[ERR] Не заполнены обязательные поля: {', '.join(missing)}")
        sys.exit(1)


# ──────────────────────────────────────────────
# Вспомогательные функции форматирования
# ──────────────────────────────────────────────

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}
WEEKDAYS_RU = {
    0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг",
    4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}

def format_date_ru(dt):
    """12 декабря 2024"""
    return f"{dt.day} {MONTHS_RU[dt.month]} {dt.year}"

def format_date_ru_short(dt):
    """12 декабря"""
    return f"{dt.day} {MONTHS_RU[dt.month]}"

def format_weekday(dt):
    return WEEKDAYS_RU[dt.weekday()]


# ──────────────────────────────────────────────
# Генерация HTML страницы мероприятия
# ──────────────────────────────────────────────

NEW_VENUE_DATE = datetime(2026, 4, 1)
NEW_VENUE      = "г. Ялта, ул. Игнатенко, 5"
OLD_VENUE      = "г. Ялта, ул. Кирова, 83б, 2 эт."
OLD_VENUE_CARD = "Ул. Кирова, 83б, Ялта"
NEW_VENUE_CARD = "Ул. Игнатенко, 5, Ялта"

def default_venue(dt, card=False):
    """Возвращает дефолтный адрес в зависимости от даты мероприятия."""
    if dt >= NEW_VENUE_DATE:
        return NEW_VENUE_CARD if card else NEW_VENUE
    return OLD_VENUE_CARD if card else OLD_VENUE


def build_details_list(data, dt):
    rows = []

    for key, label in [
        ("РЕЖИССЁР",   "Режиссёр"),
        ("СТРАНА_ГОД", "Страна / год"),
        ("В_РОЛЯХ",    "В ролях"),
        ("ВЕДЁТ",      "Ведёт"),
    ]:
        if data.get(key):
            rows.append(f'      <li><strong>{label}</strong> {data[key]}</li>')

    rows.append(f'      <li><strong>Дата</strong> {format_date_ru(dt)}, {format_weekday(dt).lower()} (завершено)</li>')
    rows.append(f'      <li><strong>Время</strong> {data["ВРЕМЯ"]}</li>')
    mesto = data.get("МЕСТО") or default_venue(dt)
    rows.append(f'      <li><strong>Место</strong> {mesto}</li>')

    if data.get("ВОЗРАСТ"):
        rows.append(f'      <li><strong>Возраст</strong> {data["ВОЗРАСТ"]}</li>')
    if data.get("ВКЛЮЧЕНО"):
        rows.append(f'      <li><strong>Включено</strong> {data["ВКЛЮЧЕНО"]}</li>')

    return "\n".join(rows)


def build_body_text(data):
    paragraphs = [p.strip() for p in data["ОПИСАНИЕ_СТРАНИЦЫ"].split("\n\n") if p.strip()]
    parts = []
    for p in paragraphs:
        # Переносы внутри абзаца → пробел
        p = " ".join(p.split("\n"))
        parts.append(f"      <p>{p}</p>")
    return "\n".join(parts)


def build_gallery_html(gallery_paths, slug, title):
    """gallery_paths — список web-путей (photos/...)"""
    if not gallery_paths:
        return ""
    imgs = "\n".join(
        f'        <img src="/{p}" alt="{title} фото {i+1}" onclick="openLightbox(this.src)" loading="lazy">'
        for i, p in enumerate(gallery_paths)
    )
    return f"""
    <div class="event-gallery">
      <h2 class="event-gallery-title">Фотоотчёт</h2>
      <div class="gallery-grid-2">
{imgs}
      </div>
    </div>"""


def build_event_page(data, dt, cover_web_path, gallery_paths=None):
    slug = data["SLUG"]
    title = data["НАЗВАНИЕ"]
    format_ = data["ФОРМАТ"]
    age = data.get("ВОЗРАСТ", "")
    tag_text = f"{format_} · {age}" if age else format_
    price_main = data.get("ЦЕНА_ОСНОВНАЯ", "650 ₽")
    price_member = data.get("ЦЕНА_ЧЛЕНЫ", "500 ₽ членам клуба")
    og_desc = data.get("OG_ОПИСАНИЕ", data["ОПИСАНИЕ_КАРТОЧКИ"])

    date_str = format_date_ru(dt)
    weekday = format_weekday(dt)
    details = build_details_list(data, dt)
    body_text = build_body_text(data)
    gallery_html = build_gallery_html(gallery_paths or [], slug, title)

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — {format_} — Киммерия Арт</title>
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Киммерия-Арт">
  <meta property="og:url" content="https://art-kimmeria.ru/{slug}/">
  <meta property="og:title" content="{title} — {format_}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:image" content="https://art-kimmeria.ru/{cover_web_path}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} — {format_}">
  <meta name="twitter:description" content="{og_desc}">
  <meta name="twitter:image" content="https://art-kimmeria.ru/{cover_web_path}">
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
    .nav-links {{ display: flex; gap: 4px; list-style: none; }}
    .nav-links a {{ font-size: 13px; font-weight: 500; color: #111111; text-decoration: none; padding: 6px 12px; border-radius: 100px; transition: background 0.15s; }}
    .nav-links a:hover {{ background: #f5f5f5; }}
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
    .lightbox img {{ max-width: 92vw; max-height: 92vh; object-fit: contain; border-radius: 4px; box-shadow: 0 32px 80px rgba(0,0,0,0.6); cursor: default; }}
    .lightbox-close {{ position: absolute; top: 20px; right: 24px; font-size: 32px; color: #ffffff; cursor: pointer; line-height: 1; opacity: 0.7; transition: opacity 0.15s; background: none; border: none; padding: 0; }}
    .lightbox-close:hover {{ opacity: 1; }}
    .event-past-banner {{ background: #111111; color: #ffffff; text-align: center; padding: 12px 48px; font-size: 12px; font-weight: 600; letter-spacing: 0.06em; }}
    .event-main {{ display: grid; grid-template-columns: 1fr 360px; gap: 48px; max-width: 1200px; margin: 0 auto; padding: 60px 48px; align-items: start; }}
    .event-section-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666666; font-weight: 600; margin-bottom: 12px; }}
    .event-description {{ font-size: 20px; font-weight: 500; line-height: 1.6; color: #111111; margin-bottom: 32px; max-width: 620px; }}
    .event-details-list {{ list-style: none; margin-bottom: 40px; }}
    .event-details-list li {{ font-size: 16px; color: #666666; padding: 12px 0; border-bottom: 1px solid #e8e8e8; display: flex; gap: 16px; align-items: baseline; }}
    .event-details-list li strong {{ color: #111111; font-weight: 600; min-width: 90px; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }}
    .event-body-text {{ font-size: 15px; color: #444444; line-height: 1.8; max-width: 580px; margin-bottom: 40px; }}
    .event-body-text p {{ margin-bottom: 16px; }}
    .event-gallery {{ margin-bottom: 40px; max-width: 620px; }}
    .event-gallery-title {{ font-size: 20px; font-weight: 600; color: #111111; margin-bottom: 16px; }}
    .gallery-grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }}
    .gallery-grid-2 img {{ width: 100%; aspect-ratio: 4/3; object-fit: cover; display: block; border-radius: 8px; cursor: zoom-in; }}
    .event-sidebar {{ position: sticky; top: 80px; background: #ffffff; border: 1px solid #e8e8e8; border-radius: 16px; padding: 32px; }}
    .sidebar-date-block {{ margin-bottom: 24px; border-bottom: 1px solid #e8e8e8; padding-bottom: 24px; }}
    .sidebar-date-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666666; font-weight: 600; margin-bottom: 6px; }}
    .sidebar-date {{ font-size: 24px; font-weight: 700; line-height: 1.3; color: #111111; }}
    .sidebar-time {{ font-size: 16px; color: #666666; margin-top: 6px; }}
    .sidebar-place-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666666; font-weight: 600; margin-bottom: 4px; margin-top: 20px; }}
    .sidebar-place {{ font-size: 16px; color: #111111; line-height: 1.5; }}
    .sidebar-price-block {{ margin-top: 24px; border-top: 1px solid #e8e8e8; padding-top: 24px; margin-bottom: 24px; }}
    .sidebar-price-label {{ font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #666666; font-weight: 600; margin-bottom: 12px; }}
    .sidebar-price-main {{ font-size: 36px; font-weight: 700; color: #111111; line-height: 1; margin-bottom: 6px; }}
    .sidebar-price-member {{ font-size: 13px; color: #666666; font-weight: 500; }}
    .btn-past {{ display: block; width: 100%; padding: 14px 24px; text-align: center; background: #f5f5f5; color: #666666; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; border: 1px solid #e8e8e8; border-radius: 100px; cursor: default; }}
    .btn-secondary {{ display: block; width: 100%; padding: 14px 24px; text-align: center; background: #ffffff; color: #111111; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; text-decoration: none; border: 1px solid #e8e8e8; border-radius: 100px; transition: background 0.15s; margin-top: 10px; }}
    .btn-secondary:hover {{ background: #f5f5f5; }}
    .event-back-section {{ padding: 0 48px 60px; }}
    .event-back-link {{ font-size: 13px; font-weight: 600; color: #111111; text-decoration: none; padding: 8px 16px; border-radius: 100px; border: 1px solid #e8e8e8; display: inline-block; transition: background 0.15s; }}
    .event-back-link:hover {{ background: #f5f5f5; }}
    .btn-share {{ display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px 24px; background: #ffffff; color: #111111; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; border: 1px solid #e8e8e8; border-radius: 100px; cursor: pointer; transition: background 0.15s; margin-top: 10px; position: relative; }}
    .btn-share:hover {{ background: #f5f5f5; }}
    .btn-share svg {{ width: 15px; height: 15px; flex-shrink: 0; }}
    .share-popup {{ position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%) translateY(4px); background: #111111; color: #ffffff; font-size: 12px; font-weight: 500; padding: 6px 14px; border-radius: 100px; white-space: nowrap; pointer-events: none; opacity: 0; transition: all 0.2s; }}
    .share-popup.visible {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
    footer {{ background: #111111; padding: 40px 48px; display: flex; justify-content: space-between; align-items: center; }}
    .footer-logo {{ font-size: 17px; font-weight: 700; color: #ffffff; letter-spacing: -0.01em; }}
    .footer-links {{ display: flex; gap: 20px; }}
    .footer-links a {{ font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.15s; }}
    .footer-links a:hover {{ color: #ffffff; }}
    .footer-copy {{ font-size: 12px; color: rgba(255,255,255,0.3); }}
    @media (max-width: 900px) {{
      nav {{ padding: 0 20px; }} .nav-links {{ display: none; }}
      .event-hero-inner {{ grid-template-columns: 1fr; gap: 24px; padding: 32px 20px; }}
      .event-hero-poster {{ max-width: 220px; max-height: 300px; margin: 0 auto; }}
      .event-hero-text {{ text-align: center; }}
      .event-hero-title {{ font-size: 28px; }} .event-past-banner {{ padding: 12px 20px; }}
      .event-main {{ grid-template-columns: 1fr; padding: 36px 20px; gap: 32px; }}
      .event-sidebar {{ position: static; }}
      footer {{ padding: 28px 20px; flex-direction: column; gap: 16px; text-align: center; }}
      .footer-links {{ flex-wrap: wrap; justify-content: center; }}
      .event-back-section {{ padding: 0 20px 40px; }}
    }}
    @media (max-width: 600px) {{
      nav {{ padding: 0 16px; }}
      .event-hero-poster {{ max-width: 160px; }}
      .event-hero-title {{ font-size: 22px; }}
      .event-hero-inner {{ padding: 24px 16px; }}
      .event-main {{ padding: 24px 16px; }} .event-sidebar {{ padding: 24px; }}
      .event-back-section {{ padding: 0 16px 32px; }} footer {{ padding: 24px 16px; }}
    }}
    .nav-burger {{
      display: none; flex-direction: column; justify-content: center; gap: 5px;
      width: 40px; height: 40px; background: none; border: none; cursor: pointer;
      padding: 8px; border-radius: 8px; transition: background 0.15s;
    }}
    .nav-burger:hover {{ background: #f5f5f5; }}
    .nav-burger span {{ display: block; width: 22px; height: 2px; background: #111111; border-radius: 2px; transition: all 0.25s; }}
    .nav-burger.open span:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
    .nav-burger.open span:nth-child(2) {{ opacity: 0; }}
    .nav-burger.open span:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}
    .mobile-menu {{
      display: none; position: fixed; top: 60px; left: 0; right: 0; bottom: 0;
      background: #ffffff; z-index: 99; padding: 24px 20px;
      flex-direction: column; gap: 4px; overflow-y: auto;
    }}
    .mobile-menu.open {{ display: flex; }}
    .mobile-menu a {{ font-size: 20px; font-weight: 600; color: #111111; text-decoration: none; padding: 14px 16px; border-radius: 12px; transition: background 0.15s; }}
    .mobile-menu a:hover {{ background: #f5f5f5; }}
    .mobile-menu-divider {{ height: 1px; background: #e8e8e8; margin: 8px 0; }}
    @media (max-width: 900px) {{
      .nav-links {{ display: none; }}
      .nav-back {{ display: none; }}
      .nav-burger {{ display: flex; }}
    }}
  </style>
</head>
<body>

<nav>
  <a href="/" class="nav-logo">Киммерия-Арт</a>
  <ul class="nav-links"></ul>
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
  <div class="event-hero-bg" style="background-image: url('/{cover_web_path}');"></div>
  <div class="event-hero-inner">
    <div class="event-hero-poster">
      <img src="/{cover_web_path}" alt="{title} — {format_}" onclick="openLightbox(this.src)">
    </div>
    <div class="event-hero-text">
      <div class="event-hero-tag">{tag_text}</div>
      <h1 class="event-hero-title">{title}</h1>
      <div class="event-hero-date">{date_str} · {weekday} · {data["ВРЕМЯ"]}</div>
    </div>
  </div>
</div>

<div class="event-past-banner">Мероприятие завершено</div>

<div class="event-main">
  <div class="event-content">
    <p class="event-section-label">О {format_.lower()} и показе</p>
    <div class="event-description">
      {data["ОПИСАНИЕ_КАРТОЧКИ"]}
    </div>

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
      <div class="sidebar-time">Начало в {data["ВРЕМЯ"]}</div>
      <div class="sidebar-place-label">Где</div>
      <div class="sidebar-place">{data.get("МЕСТО") or default_venue(dt)}</div>
    </div>
    <div class="sidebar-price-block">
      <div class="sidebar-price-label">Стоимость была</div>
      <div class="sidebar-price-main">{price_main}</div>
      <div class="sidebar-price-member">{price_member}</div>
    </div>
    <div class="btn-past">Мероприятие завершено</div>
    <a href="/#events" class="btn-secondary">← Все события</a>
    <button class="btn-share" onclick="shareEvent(this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
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
function openLightbox(src) {{
  document.getElementById('lightboxImg').src = src;
  document.getElementById('lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeLightbox() {{
  document.getElementById('lightbox').classList.remove('open');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeLightbox(); }});
function shareEvent(btn) {{
  var url = window.location.href;
  var titleEl = document.querySelector('.event-hero-title');
  var title = (titleEl ? titleEl.textContent.trim() : document.title) + ' — Киммерия-Арт';
  var popup = btn.querySelector('.share-popup');
  if (navigator.share) {{ navigator.share({{ title: title, url: url }}).catch(function(){{}}); return; }}
  function showPopup() {{ popup.classList.add('visible'); setTimeout(function() {{ popup.classList.remove('visible'); }}, 2000); }}
  function fallback() {{
    var ta = document.createElement('textarea');
    ta.value = url; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
    showPopup();
  }}
  if (navigator.clipboard) {{ navigator.clipboard.writeText(url).then(showPopup).catch(fallback); }}
  else {{ fallback(); }}
}}
function toggleMenu() {{
  var burger = document.getElementById('navBurger');
  var menu = document.getElementById('mobileMenu');
  burger.classList.toggle('open');
  menu.classList.toggle('open');
  document.body.style.overflow = menu.classList.contains('open') ? 'hidden' : '';
}}
function closeMenu() {{
  document.getElementById('navBurger').classList.remove('open');
  document.getElementById('mobileMenu').classList.remove('open');
  document.body.style.overflow = '';
}}
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────
# Вставка карточки в index.html
# ──────────────────────────────────────────────

SVG_PLACEHOLDER = '<div style="width:100%;height:100%;background:#1a1a1a;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:48px;height:64px;opacity:0.25"><rect width="60" height="80" rx="4" fill="#888"/><path d="M18 30 L42 42 L18 54 Z" fill="#fff"/></svg></div>'

def build_index_card(data, dt, cover_web_path, has_cover):
    slug = data["SLUG"]
    title = data["НАЗВАНИЕ"]
    format_ = data["ФОРМАТ"]
    date_iso = dt.strftime("%Y-%m-%d")
    date_ru = format_date_ru(dt)
    desc = data["ОПИСАНИЕ_КАРТОЧКИ"]
    # Первое предложение для карточки (если длинное — обрезаем)
    card_desc = desc if len(desc) <= 120 else desc[:120].rsplit(" ", 1)[0] + "…"

    if has_cover:
        photo_html = f'<img src="{cover_web_path}" alt="{title}">'
    else:
        photo_html = SVG_PLACEHOLDER

    return f"""
    <!-- {title} -->
    <div class="event-card past hidden" data-tab="past" data-format="{format_.lower()}" data-date="{date_iso}" onclick="location.href='/{slug}/'">
      <div class="event-photo-wrap">
        {photo_html}
        <span class="event-badge">{format_}</span>
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
          <span class="event-location">{data.get("МЕСТО") or default_venue(dt, card=True)}</span>
          <div>
            <div class="event-price" style="opacity:0.5">{data.get("ЦЕНА_ОСНОВНАЯ", "650")} / {data.get("ЦЕНА_ЧЛЕНЫ_КОРОТКАЯ", "500")} ₽</div>
            <span class="event-past-tag">Завершено</span>
          </div>
        </div>
      </div>
    </div>
"""


def insert_index_card(card_html, dt):
    index_path = os.path.join(SITE_DIR, "index.html")
    with open(index_path, encoding="utf-8") as f:
        content = f.read()

    # Ищем все карточки прошедших событий и вставляем по дате (новые выше)
    # Маркер конца блока прошедших событий
    end_marker = "  </div>\n</section>"

    # Найдём место вставки: первая карточка с датой <= нашей
    pattern = r'data-date="(\d{4}-\d{2}-\d{2})"'
    date_str = dt.strftime("%Y-%m-%d")

    # Найдём первую карточку past с датой меньше или равной нашей
    insert_before = None
    for m in re.finditer(r'(    <!-- .+? -->)\n    <div class="event-card past', content):
        # Найдём дату этой карточки
        snippet = content[m.start():m.start()+200]
        dm = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', snippet)
        if dm and dm.group(1) <= date_str:
            insert_before = m.start()
            break

    if insert_before is not None:
        content = content[:insert_before] + card_html + content[insert_before:]
    else:
        # Вставляем перед закрывающим тегом
        content = content.replace(end_marker, card_html + end_marker, 1)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] Карточка добавлена в index.html")


# ──────────────────────────────────────────────
# Вставка строки в архив киноклуба
# ──────────────────────────────────────────────

def build_archive_item(data, dt, cover_web_path, has_cover):
    slug = data["SLUG"]
    title = data["НАЗВАНИЕ"]
    date_ru = format_date_ru(dt)
    desc = data["ОПИСАНИЕ_КАРТОЧКИ"]
    archive_desc = desc if len(desc) <= 100 else desc[:100].rsplit(" ", 1)[0] + "…"

    if has_cover:
        thumb = f'<div class="archive-thumb"><img src="/{cover_web_path}" alt="{title}" loading="lazy"></div>'
    else:
        thumb = '<div class="archive-thumb archive-thumb--placeholder"><svg viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:40px;height:53px;opacity:0.3"><rect width="60" height="80" rx="4" fill="#888"/><path d="M18 30 L42 42 L18 54 Z" fill="#fff"/></svg></div>'

    return f"""
        <li><a href="/{slug}/" class="archive-item">
          {thumb}
          <div class="archive-body">
            <div class="archive-date">{date_ru}</div>
            <div class="archive-title">{title}</div>
            <div class="archive-desc">{archive_desc}</div>
          </div>
        </a></li>
"""


def insert_archive_item(item_html, dt):
    kinoklub_path = os.path.join(SITE_DIR, "kinoklub", "index.html")
    with open(kinoklub_path, encoding="utf-8") as f:
        content = f.read()

    date_str = dt.strftime("%Y-%m-%d")

    # Найдём первый archive-item с датой меньше или равной нашей
    # Даты в архиве хранятся как текст, конвертируем через поиск
    insert_before = None

    # Ищем archive-date теги
    for m in re.finditer(r'(<li><a href="[^"]*" class="archive-item">)', content):
        # Ищем дату в следующих 300 символах
        snippet = content[m.start():m.start()+400]
        dm = re.search(r'<div class="archive-date">(\d+) ([а-яё]+) (\d+)</div>', snippet)
        if dm:
            day, month_ru, year = int(dm.group(1)), dm.group(2), int(dm.group(3))
            month_num = next((k for k, v in MONTHS_RU.items() if v == month_ru), 0)
            try:
                item_dt = datetime(year, month_num, day)
                if item_dt <= dt:
                    insert_before = m.start()
                    break
            except Exception:
                pass

    end_marker = "      </ul>\n    </div>"

    if insert_before is not None:
        content = content[:insert_before] + item_html + content[insert_before:]
    else:
        content = content.replace(end_marker, item_html + end_marker, 1)

    with open(kinoklub_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] Запись добавлена в архив киноклуба")


# ──────────────────────────────────────────────
# Главная функция
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Использование: python add_event.py event.txt")
        sys.exit(1)

    event_file = sys.argv[1]
    if not os.path.exists(event_file):
        print(f"[ERR] Файл не найден: {event_file}")
        sys.exit(1)

    data = parse_event_file(event_file)
    validate(data)

    slug = data["SLUG"]
    dt = datetime.strptime(data["ДАТА"], "%Y-%m-%d")

    # Обложка — ищем в нескольких местах:
    # 1) абсолютный путь как есть
    # 2) рядом с txt-файлом
    # 3) рядом с папкой сайта (на случай если txt лежит в сайте, а обложка — рядом в исходниках)
    cover_src = data["ОБЛОЖКА"].strip()
    if not os.path.isabs(cover_src):
        txt_dir = os.path.dirname(os.path.abspath(event_file))
        candidates = [
            os.path.join(txt_dir, cover_src),
            os.path.join(SITE_DIR, cover_src),
        ]
        cover_src = next((p for p in candidates if os.path.exists(p)), candidates[0])

    has_cover = os.path.exists(cover_src)
    if not has_cover:
        print(f"[!!]  Обложка не найдена: {cover_src} — будет заглушка")
        cover_web_path = ""
    else:
        ext = os.path.splitext(cover_src)[1]
        cover_filename = f"{slug}-cover{ext}"
        cover_dest = os.path.join(SITE_DIR, "photos", cover_filename)
        shutil.copy2(cover_src, cover_dest)
        cover_web_path = f"photos/{cover_filename}"
        print(f"[OK] Обложка скопирована: {cover_web_path}")

    # Фотографии с мероприятия (все jpg/png в папке, кроме обложки)
    # ПАПКА_ФОТО задаётся явно, иначе — папка рядом с txt (или папка обложки если она в другом месте)
    if data.get("ПАПКА_ФОТО"):
        foto_dir = data["ПАПКА_ФОТО"].strip()
        if not os.path.isabs(foto_dir):
            foto_dir = os.path.join(os.path.dirname(os.path.abspath(event_file)), foto_dir)
    else:
        # Если обложка лежит не рядом с txt — берём папку обложки
        txt_dir = os.path.dirname(os.path.abspath(event_file))
        cover_dir = os.path.dirname(cover_src) if has_cover else txt_dir
        foto_dir = cover_dir if cover_dir != SITE_DIR else txt_dir
    event_folder = foto_dir
    cover_basename = os.path.basename(cover_src).lower()
    img_exts = {".jpg", ".jpeg", ".png", ".webp"}
    gallery_paths = []
    for fname in sorted(os.listdir(event_folder)):
        if fname.lower() == cover_basename:
            continue
        if os.path.splitext(fname)[1].lower() in img_exts:
            dest_name = f"{slug}-photo-{len(gallery_paths)+1}{os.path.splitext(fname)[1]}"
            dest_path = os.path.join(SITE_DIR, "photos", dest_name)
            shutil.copy2(os.path.join(event_folder, fname), dest_path)
            gallery_paths.append(f"photos/{dest_name}")
    if gallery_paths:
        print(f"[OK] Фотографий с мероприятия: {len(gallery_paths)}")

    # Создать папку страницы
    event_dir = os.path.join(SITE_DIR, slug)
    os.makedirs(event_dir, exist_ok=True)

    # Сгенерировать страницу
    page_html = build_event_page(data, dt, cover_web_path, gallery_paths)
    page_path = os.path.join(event_dir, "index.html")
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"[OK] Страница создана: {slug}/index.html")

    # Карточка на главную
    card_html = build_index_card(data, dt, cover_web_path, has_cover)
    insert_index_card(card_html, dt)

    # Архив киноклуба (только если формат — кинопоказ или документальный)
    fmt = data["ФОРМАТ"].lower()
    if any(w in fmt for w in ["кинопоказ", "документальн", "кино"]):
        item_html = build_archive_item(data, dt, cover_web_path, has_cover)
        insert_archive_item(item_html, dt)
    else:
        print(f"[i]  Формат «{data['ФОРМАТ']}» — в архив киноклуба не добавляю")

    print(f"\n[>] Готово! Мероприятие «{data['НАЗВАНИЕ']}» добавлено.")
    print(f"   Страница: /{slug}/")
    print(f"\nЧтобы опубликовать, запусти:")
    print(f"   cd \"{SITE_DIR}\" && git add -A && git commit -m \"Add {slug}\" && git push")


if __name__ == "__main__":
    main()
