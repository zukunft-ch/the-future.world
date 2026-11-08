(function () {
  'use strict';
  var root = document.documentElement;
  var toggle = document.querySelector('.theme-toggle');
  function syncTheme() {
    var dark = root.dataset.theme === 'dark';
    toggle.setAttribute('aria-pressed', String(dark));
    document.getElementById('theme-color').content = dark ? '#101315' : '#eef0ec';
  }
  toggle.hidden = false;
  syncTheme();
  toggle.addEventListener('click', function () {
    var dark = root.dataset.theme !== 'dark';
    if (dark) root.dataset.theme = 'dark'; else delete root.dataset.theme;
    try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
    syncTheme();
  });
  var menu = document.getElementById('site-menu');
  var search = document.getElementById('page-search');
  var links = Array.from(menu.querySelectorAll('.menu-links a'));
  function filter() {
    var query = search.value.trim().toLocaleLowerCase();
    var count = 0;
    links.forEach(function (link) {
      link.hidden = !link.textContent.toLocaleLowerCase().includes(query);
      if (!link.hidden) count++;
    });
    document.getElementById('search-status').hidden = count > 0;
  }
  search.addEventListener('input', filter);
  menu.addEventListener('toggle', function () { if (!menu.open) { search.value = ''; filter(); } });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
  });
  document.addEventListener('click', function (event) { if (!menu.contains(event.target)) menu.open = false; });
  if ('serviceWorker' in navigator && location.protocol === 'https:' && location.hostname !== 'localhost') {
    navigator.serviceWorker.register('/sw.js').catch(function () {});
  }
})();
