# -*- coding: utf-8 -*-
import os, sys

BASE = r'D:\Загрузки Д\Киммерия-Арт\programmy'

# Блок "Афиша Киммерия-Арт" в admin-workspace
BUTTON_HTML = '''              <div class="admin-section admin-section-afisha">
                <div class="admin-section-top">
                  <div class="admin-section-title">Афиша Киммерия-Арт</div>
                </div>
                <div class="admin-field-group">
                  <label class="field-label">Кастомный баннер</label>
                  <div id="bannerPreviewWrap" style="margin-bottom:8px;display:none;">
                    <img id="bannerPreview" src="" style="width:100%;border-radius:8px;display:block;margin-bottom:6px;">
                    <button onclick="resetBanner()" style="font-size:11px;color:#c00;background:none;border:none;cursor:pointer;padding:0;">✕ Сбросить баннер</button>
                  </div>
                  <label style="display:flex;align-items:center;gap:8px;padding:10px 12px;border:1.5px dashed #d0d0d0;border-radius:8px;cursor:pointer;font-size:13px;color:#666;transition:border-color 0.15s;" onmouseover="this.style.borderColor=\'#1a4a3a\'" onmouseout="this.style.borderColor=\'#d0d0d0\'">
                    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px;flex-shrink:0;"><rect x="1" y="3" width="14" height="10" rx="2"/><circle cx="5.5" cy="7" r="1.5"/><path d="M1 11l4-4 3 3 2-2 4 4"/></svg>
                    <span id="bannerUploadLabel">Загрузить баннер (JPG/PNG)</span>
                    <input type="file" id="bannerFile" accept="image/*" style="display:none;" onchange="uploadBanner(this)">
                  </label>
                  <div id="bannerUploadResult" style="font-size:11px;color:#888;margin-top:6px;min-height:14px;"></div>
                </div>
                <div class="admin-field-group">
                  <label class="field-label">Дата показа</label>
                  <input class="editable-field" type="date" id="afisha-date" style="min-height:unset;resize:none;">
                </div>
                <div class="admin-field-group">
                  <label class="field-label">Время</label>
                  <input class="editable-field" type="time" id="afisha-time" value="19:00" style="min-height:unset;resize:none;">
                </div>
                <div class="admin-field-group">
                  <label class="field-label">Цена для покупателя</label>
                  <input class="editable-field" id="afisha-price" placeholder="800 ₽" style="min-height:unset;resize:none;">
                </div>
                <div class="admin-actions">
                  <button class="admin-btn-pdf admin-btn-afisha" id="afishaBtn" onclick="addToAfisha()">
                    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><line x1="8" y1="5" x2="8" y2="11"/><line x1="5" y1="8" x2="11" y2="8"/></svg>
                    Добавить в афишу
                  </button>
                  <button class="admin-btn-pdf" id="afishaRemoveBtn" onclick="removeFromAfisha()" style="background:#fff;color:#c00;border:1.5px solid #ffd0d0;margin-top:8px;display:none;">
                    Снять с афиши
                  </button>
                  <div id="afishaResult" style="font-size:12px;color:#888;margin-top:8px;text-align:center;min-height:16px;"></div>
                </div>
              </div>
'''

JS_FUNCTION = r"""
// ── АФИША КИММЕРИЯ-АРТ ──────────────────────────────────────────────────────

var _afishaSlug = (typeof PAGE_URL !== 'undefined')
  ? PAGE_URL.replace(/.*\/programmy\//, '').replace(/\/$/, '')
  : location.pathname.replace(/.*\/programmy\//, '').replace(/\/$/, '');

var _customBannerUrl = null;
var _CLOUDINARY_UPLOAD = 'https://api.cloudinary.com/v1_1/dmzsczjzd/image/upload';
var _CLOUDINARY_PRESET = 'kimmeria_unsigned';

// Загружаем актуальное состояние из БД при открытии админки
(function() {
  var origShow = window.showAdminWorkspace;
  window.showAdminWorkspace = function() {
    if (origShow) origShow();
    _syncProgramMeta();
    _loadAfishaState();
  };
})();

function _syncProgramMeta() {
  var title   = (document.querySelector('.page-title') || {}).textContent || '';
  var desc    = (document.querySelector('.page-subtitle') || {}).textContent || '';
  var bodyEl  = document.querySelector('.body-text');
  var descFull= bodyEl ? bodyEl.textContent.trim().slice(0,300) : '';
  var imgEl   = document.querySelector('.poster-img');
  var imgUrl  = imgEl ? imgEl.src : '';
  var eyebrow = (document.querySelector('.page-eyebrow') || {}).textContent || '';
  var format  = eyebrow.toLowerCase().includes('лекц') ? 'лекция'
              : eyebrow.toLowerCase().includes('спект') ? 'спектакль'
              : eyebrow.toLowerCase().includes('кино') ? 'кинопоказ'
              : eyebrow.toLowerCase().includes('дегуст') ? 'дегустация'
              : eyebrow.toLowerCase().includes('мастер') ? 'мастер-класс'
              : 'мероприятие';
  var ageMatch = eyebrow.match(/\d+\+/);
  var age = ageMatch ? ageMatch[0] : null;
  var priceEl = document.querySelector('.spec-value-price');
  var price = priceEl ? priceEl.textContent.trim() : '';

  fetch('/api/afisha?id=' + _afishaSlug + '&action=sync', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'x-admin-password': ADMIN_PASSWORD },
    body: JSON.stringify({
      title: title.trim(),
      description: descFull,
      description_short: desc.trim(),
      image_url: imgUrl,
      format: format,
      age: age,
      price: price,
    }),
  }).catch(function(){});
}

function _loadAfishaState() {
  fetch('/api/afisha?id=' + _afishaSlug)
    .then(function(r){ return r.json(); })
    .then(function(data) {
      if (!data) return;
      if (data.custom_banner) {
        _customBannerUrl = data.custom_banner;
        _showBannerPreview(data.custom_banner);
      }
      if (data.status === 'published') {
        var removeBtn = document.getElementById('afishaRemoveBtn');
        if (removeBtn) removeBtn.style.display = 'block';
        if (data.date && data.date !== '1970-01-01') {
          var d = document.getElementById('afisha-date');
          if (d) d.value = data.date.slice(0,10);
        }
        if (data.time) {
          var t = document.getElementById('afisha-time');
          if (t) t.value = data.time;
        }
        if (data.price) {
          var p = document.getElementById('afisha-price');
          if (p) p.value = data.price;
        }
      }
    }).catch(function(){});
}

function uploadBanner(input) {
  var file = input.files[0];
  if (!file) return;
  var result = document.getElementById('bannerUploadResult');
  var label  = document.getElementById('bannerUploadLabel');
  result.textContent = 'Загружаю...';
  result.style.color = '#888';

  var fd = new FormData();
  fd.append('file', file);
  fd.append('upload_preset', _CLOUDINARY_PRESET);
  fd.append('folder', 'kimmeria/banners');

  fetch(_CLOUDINARY_UPLOAD, { method: 'POST', body: fd })
    .then(function(r){ return r.json(); })
    .then(function(data) {
      if (!data.secure_url) throw new Error(data.error && data.error.message || 'Upload failed');
      _customBannerUrl = data.secure_url;
      _showBannerPreview(data.secure_url);
      result.textContent = 'Загружено!';
      result.style.color = '#1a4a3a';
      // Сохраняем баннер в БД сразу
      fetch('/api/afisha?id=' + _afishaSlug + '&action=banner', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': ADMIN_PASSWORD },
        body: JSON.stringify({ custom_banner: data.secure_url }),
      }).catch(function(){});
      // Обновляем poster-img на странице
      var posterEl = document.querySelector('.poster-img');
      if (posterEl) posterEl.src = data.secure_url;
      label.textContent = file.name;
    })
    .catch(function(e) {
      result.textContent = 'Ошибка: ' + e.message;
      result.style.color = '#c00';
    });
}

function _showBannerPreview(url) {
  var wrap = document.getElementById('bannerPreviewWrap');
  var img  = document.getElementById('bannerPreview');
  if (wrap && img) { img.src = url; wrap.style.display = 'block'; }
}

function resetBanner() {
  _customBannerUrl = null;
  var wrap = document.getElementById('bannerPreviewWrap');
  if (wrap) wrap.style.display = 'none';
  document.getElementById('bannerUploadResult').textContent = '';
  document.getElementById('bannerUploadLabel').textContent = 'Загрузить баннер (JPG/PNG)';
  fetch('/api/afisha?id=' + _afishaSlug + '&action=banner', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'x-admin-password': ADMIN_PASSWORD },
    body: JSON.stringify({ custom_banner: null }),
  }).catch(function(){});
}

function addToAfisha() {
  var date  = document.getElementById('afisha-date').value;
  var time  = document.getElementById('afisha-time').value || '19:00';
  var price = document.getElementById('afisha-price').value.trim() || 'По запросу';
  var result = document.getElementById('afishaResult');

  if (!date) { result.textContent = 'Укажите дату'; result.style.color='#c00'; return; }

  var btn = document.getElementById('afishaBtn');
  btn.disabled = true;
  btn.textContent = 'Добавляю...';
  result.textContent = '';

  var d = new Date(date);
  var months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
  var dateLabel = d.getDate() + ' ' + months[d.getMonth()] + ' · ' + time;

  var title   = (document.querySelector('.page-title') || {}).textContent || '';
  var desc    = (document.querySelector('.page-subtitle') || document.querySelector('.body-text') || {}).textContent || '';
  var eyebrow = (document.querySelector('.page-eyebrow') || {}).textContent || '';
  var imgEl   = document.querySelector('.poster-img');
  var imgUrl  = imgEl ? imgEl.src : '';
  var format  = eyebrow.toLowerCase().includes('лекц') ? 'лекция'
              : eyebrow.toLowerCase().includes('спект') ? 'спектакль'
              : eyebrow.toLowerCase().includes('кино') ? 'кинопоказ'
              : eyebrow.toLowerCase().includes('дегуст') ? 'дегустация'
              : eyebrow.toLowerCase().includes('мастер') ? 'мастер-класс'
              : 'мероприятие';

  fetch('/api/afisha', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-admin-password': ADMIN_PASSWORD },
    body: JSON.stringify({
      slug: _afishaSlug,
      title: title.trim(),
      description: desc.trim().slice(0, 200),
      date: date,
      time: time,
      date_label: dateLabel,
      format: format,
      price: price,
      image_url: imgUrl,
      custom_banner: _customBannerUrl,
    }),
  })
  .then(function(r){ return r.json(); })
  .then(function(data) {
    if (data.ok) {
      result.textContent = 'Добавлено на главную';
      result.style.color = '#1a4a3a';
      var removeBtn = document.getElementById('afishaRemoveBtn');
      if (removeBtn) removeBtn.style.display = 'block';
    } else {
      result.textContent = 'Ошибка: ' + (data.error || 'неизвестная');
      result.style.color = '#c00';
    }
    btn.disabled = false;
    btn.innerHTML = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><line x1="8" y1="5" x2="8" y2="11"/><line x1="5" y1="8" x2="11" y2="8"/></svg> Добавить в афишу';
  })
  .catch(function() {
    result.textContent = 'Ошибка соединения';
    result.style.color = '#c00';
    btn.disabled = false;
  });
}

function removeFromAfisha() {
  if (!confirm('Снять программу с главной афиши?')) return;
  fetch('/api/afisha?id=' + _afishaSlug, {
    method: 'DELETE',
    headers: { 'x-admin-password': ADMIN_PASSWORD },
  }).then(function() {
    document.getElementById('afishaResult').textContent = 'Снято с афиши';
    document.getElementById('afishaResult').style.color = '#888';
    var removeBtn = document.getElementById('afishaRemoveBtn');
    if (removeBtn) removeBtn.style.display = 'none';
  }).catch(function(){});
}
"""

def patch_file(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    changed = False

    # Если уже есть новая версия — пропускаем
    if 'uploadBanner' in html:
        print('  уже актуально, пропускаю')
        return False

    # Удаляем старый блок афиши если есть
    if 'admin-section-afisha' in html:
        import re
        html = re.sub(
            r'<div class="admin-section admin-section-afisha">.*?</div>\s*\n',
            '', html, flags=re.DOTALL
        )
        changed = True

    # Удаляем старую JS функцию addToAfisha если есть
    if 'function addToAfisha' in html:
        import re
        html = re.sub(
            r'\nfunction addToAfisha\(\).*?(?=\n(?:function|\}\);|</script>))',
            '', html, flags=re.DOTALL
        )
        changed = True

    # Вставляем новый блок перед первым <div class="admin-actions">
    marker = '<div class="admin-actions">'
    idx = html.find(marker)
    if idx == -1:
        print('  [!] admin-actions не найден')
        return False
    html = html[:idx] + BUTTON_HTML + html[idx:]

    # Вставляем JS перед последним </script>
    last_script = html.rfind('</script>')
    if last_script == -1:
        print('  [!] </script> не найден')
        return False
    html = html[:last_script] + JS_FUNCTION + html[last_script:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


ok = 0
for slug in sorted(os.listdir(BASE)):
    page = os.path.join(BASE, slug, 'index.html')
    if not os.path.isfile(page):
        continue
    print(f'[{slug}]', end=' ', flush=True)
    if patch_file(page):
        print('OK')
        ok += 1
    else:
        print('пропущено')

print(f'\nГотово: {ok} файлов обновлено')
