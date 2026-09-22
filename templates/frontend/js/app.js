/* Genial Labs · app.js — interações sem framework.
   Menu mobile, tema claro/escuro persistente, toasts, status /healthz, formulário. */
(function () {
  'use strict';

  var raiz = document.documentElement;

  /* ---------- Tema claro/escuro (persistido em localStorage) ---------- */
  function aplicarTema(tema) {
    raiz.classList.remove('tema-claro', 'tema-escuro');
    if (tema === 'escuro') raiz.classList.add('tema-escuro');
    if (tema === 'claro') raiz.classList.add('tema-claro');
  }
  function temaAtual() {
    if (raiz.classList.contains('tema-escuro')) return 'escuro';
    if (raiz.classList.contains('tema-claro')) return 'claro';
    return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'escuro' : 'claro';
  }
  var salvo = null;
  try { salvo = localStorage.getItem('gl-tema'); } catch (e) { /* sem storage */ }
  if (salvo === 'claro' || salvo === 'escuro') aplicarTema(salvo);

  var btnTema = document.getElementById('trocar-tema');
  if (btnTema) {
    btnTema.addEventListener('click', function () {
      var alvo = temaAtual() === 'escuro' ? 'claro' : 'escuro';
      aplicarTema(alvo);
      try { localStorage.setItem('gl-tema', alvo); } catch (e) { /* sem storage */ }
      btnTema.setAttribute('aria-label', 'Alternar para tema ' + (alvo === 'escuro' ? 'claro' : 'escuro'));
    });
  }

  /* ---------- Menu mobile (fecha com Esc ou toque fora) ---------- */
  var btnMenu = document.getElementById('btn-menu');
  var lista = document.getElementById('menu');
  function fecharMenu() {
    lista.classList.remove('aberto');
    btnMenu.setAttribute('aria-expanded', 'false');
    btnMenu.setAttribute('aria-label', 'Abrir menu');
  }
  if (btnMenu && lista) {
    btnMenu.addEventListener('click', function () {
      var aberto = lista.classList.toggle('aberto');
      btnMenu.setAttribute('aria-expanded', String(aberto));
      btnMenu.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
    });
    document.addEventListener('click', function (ev) {
      if (!lista.contains(ev.target) && !btnMenu.contains(ev.target)) fecharMenu();
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') fecharMenu();
    });
  }

  /* ---------- Toasts (feedback não bloqueante, anunciado por leitores) ---------- */
  var regiaoToast = document.querySelector('.toast-regiao');
  function toast(mensagem, tipo) {
    if (!regiaoToast) return;
    var el = document.createElement('div');
    el.className = 'toast ' + (tipo || 'info');
    el.textContent = mensagem;
    regiaoToast.appendChild(el);
    setTimeout(function () {
      if (el.parentNode) regiaoToast.removeChild(el);
    }, 4000);
  }
  window.glToast = toast;

  /* ---------- Status da API (/healthz, o contrato Genial Labs) ---------- */
  var badgeStatus = document.getElementById('badge-status');
  var btnStatus = document.getElementById('verificar-status');
  function checarStatus() {
    if (!badgeStatus || !window.fetch) return;
    badgeStatus.className = 'badge neutro';
    badgeStatus.textContent = 'verificando…';
    var inicio = Date.now();
    var ac = window.AbortController ? new AbortController() : null;
    var timer = ac ? setTimeout(function () { ac.abort(); }, 2500) : null;
    fetch('/healthz', { cache: 'no-store', signal: ac ? ac.signal : undefined })
      .then(function (resp) {
        if (timer) clearTimeout(timer);
        var ms = Date.now() - inicio;
        if (!resp.ok) throw new Error('http ' + resp.status);
        badgeStatus.className = 'badge sucesso';
        badgeStatus.textContent = 'API online · ' + ms + ' ms';
      })
      .catch(function () {
        if (timer) clearTimeout(timer);
        badgeStatus.className = 'badge perigo';
        badgeStatus.textContent = 'API indisponível';
      });
  }
  if (btnStatus) btnStatus.addEventListener('click', checarStatus);
  checarStatus();

  /* ---------- Formulário (validação com mensagem ligada ao campo) ---------- */
  var form = document.getElementById('form-demo');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = document.getElementById('email');
      var termo = document.getElementById('termo');
      var validoEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
      document.getElementById('campo-email').classList.toggle('invalido', !validoEmail);
      document.getElementById('campo-termo').classList.toggle('invalido', !termo.checked);
      if (!validoEmail || !termo.checked) {
        (validoEmail ? termo : email).focus();
        return;
      }
      var btn = form.querySelector('button[type="submit"]');
      btn.classList.add('carregando');
      btn.disabled = true;
      setTimeout(function () {
        btn.classList.remove('carregando');
        btn.disabled = false;
        form.reset();
        toast('Dados enviados com sucesso.', 'sucesso');
      }, 900);
    });
  }
})();
