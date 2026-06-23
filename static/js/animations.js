/* ================================================================
   ZTech — animations.js
   Cursor glitter + scroll reveal
   ================================================================ */

(function () {
  'use strict';

  /* ── Cursor glow ── */
  const glow = document.getElementById('cursorGlow');

  document.addEventListener('mousemove', function (e) {
    if (glow) {
      glow.style.left = e.clientX + 'px';
      glow.style.top  = e.clientY + 'px';
    }
    spawnParticle(e.clientX, e.clientY);
  });

  /* Spawn a tiny glitter particle on mouse move */
  var lastSpawn = 0;
  function spawnParticle(x, y) {
    var now = Date.now();
    if (now - lastSpawn < 40) return;   // throttle: 25fps max
    lastSpawn = now;

    var p   = document.createElement('div');
    p.className = 'particle';

    var size  = Math.random() * 4 + 2;
    var angle = Math.random() * Math.PI * 2;
    var dist  = Math.random() * 18 + 4;
    var tx    = Math.round(Math.cos(angle) * dist);
    var ty    = Math.round(Math.sin(angle) * dist - 20);
    var dur   = (Math.random() * 0.5 + 0.5).toFixed(2) + 's';

    var colors = [
      'var(--accent)',
      'var(--accent-2)',
      'var(--accent-3)'
    ];
    var color = colors[Math.floor(Math.random() * colors.length)];

    p.style.cssText = [
      'left:' + (x + tx) + 'px',
      'top:'  + (y + ty) + 'px',
      'width:'  + size + 'px',
      'height:' + size + 'px',
      'background:' + color,
      'opacity:0.85',
      '--tx:' + tx + 'px',
      '--ty:' + ty + 'px',
      '--dur:' + dur
    ].join(';');

    document.body.appendChild(p);
    setTimeout(function () { p.remove(); }, parseFloat(dur) * 1000 + 50);
  }

  /* ── Scroll reveal ── */
  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

  function initReveal() {
    document.querySelectorAll('.reveal').forEach(function (el) {
      revealObserver.observe(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReveal);
  } else {
    initReveal();
  }

}());
