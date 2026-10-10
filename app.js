/* Vanilla SPA: no dependencies, build step, or full-page navigation. */
(() => {
  'use strict';
  const main = document.querySelector('#main');
  const sidebar = document.querySelector('#sidebar');
  const menu = document.querySelector('#menu-toggle');
  const routeStatus = document.querySelector('#route-status');
  const pages = {
    home: '<section class="hero"><div class="eyebrow">01 / SYSTEM OVERVIEW</div><h1 class="page-title">Small surface.<br><span class="accent">Fast by default.</span></h1><p class="lead">A minimal, responsive single-page app. Navigation updates the view without reloading the document.</p><div class="button-row"><a class="button" href="#/chat">Open chat interface →</a><a class="button secondary" href="#/settings">Settings</a></div></section><section class="grid" aria-label="Project characteristics"><article class="card"><div class="card-kicker">RUNTIME</div><div class="card-value">0 deps</div><div class="card-copy">Plain HTML, CSS and JavaScript.</div></article><article class="card"><div class="card-kicker">NAVIGATION</div><div class="card-value">SPA</div><div class="card-copy">Hash routes; no document reloads.</div></article><article class="card"><div class="card-kicker">DELIVERY</div><div class="card-value">Static</div><div class="card-copy">Ready for GitHub Pages.</div></article></section><h2 class="section-heading">BOOT LOG</h2><section class="terminal"><div class="terminal-head">● &nbsp; test-web / session</div><div class="terminal-body"><span class="prompt">$</span> init --minimal<br><span class="prompt">✓</span> styles loaded<br><span class="prompt">✓</span> client router ready<br><span class="prompt">✓</span> zero external requests<br><span class="prompt">$</span> <span class="cursor"></span></div></section>',
    chat: '<div class="eyebrow">02 / CHAT INTERFACE</div><h1 class="page-title">Conversation <span class="accent">shell.</span></h1><p class="lead">Lightweight UI foundation. Authentication and model streaming are not connected yet.</p><section class="chat-empty"><div><div class="chat-empty-mark">&gt;_</div><h2>No session connected</h2><p>This is only the interface skeleton. A supported sign-in flow needs a trusted local service; browser-only static files cannot safely store credentials.</p><div class="button-row center"><a class="button secondary" href="#/settings">Review settings</a><a class="button" href="#/home">Back home</a></div></div></section>',
    settings: '<div class="eyebrow">03 / CONFIGURATION</div><h1 class="page-title">Shell <span class="accent">settings.</span></h1><p class="lead">Preferences are stored locally in this browser. No account credentials are saved.</p><section class="card settings-card"><div class="card-kicker">INTERFACE</div><div class="field"><label for="display-name">Display label</label><input id="display-name" maxlength="40" autocomplete="off" placeholder="test-web"></div><div class="button-row"><button class="button" id="save-settings" type="button">Save preference</button><button class="button secondary" id="reset-settings" type="button">Reset</button></div><p id="settings-result" class="card-copy" role="status">Preferences stay in this browser.</p></section><div class="notice">Never put OAuth secrets, access tokens, or API keys in a public static site.</div>'
  };
  function currentRoute() {
    const name = location.hash.slice(2).split('/')[0];
    return Object.hasOwn(pages, name) ? name : 'home';
  }
  function render() {
    const route = currentRoute();
    main.innerHTML = pages[route];
    routeStatus.textContent = 'route: /' + route;
    document.title = route[0].toUpperCase() + route.slice(1) + ' · test-web';
    document.querySelectorAll('[data-route]').forEach(link => {
      const active = link.dataset.route === route;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    sidebar.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
    if (route === 'settings') setupSettings();
  }
  function setupSettings() {
    const input = document.querySelector('#display-name');
    const result = document.querySelector('#settings-result');
    try { input.value = localStorage.getItem('test-web.display-name') || ''; } catch {}
    document.querySelector('#save-settings').addEventListener('click', () => {
      try {
        const value = input.value.trim().slice(0, 40);
        if (value) localStorage.setItem('test-web.display-name', value);
        else localStorage.removeItem('test-web.display-name');
        result.textContent = 'Saved in this browser.';
      } catch { result.textContent = 'Browser storage unavailable; not saved.'; }
    });
    document.querySelector('#reset-settings').addEventListener('click', () => {
      input.value = '';
      try { localStorage.removeItem('test-web.display-name'); result.textContent = 'Reset complete.'; }
      catch { result.textContent = 'Browser storage unavailable.'; }
    });
  }
  menu.addEventListener('click', () => {
    const open = sidebar.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });
  window.addEventListener('hashchange', render);
  if (!location.hash) location.hash = '#/home';
  else render();
})();
