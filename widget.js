(function () {
  var ENDPOINT = 'https://art-kimmeria.ru/events.json';

  var FORMAT_LABELS = {
    'спектакль': 'Спектакль',
    'лекция': 'Лекция',
    'кинопоказ': 'Кинопоказ',
    'встреча': 'Встреча'
  };

  var CSS = `
    .km-widget { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; box-sizing: border-box; }
    .km-widget *, .km-widget *::before, .km-widget *::after { box-sizing: inherit; }
    .km-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }
    .km-card {
      background: #ffffff; border: 1px solid #e8e8e8; border-radius: 14px;
      overflow: hidden; cursor: pointer; display: flex; flex-direction: column;
      text-decoration: none; color: inherit;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .km-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,0,0,0.09); }
    .km-photo { position: relative; aspect-ratio: 3/4; overflow: hidden; flex-shrink: 0; }
    .km-photo img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s; }
    .km-card:hover .km-photo img { transform: scale(1.04); }
    .km-badge {
      position: absolute; top: 10px; left: 10px;
      background: #1a4a3a; color: #fff;
      font-size: 10px; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase;
      padding: 3px 10px; border-radius: 100px;
    }
    .km-body { padding: 14px 16px 16px; display: flex; flex-direction: column; flex: 1; }
    .km-date { font-size: 11px; font-weight: 600; color: #111; margin-bottom: 5px; }
    .km-title { font-size: 14px; font-weight: 700; color: #111; line-height: 1.35; margin-bottom: 6px; }
    .km-desc { font-size: 12px; color: #666; line-height: 1.55; margin-bottom: 12px; flex: 1;
      overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
    .km-bottom { display: flex; align-items: center; justify-content: space-between; gap: 8px;
      padding-top: 10px; border-top: 1px solid #e8e8e8; margin-top: auto; }
    .km-price { font-size: 13px; font-weight: 700; color: #111; }
    .km-btn {
      font-size: 11px; font-weight: 700; color: #fff; background: #1a4a3a;
      padding: 6px 14px; border-radius: 100px; text-decoration: none;
      letter-spacing: 0.05em; text-transform: uppercase; white-space: nowrap;
      transition: opacity 0.15s;
    }
    .km-btn:hover { opacity: 0.85; }
    .km-footer {
      margin-top: 16px; text-align: center;
    }
    .km-footer a {
      font-size: 11px; color: #999; text-decoration: none;
      letter-spacing: 0.04em;
    }
    .km-footer a:hover { color: #1a4a3a; }
    .km-empty { font-size: 14px; color: #999; padding: 24px 0; text-align: center; }
  `;

  function injectCSS() {
    if (document.getElementById('km-widget-css')) return;
    var style = document.createElement('style');
    style.id = 'km-widget-css';
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  function getParam(el, name, fallback) {
    return el.getAttribute('data-' + name) || fallback;
  }

  function filterEvents(events, format, ids, limit) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);

    var result = events.filter(function (e) {
      var d = new Date(e.date);
      if (d < today) return false;
      if (ids) {
        var list = ids.split(',').map(function (s) { return s.trim(); });
        if (list.indexOf(e.id) === -1) return false;
      }
      if (format && format !== 'all') {
        if (e.format !== format) return false;
      }
      return true;
    });

    result.sort(function (a, b) { return new Date(a.date) - new Date(b.date); });

    if (limit) result = result.slice(0, parseInt(limit));
    return result;
  }

  function buildURL(url, partner) {
    if (!partner) return url;
    var sep = url.indexOf('?') === -1 ? '?' : '&';
    return url + sep + 'utm_source=' + encodeURIComponent(partner) + '&utm_medium=widget&utm_campaign=kimmeria_art';
  }

  function renderCards(events, partner) {
    if (!events.length) {
      return '<div class="km-empty">Актуальных мероприятий пока нет</div>';
    }
    return events.map(function (e) {
      var href = buildURL(e.url, partner);
      var badge = FORMAT_LABELS[e.format] || e.format;
      return '<a class="km-card" href="' + href + '" target="_blank" rel="noopener">' +
        '<div class="km-photo">' +
          '<img src="' + e.image + '" alt="' + e.title + '" loading="lazy">' +
          '<span class="km-badge">' + badge + '</span>' +
        '</div>' +
        '<div class="km-body">' +
          '<div class="km-date">' + e.date_label + '</div>' +
          '<div class="km-title">' + e.title + '</div>' +
          '<div class="km-desc">' + e.description + '</div>' +
          '<div class="km-bottom">' +
            '<span class="km-price">' + e.price + '</span>' +
            '<span class="km-btn">Подробнее</span>' +
          '</div>' +
        '</div>' +
      '</a>';
    }).join('');
  }

  function formatDateRu(dateStr) {
    var months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
    var d = new Date(dateStr);
    return d.getDate() + ' ' + months[d.getMonth()];
  }

  function renderScheduleCards(items, partner) {
    if (!items.length) {
      return '<div class="km-empty">Программа мероприятий уточняется</div>';
    }
    var today = new Date(); today.setHours(0,0,0,0);
    var upcoming = items.filter(function(i) { return new Date(i.event_date) >= today; });
    if (!upcoming.length) upcoming = items;
    return upcoming.map(function(item) {
      var href = buildURL('https://art-kimmeria.ru/programmy/' + item.program_slug + '/', partner);
      var dateLabel = formatDateRu(item.event_date) + ' · ' + item.event_time;
      return '<a class="km-card" href="' + href + '" target="_blank" rel="noopener">' +
        '<div class="km-photo">' +
          (item.program_image ? '<img src="' + item.program_image + '" alt="' + item.program_title + '" loading="lazy">' : '') +
          '<span class="km-badge">Программа</span>' +
        '</div>' +
        '<div class="km-body">' +
          '<div class="km-date">' + dateLabel + '</div>' +
          '<div class="km-title">' + item.program_title + '</div>' +
          '<div class="km-bottom">' +
            '<span class="km-price">' + item.price + '</span>' +
            '<span class="km-btn">Подробнее</span>' +
          '</div>' +
        '</div>' +
      '</a>';
    }).join('');
  }

  function initWidget(container) {
    var token   = getParam(container, 'token',   null);
    var format  = getParam(container, 'format',  null);
    var limit   = getParam(container, 'limit',   null);
    var ids     = getParam(container, 'ids',     null);
    var partner = getParam(container, 'partner', null);
    var footer  = getParam(container, 'footer',  'true') !== 'false';

    container.classList.add('km-widget');

    // Режим расписания заказчика
    if (token) {
      fetch('https://art-kimmeria.ru/api/schedules?token=' + token)
        .then(function(r) { return r.json(); })
        .then(function(data) {
          var html = '<div class="km-grid">' + renderScheduleCards(data.items || [], partner) + '</div>';
          if (footer) {
            html += '<div class="km-footer"><a href="https://art-kimmeria.ru/?utm_source=' +
              (partner || 'widget') + '&utm_medium=widget" target="_blank" rel="noopener">' +
              'Киммерия-Арт · Ялта</a></div>';
          }
          container.innerHTML = html;
        })
        .catch(function() {
          container.innerHTML = '<div class="km-empty">Не удалось загрузить программу</div>';
        });
      return;
    }

    // Стандартный режим — все мероприятия
    fetch(ENDPOINT + '?_=' + Date.now())
      .then(function (r) { return r.json(); })
      .then(function (events) {
        var filtered = filterEvents(events, format, ids, limit);
        var html = '<div class="km-grid">' + renderCards(filtered, partner) + '</div>';
        if (footer) {
          html += '<div class="km-footer"><a href="https://art-kimmeria.ru/?utm_source=' +
            (partner || 'widget') + '&utm_medium=widget" target="_blank" rel="noopener">' +
            'Все мероприятия — Киммерия-Арт · Ялта</a></div>';
        }
        container.innerHTML = html;
      })
      .catch(function () {
        container.innerHTML = '<div class="km-empty">Не удалось загрузить мероприятия</div>';
      });
  }

  function init() {
    injectCSS();
    var containers = document.querySelectorAll('[id="kimmeria-widget"], .kimmeria-widget');
    containers.forEach(initWidget);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
