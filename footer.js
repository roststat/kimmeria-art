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
