# -*- coding: utf-8 -*-
import os, re, sys

BASE = r'D:\Загрузки Д\Киммерия-Арт\programmy'

# Кнопка вставляется перед .admin-actions div
BUTTON_HTML = '''              <div class="admin-section admin-section-afisha">
                <div class="admin-section-top">
                  <div class="admin-section-title">Афиша Киммерия-Арт</div>
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
                  <div id="afishaResult" style="font-size:12px;color:#888;margin-top:8px;text-align:center;min-height:16px;"></div>
                </div>
              </div>
'''

# JS функция вставляется перед закрывающим </script> в конце файла
JS_FUNCTION = r"""
function addToAfisha() {
  var date  = document.getElementById('afisha-date').value;
  var time  = document.getElementById('afisha-time').value || '19:00';
  var price = document.getElementById('afisha-price').value.trim() || 'По запросу';
  var result = document.getElementById('afishaResult');

  if (!date) { result.textContent = 'Укажите дату'; result.style.color='#c00'; return; }

  var btn = document.getElementById('afishaBtn');
  btn.disabled = true;
  btn.textContent = 'Добавляю…';
  result.textContent = '';

  var d = new Date(date);
  var months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
  var dateLabel = d.getDate() + ' ' + months[d.getMonth()] + ' · ' + time;

  var title   = (document.querySelector('.page-title') || {}).textContent || '';
  var desc    = (document.querySelector('.page-subtitle') || document.querySelector('.body-text') || {}).textContent || '';
  var eyebrow = (document.querySelector('.page-eyebrow') || {}).textContent || '';
  var imgEl   = document.querySelector('.poster-img');
  var imgUrl  = imgEl ? imgEl.src : '';
  var slug    = PAGE_URL.replace(/.*\/programmy\//, '').replace(/\/$/, '');

  fetch('/api/afisha', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-admin-password': ADMIN_PASSWORD },
    body: JSON.stringify({
      slug: slug,
      title: title.trim(),
      description: desc.trim().slice(0, 200),
      date: date,
      time: time,
      date_label: dateLabel,
      format: eyebrow.toLowerCase().includes('лекц') ? 'лекция'
            : eyebrow.toLowerCase().includes('спект') ? 'спектакль'
            : eyebrow.toLowerCase().includes('кино') ? 'кинопоказ'
            : 'мероприятие',
      price: price,
      image_url: imgUrl,
    }),
  })
  .then(function(r){ return r.json(); })
  .then(function(data){
    if (data.ok) {
      result.textContent = 'Добавлено на главную ✓';
      result.style.color = '#1a4a3a';
    } else {
      result.textContent = 'Ошибка: ' + (data.error || 'неизвестная');
      result.style.color = '#c00';
    }
    btn.disabled = false;
    btn.innerHTML = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><line x1="8" y1="5" x2="8" y2="11"/><line x1="5" y1="8" x2="11" y2="8"/></svg> Добавить в афишу';
  })
  .catch(function(e){
    result.textContent = 'Ошибка соединения';
    result.style.color = '#c00';
    btn.disabled = false;
  });
}
"""

def patch_file(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    if 'addToAfisha' in html:
        print(f'  уже есть, пропускаю')
        return False

    # Найдём место вставки — перед первым <div class="admin-actions">
    # (это блок с кнопкой КП)
    marker = '<div class="admin-actions">'
    idx = html.find(marker)
    if idx == -1:
        print(f'  [!] admin-actions не найден')
        return False

    html = html[:idx] + BUTTON_HTML + html[idx:]

    # Вставим JS перед последним </script>
    last_script = html.rfind('</script>')
    if last_script == -1:
        print(f'  [!] </script> не найден')
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
    print(f'[{slug}]', end=' ')
    sys.stdout.flush()
    if patch_file(page):
        print('OK')
        ok += 1

print(f'\nГотово: {ok} файлов обновлено')
