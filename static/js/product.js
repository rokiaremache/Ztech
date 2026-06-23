/* ================================================================
   ZTech — product.js
   Image gallery switcher + quantity buttons
   ================================================================ */
(function () {
  /* Gallery: handled inline in product_detail.html via global functions */

  /* Keyboard quantity input guard */
  document.querySelectorAll('input[type="number"].qty-input').forEach(function (inp) {
    inp.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') e.preventDefault();
    });
  });
}());
