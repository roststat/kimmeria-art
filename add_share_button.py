#!/usr/bin/env python3
"""Добавляет плавающую кнопку «Поделиться» перед </body> на нужных страницах."""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

SHARE_BLOCK = '''
<!-- FLOATING SHARE BUTTON -->
<style>
.fab-share {
  position: fixed;
  top: 50%;
  right: 24px;
  transform: translateY(-50%);
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  color: #1a4a3a;
  border: 1.5px solid #d0e8e0;
  border-radius: 100px;
  padding: 11px 20px 11px 16px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0,0,0,0.10);
  transition: box-shadow 0.15s, transform 0.15s;
}
.fab-share:hover { box-shadow: 0 6px 28px rgba(0,0,0,0.14); transform: translateY(calc(-50% - 1px)); }
.fab-share-toast {
  position: fixed;
  top: calc(50% - 56px);
  right: 24px;
  z-index: 201;
  background: #1a4a3a;
  color: #fff;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  padding: 10px 18px;
  border-radius: 100px;
  display: none;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
@media (max-width: 600px) {
  .fab-share { right: 16px; padding: 10px 14px; }
  .fab-share-label { display: none; }
  .fab-share-toast { right: 16px; }
}
</style>
<button class="fab-share" id="fabShare" onclick="fabShareClick()" title="Поделиться">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
  <span class="fab-share-label">Поделиться</span>
</button>
<div class="fab-share-toast" id="fabShareToast">Ссылка скопирована!</div>
<script>
function fabShareClick() {
  var url = window.location.href.split('?')[0];
  var titleEl = document.querySelector('h1, .page-title, .event-hero-title');
  var shareText = (titleEl ? titleEl.textContent.trim() : document.title) + ' — Киммерия-Арт';
  if (navigator.share) {
    navigator.share({ title: shareText, url: url }).catch(function(){});
  } else {
    navigator.clipboard.writeText(url).then(function() {
      var toast = document.getElementById('fabShareToast');
      toast.style.display = 'block';
      setTimeout(function() { toast.style.display = 'none'; }, 2500);
    }).catch(function() {
      var ta = document.createElement('textarea');
      ta.value = url; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
      var toast = document.getElementById('fabShareToast');
      toast.style.display = 'block';
      setTimeout(function() { toast.style.display = 'none'; }, 2500);
    });
  }
}
</script>
'''

# Страницы для добавления кнопки
TARGETS = []

# programmy/*
programmy_dir = os.path.join(ROOT, 'programmy')
for name in os.listdir(programmy_dir):
    path = os.path.join(programmy_dir, name, 'index.html')
    if os.path.isfile(path):
        TARGETS.append(path)

# Спецстраницы (не event-*, не admin, не служебные)
EXTRA_DIRS = [
    'master-mikrodrama',
    'master-mikrodrama-2',
    'idealnaya-sreda',
    'kinoklub',
    'vstrecha-denpolyarnika',
    'vstrecha-kvartirnyy',
    'vstrecha-sladkoe',
    'lecture-afrodita',
    'lecture-gekata',
    'lecture-lilit',
    'hotel-partner',
    'hotel-foros',
    # kurs-mikrodram уже имеет кнопку — пропускаем
]
for d in EXTRA_DIRS:
    path = os.path.join(ROOT, d, 'index.html')
    if os.path.isfile(path):
        TARGETS.append(path)

updated = 0
skipped = 0

for path in TARGETS:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'fabShareClick' in content or 'fab-share' in content:
        print(f'[skip] уже есть: {path}')
        skipped += 1
        continue

    if '</body>' not in content:
        print(f'[warn] нет </body>: {path}')
        continue

    new_content = content.replace('</body>', SHARE_BLOCK + '</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    rel = os.path.relpath(path, ROOT)
    print(f'[ok]   {rel}')
    updated += 1

print(f'\nГотово: обновлено {updated}, пропущено {skipped}')
