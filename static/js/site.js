// TableTap site animation: progressive enhancement only.
// 1) Page-to-page: a short fade on internal link clicks (forms, anchors,
//    external links and new tabs are untouched, so ordering never breaks).
// 2) Reveal: landing sections fade/slide in once when scrolled into view.
// If JavaScript is off, pages load normally and all content is visible.
(function () {
  document.body.classList.add("tt-page-in");
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a || a.target === "_blank" || a.hasAttribute("download")) return;
    var href = a.getAttribute("href");
    if (!href || href.charAt(0) === "#" || href.indexOf("://") !== -1) return;
    if (href.indexOf("/logout/") !== -1) return;
    e.preventDefault();
    document.body.classList.add("tt-page-leaving");
    setTimeout(function () { window.location.href = href; }, 160);
  });
  var reveal = document.querySelectorAll(".reveal");
  if (reveal.length && "IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); }
      });
    }, { threshold: 0.12 });
    reveal.forEach(function (el) { observer.observe(el); });
  } else {
    reveal.forEach(function (el) { el.classList.add("is-visible"); });
  }
})();
