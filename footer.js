(function () {
  var css = `
footer {
  border-top: 1px solid #e8e8e8;
  padding: 28px 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  background: #fff;
}
.footer-logo { font-size: 16px; font-weight: 700; color: #111111; }
.footer-links { display: flex; gap: 20px; flex-wrap: wrap; }
.footer-links a {
  font-size: 13px; color: #999999; text-decoration: none;
  transition: color 0.15s;
}
.footer-links a:hover { color: #111111; }
.footer-copy { font-size: 12px; color: #bbbbbb; width: 100%; }
@media (max-width: 768px) {
  footer { padding: 24px 20px; flex-direction: column; align-items: flex-start; gap: 16px; }
  .footer-links { justify-content: flex-start; gap: 14px; }
}
`;

  var html = `
<footer>
  <div class="footer-logo">Киммерия-Арт</div>
  <div class="footer-links">
    <a href="https://vk.com/kimmeria_art" target="_blank">ВКонтакте</a>
    <a href="https://t.me/kimmeria_art" target="_blank">Telegram</a>
    <a href="/oferta/">Оферта</a>
    <a href="/oferta/#vozvrat">Возврат билетов</a>
    <a href="/privacy/">Политика конфиденциальности</a>
    <a href="/terms/">Пользовательское соглашение</a>
    <a href="/cookies/">Политика cookie</a>
  </div>
  <div class="footer-copy">© 2026 ИП Емельянов Филипп Андреевич · ИНН 772865046680 · Ялта</div>
</footer>
`;

  // Inject CSS
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // Replace placeholder or existing footer
  var placeholder = document.getElementById('site-footer');
  if (placeholder) {
    placeholder.outerHTML = html;
  } else {
    var existing = document.querySelector('footer');
    if (existing) existing.outerHTML = html;
  }
})();

// Автоскрытие стоимости на страницах прошедших мероприятий
(function () {
  var MONTHS = {
    'января':1,'февраля':2,'марта':3,'апреля':4,'мая':5,'июня':6,
    'июля':7,'августа':8,'сентября':9,'октября':10,'ноября':11,'декабря':12
  };

  function parseEventDate(text) {
    // Формат: "20 апреля 2026" (возможно с <br> и днём недели после)
    var m = text.match(/(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})/);
    if (!m) return null;
    return new Date(+m[3], MONTHS[m[2]] - 1, +m[1]);
  }

  function getEventDate() {
    // Ищем в sidebar-date или sidebar-value рядом с меткой "Когда"
    var candidates = document.querySelectorAll('.sidebar-date, .sidebar-value');
    for (var i = 0; i < candidates.length; i++) {
      var d = parseEventDate(candidates[i].textContent);
      if (d) return d;
    }
    return null;
  }

  var eventDate = getEventDate();
  if (!eventDate) return;

  var today = new Date();
  today.setHours(0, 0, 0, 0);

  // Мероприятие прошло — скрываем блоки стоимости
  if (eventDate < today) {
    var priceBlocks = document.querySelectorAll('.sidebar-price-block');
    priceBlocks.forEach(function (el) { el.style.display = 'none'; });

    // Нестандартные блоки стоимости (sidebar-label + sidebar-value/sidebar-price-main)
    var labels = document.querySelectorAll('.sidebar-label, .sidebar-price-label');
    labels.forEach(function (el) {
      if (/стоимость|билеты|энергообмен/i.test(el.textContent)) {
        // Скрываем сам лейбл и следующий элемент с ценой
        el.style.display = 'none';
        var next = el.nextElementSibling;
        while (next && !next.classList.contains('sidebar-label') && !next.classList.contains('btn-past') && !next.classList.contains('btn-primary') && !next.classList.contains('btn-register') && !next.classList.contains('sidebar-divider')) {
          next.style.display = 'none';
          next = next.nextElementSibling;
        }
        if (next && next.classList.contains('sidebar-divider')) {
          next.style.display = 'none';
        }
      }
    });
  }
})();
