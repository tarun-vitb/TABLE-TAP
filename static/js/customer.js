// TableTap customer UI: progressive enhancement only. Every action below
// (add, remove, search, veg filter, cart) already works as a plain form
// POST/GET without this file. This file only adds: category-chip highlight
// on scroll, veg-toggle auto-submit, and toast auto-dismiss.
(function () {
  // Toast: dismiss on tap, or after 2.5s.
  var toast = document.querySelector(".tt-toast");
  if (toast) {
    var close = toast.querySelector("button");
    var dismiss = function () { toast.remove(); };
    if (close) close.addEventListener("click", dismiss);
    setTimeout(dismiss, 2500);
  }
  // Veg-only toggle submits its form on change (search still uses Enter).
  var veg = document.getElementById("tt-veg");
  if (veg) veg.addEventListener("change", function () { veg.form.submit(); });
  // Category chips: highlight the section currently in view.
  var chips = document.querySelectorAll(".tt-cat-chip");
  var sections = document.querySelectorAll(".tt-section");
  if (chips.length && sections.length && "IntersectionObserver" in window) {
    var setActive = function (id) {
      chips.forEach(function (c) {
        c.classList.toggle("is-active", c.getAttribute("href") === "#" + id);
      });
    };
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) setActive(e.target.id);
      });
    }, { rootMargin: "-140px 0px -60% 0px" });
    sections.forEach(function (s) { observer.observe(s); });
    chips.forEach(function (c) {
      c.addEventListener("click", function () { setActive(c.getAttribute("href").slice(1)); });
    });
  }
})();
