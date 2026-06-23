/* ================================================================
   ZTech — theme.js
   Smooth theme switching
   ================================================================ */
(function () {
  document.querySelectorAll('a[href*="set_theme"]').forEach(function (link) {
    link.addEventListener('click', function () {
      document.documentElement.classList.add('theme-transitioning');
      setTimeout(function () {
        document.documentElement.classList.remove('theme-transitioning');
      }, 500);
    });
  });
}());
