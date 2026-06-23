/* ================================================================
   ZTech — cart.js
   Cart badge update after add-to-cart
   ================================================================ */
(function () {
  function updateBadge(count) {
    var badge = document.getElementById('cartBadge');
    if (!badge) {
      var btn = document.querySelector('.nav-icon-btn[href*="cart"]');
      if (!btn) return;
      badge = document.createElement('span');
      badge.id = 'cartBadge';
      badge.className = 'cart-badge';
      btn.appendChild(badge);
    }
    badge.textContent = count;
    badge.style.animation = 'none';
    requestAnimationFrame(function () {
      badge.style.animation = 'scaleIn 0.3s ease';
    });
  }

  /* Auto-dismiss toast messages */
  function autoDismiss() {
    var container = document.getElementById('messagesContainer');
    if (!container) return;
    setTimeout(function () {
      container.querySelectorAll('.message-toast').forEach(function (t) {
        t.style.transition = 'opacity 0.3s, transform 0.3s';
        t.style.opacity = '0';
        t.style.transform = 'translateX(16px)';
        setTimeout(function () { t.remove(); }, 320);
      });
    }, 4200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoDismiss);
  } else {
    autoDismiss();
  }

  window.updateCartBadge = updateBadge;
}());
