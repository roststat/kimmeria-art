# -*- coding: utf-8 -*-
import os, re, sys

BASE = r'D:\Загрузки Д\Киммерия-Арт\programmy'

BUTTON_HTML = '''              <div class="admin-section admin-section-afisha">
                <div class="admin-section-top">
                  <div class="admin-section-title">Афиша Киммерия-Арт</div>
                </div>
                <div class="admin-field-group">
                  <label class="field-label">Кастомный баннер</label>
                  <div id="bannerPreviewWrap" style="margin-bottom:8px;display:none;">
                    <img id="bannerPreview" src="" style="width:100%;border-radius:8px;display:block;margin-bottom:6px;">
                    <button onclick="window.resetBanner()" style="font-size:11px;color:#c00;background:none;border:none;cursor:pointer;padding:0;">&#x2715; Сбросить баннер</button>
                  </div>
                  <label style="display:flex;align-items:center;gap:8px;padding:10px 12px;border:1.5px dashed #d0d0d0;border-radius:8px;cursor:pointer;font-size:13px;color:#666;transition:border-color 0.15s;" onmouseover="this.style.borderColor=\'#1a4a3a\'" onmouseout="this.style.borderColor=\'#d0d0d0\'">
                    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px;flex-shrink:0;"><rect x="1" y="3" width="14" height="10" rx="2"/><circle cx="5.5" cy="7" r="1.5"/><path d="M1 11l4-4 3 3 2-2 4 4"/></svg>
                    <span id="bannerUploadLabel">Загрузить баннер (JPG/PNG)</span>
                    <input type="file" id="bannerFile" accept="image/*" style="display:none;" onchange="window.uploadBanner(this)">
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
                  <button class="admin-btn-pdf admin-btn-afisha" id="afishaBtn" onclick="window.addToAfisha()">
                    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><line x1="8" y1="5" x2="8" y2="11"/><line x1="5" y1="8" x2="11" y2="8"/></svg>
                    Добавить в афишу
                  </button>
                  <button class="admin-btn-pdf" id="afishaRemoveBtn" onclick="window.removeFromAfisha()" style="background:#fff;color:#c00;border:1.5px solid #ffd0d0;margin-top:8px;display:none;">
                    Снять с афиши
                  </button>
                  <div id="afishaResult" style="font-size:12px;color:#888;margin-top:8px;text-align:center;min-height:16px;"></div>
                </div>
              </div>
'''

JS_BLOCK = r"""<script>
(function() {
  var _slug = (typeof PAGE_URL !== 'undefined')
    ? PAGE_URL.replace(/.*\/programmy\//, '').replace(/\/$/, '')
    : location.pathname.replace(/\/programmy\//, '').replace(/\/$/, '').replace(/\//g,'');
  var _banner = null;
  var _CL_URL    = 'https://api.cloudinary.com/v1_1/dmzsczjzd/image/upload';
  var _CL_PRESET = 'kimmeria_unsigned';
  var _PASS = (typeof ADMIN_PASSWORD !== 'undefined') ? ADMIN_PASSWORD : 'kimmeria';

  function _api(method, params, body) {
    var qs = Object.keys(params||{}).map(function(k){ return k+'='+params[k]; }).join('&');
    return fetch('/api/afisha' + (qs ? '?'+qs : ''), {
      method: method,
      headers: Object.assign({'x-admin-password': _PASS}, body ? {'Content-Type':'application/json'} : {}),
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  function _showPreview(url) {
    var wrap = document.getElementById('bannerPreviewWrap');
    var img  = document.getElementById('bannerPreview');
    if (wrap && img) { img.src = url; wrap.style.display = 'block'; }
  }

  // Перехватываем showAdminWorkspace — после загрузки страницы
  window.addEventListener('load', function() {
    var orig = window.showAdminWorkspace;
    window.showAdminWorkspace = function() {
      if (orig) orig();
      // Синхронизируем мета
      var title   = (document.querySelector('.page-title')||{}).textContent||'';
      var desc    = (document.querySelector('.page-subtitle')||{}).textContent||'';
      var bodyEl  = document.querySelector('.body-text');
      var imgEl   = document.querySelector('.poster-img');
      var eyebrow = (document.querySelector('.page-eyebrow')||{}).textContent||'';
      var fmt = eyebrow.toLowerCase().includes('лекц') ? 'лекция'
              : eyebrow.toLowerCase().includes('спект') ? 'спектакль'
              : eyebrow.toLowerCase().includes('кино') ? 'кинопоказ'
              : eyebrow.toLowerCase().includes('дегуст') ? 'дегустация'
              : eyebrow.toLowerCase().includes('мастер') ? 'мастер-класс' : 'мероприятие';
      var age = (eyebrow.match(/\d+\+/)||[])[0] || null;
      _api('PATCH', {id:_slug}, {
        title: title.trim(), description: bodyEl ? bodyEl.textContent.trim().slice(0,300) : '',
        description_short: desc.trim(), image_url: imgEl ? imgEl.src : '',
        format: fmt, age: age, price: '',
      }).catch(function(){});
      // Загружаем состояние
      _api('GET', {id:_slug}).then(function(r){ return r.json(); }).then(function(d) {
        if (!d) return;
        if (d.custom_banner) { _banner = d.custom_banner; _showPreview(d.custom_banner); }
        if (d.status === 'published') {
          var rb = document.getElementById('afishaRemoveBtn');
          if (rb) rb.style.display = 'block';
          if (d.date && d.date !== '1970-01-01') {
            var el = document.getElementById('afisha-date');
            if (el) el.value = d.date.slice(0,10);
          }
          if (d.time) { var el2 = document.getElementById('afisha-time'); if (el2) el2.value = d.time; }
          if (d.price) { var el3 = document.getElementById('afisha-price'); if (el3) el3.value = d.price; }
        }
      }).catch(function(){});
    };
  });

  window.uploadBanner = function(input) {
    var file = input.files[0]; if (!file) return;
    var res = document.getElementById('bannerUploadResult');
    res.textContent = 'Загружаю...'; res.style.color = '#888';
    var fd = new FormData();
    fd.append('file', file); fd.append('upload_preset', _CL_PRESET); fd.append('folder', 'kimmeria');
    fetch(_CL_URL, {method:'POST', body:fd})
      .then(function(r){ return r.json(); })
      .then(function(d) {
        if (!d.secure_url) throw new Error((d.error&&d.error.message)||'Upload failed');
        _banner = d.secure_url;
        _showPreview(d.secure_url);
        res.textContent = 'Загружено!'; res.style.color = '#1a4a3a';
        document.getElementById('bannerUploadLabel').textContent = file.name;
        var p = document.querySelector('.poster-img'); if (p) p.src = d.secure_url;
        _api('PATCH', {id:_slug, action:'banner'}, {custom_banner: d.secure_url}).catch(function(){});
      }).catch(function(e){ res.textContent = 'Ошибка: '+e.message; res.style.color='#c00'; });
  };

  window.resetBanner = function() {
    _banner = null;
    var w = document.getElementById('bannerPreviewWrap'); if (w) w.style.display='none';
    document.getElementById('bannerUploadResult').textContent = '';
    document.getElementById('bannerUploadLabel').textContent = 'Загрузить баннер (JPG/PNG)';
    _api('PATCH', {id:_slug, action:'banner'}, {custom_banner: null}).catch(function(){});
  };

  window.addToAfisha = function() {
    var section = document.querySelector('.admin-section-afisha');
    var date  = section ? section.querySelector('#afisha-date').value : document.getElementById('afisha-date').value;
    var time  = section ? section.querySelector('#afisha-time').value : (document.getElementById('afisha-time').value || '19:00');
    var price = section ? section.querySelector('#afisha-price').value.trim() : document.getElementById('afisha-price').value.trim();
    if (!time) time = '19:00';
    if (!price) price = 'По запросу';
    var res   = document.getElementById('afishaResult');
    if (!date) { res.textContent='Укажите дату'; res.style.color='#c00'; return; }
    var btn = document.getElementById('afishaBtn');
    btn.disabled = true; btn.textContent = 'Добавляю...'; res.textContent = '';
    var d = new Date(date);
    var M = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
    var dateLabel = d.getDate()+' '+M[d.getMonth()]+' · '+time;
    var title   = (document.querySelector('.page-title')||{}).textContent||'';
    var desc    = (document.querySelector('.page-subtitle')||document.querySelector('.body-text')||{}).textContent||'';
    var eyebrow = (document.querySelector('.page-eyebrow')||{}).textContent||'';
    var imgEl   = document.querySelector('.poster-img');
    var fmt = eyebrow.toLowerCase().includes('лекц') ? 'лекция'
            : eyebrow.toLowerCase().includes('спект') ? 'спектакль'
            : eyebrow.toLowerCase().includes('кино') ? 'кинопоказ'
            : eyebrow.toLowerCase().includes('дегуст') ? 'дегустация'
            : eyebrow.toLowerCase().includes('мастер') ? 'мастер-класс' : 'мероприятие';
    _api('POST', {}, {
      slug: _slug, title: title.trim(), description: desc.trim().slice(0,200),
      date: date, time: time, date_label: dateLabel, format: fmt, price: price,
      image_url: imgEl ? imgEl.src : '', custom_banner: _banner,
    }).then(function(r){ return r.json(); }).then(function(d) {
      if (d.ok) {
        res.textContent='Добавлено на главную'; res.style.color='#1a4a3a';
        var rb = document.getElementById('afishaRemoveBtn'); if (rb) rb.style.display='block';
      } else { res.textContent='Ошибка: '+(d.error||'неизвестная'); res.style.color='#c00'; }
      btn.disabled=false;
      btn.innerHTML='<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><line x1="8" y1="5" x2="8" y2="11"/><line x1="5" y1="8" x2="11" y2="8"/></svg> Добавить в афишу';
    }).catch(function(){ res.textContent='Ошибка соединения'; res.style.color='#c00'; btn.disabled=false; });
  };

  window.removeFromAfisha = function() {
    if (!confirm('Снять программу с главной афиши?')) return;
    _api('DELETE', {id:_slug}).then(function() {
      var res = document.getElementById('afishaResult');
      res.textContent='Снято с афиши'; res.style.color='#888';
      var rb = document.getElementById('afishaRemoveBtn'); if (rb) rb.style.display='none';
    }).catch(function(){});
  };
})();
</script>
"""

def clean_and_patch(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    # Удаляем ВСЕ старые блоки афиши из HTML
    html = re.sub(
        r'\s*<div class="admin-section admin-section-afisha">.*?</div>\s*\n',
        '\n', html, flags=re.DOTALL
    )

    # Удаляем старые JS функции афиши (все варианты)
    html = re.sub(
        r'\n(?:window\.)?(?:uploadBanner|resetBanner|addToAfisha|removeFromAfisha|_syncProgramMeta|_loadAfishaState|_showBannerPreview)\s*=?\s*function[^{]*\{.*?(?=\n(?:window\.|function |\}\);|var |</script>))',
        '', html, flags=re.DOTALL
    )

    # Удаляем старый IIFE блок афиши если есть
    html = re.sub(
        r'\n// ── АФИША КИММЕРИЯ-АРТ.*?(?=\nfunction |\n</script>)',
        '', html, flags=re.DOTALL
    )

    # Удаляем старый отдельный <script> блок афиши если вдруг есть
    html = re.sub(
        r'<script>\s*\(function\(\) \{\s*var _slug.*?\}\)\(\);\s*</script>\s*',
        '', html, flags=re.DOTALL
    )

    # Вставляем HTML-блок перед первым <div class="admin-actions">
    marker = '<div class="admin-actions">'
    idx = html.find(marker)
    if idx == -1:
        print('  [!] admin-actions не найден')
        return False

    html = html[:idx] + BUTTON_HTML + html[idx:]

    # Вставляем JS-блок перед </body>
    body_end = html.rfind('</body>')
    if body_end == -1:
        body_end = html.rfind('</html>')
    html = html[:body_end] + JS_BLOCK + '\n' + html[body_end:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


ok = 0
for slug in sorted(os.listdir(BASE)):
    page = os.path.join(BASE, slug, 'index.html')
    if not os.path.isfile(page):
        continue
    print(f'[{slug}]', end=' ', flush=True)
    if clean_and_patch(page):
        print('OK')
        ok += 1
    else:
        print('пропущено')

print(f'\nГотово: {ok} файлов обновлено')
