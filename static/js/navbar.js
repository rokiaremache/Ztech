/* ================================================================
   ZTech — navbar.js
   Sticky behaviour + mobile hamburger
   ================================================================ */
(function () {
  var nav = document.getElementById('mainNav');
  if (!nav) return;

  /* Scroll: add shadow when not at top */
  window.addEventListener('scroll', function () {
    if (window.scrollY > 60) {
      nav.style.boxShadow = '0 4px 30px rgba(0,0,0,0.18)';
    } else {
      nav.style.boxShadow = 'none';
    }
  }, { passive: true });

  /* Hamburger */
  var ham   = document.getElementById('navHamburger');
  var links = document.getElementById('navLinks');
  if (ham && links) {
    ham.addEventListener('click', function () {
      links.classList.toggle('open');
    });
  }

  /* Close mobile menu when a link is clicked */
  if (links) {
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('open');
      });
    });
  }
}());
