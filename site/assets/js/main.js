/* Diallo IA — scripts du site (aucune dépendance, aucun traceur) */
(function () {
  "use strict";

  var WA_NUMBER = "2250777561566";
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Liens WhatsApp : message pré-rempli selon l'endroit du site ---- */
  document.querySelectorAll("[data-wa]").forEach(function (link) {
    var message = link.getAttribute("data-wa") || "";
    link.href = "https://wa.me/" + WA_NUMBER + (message ? "?text=" + encodeURIComponent(message) : "");
    link.target = "_blank";
    link.rel = "noopener";
  });

  /* ---- Liens externes : nouvel onglet ---- */
  document.querySelectorAll('a[href^="http"]').forEach(function (link) {
    link.target = "_blank";
    if (!/noopener/.test(link.rel)) link.rel = (link.rel + " noopener").trim();
  });

  /* ---- En-tête : ombre au défilement ---- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- Menu mobile plein écran ---- */
  var menu = document.getElementById("menu-mobile");
  var openBtn = document.querySelector("[data-menu-open]");
  if (menu && openBtn) {
    var closeMenu = function (focusBack) {
      menu.classList.remove("is-open");
      document.body.classList.remove("menu-open");
      openBtn.setAttribute("aria-expanded", "false");
      setTimeout(function () { if (!menu.classList.contains("is-open")) menu.hidden = true; }, 300);
      if (focusBack) openBtn.focus();
    };
    var openMenu = function () {
      menu.hidden = false;
      requestAnimationFrame(function () { menu.classList.add("is-open"); });
      document.body.classList.add("menu-open");
      openBtn.setAttribute("aria-expanded", "true");
      var first = menu.querySelector("nav a");
      if (first) setTimeout(function () { first.focus(); }, 50);
    };
    openBtn.addEventListener("click", openMenu);
    menu.querySelectorAll("[data-menu-close]").forEach(function (el) {
      el.addEventListener("click", function () { closeMenu(el.tagName === "BUTTON"); });
    });
    menu.querySelectorAll("[data-wa]").forEach(function (el) {
      el.addEventListener("click", function () { closeMenu(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) closeMenu(true);
      if (e.key === "Tab" && menu.classList.contains("is-open")) {
        var items = menu.querySelectorAll("a, button");
        var firstEl = items[0], lastEl = items[items.length - 1];
        if (e.shiftKey && document.activeElement === firstEl) { e.preventDefault(); lastEl.focus(); }
        else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); firstEl.focus(); }
      }
    });
    window.addEventListener("resize", function () { if (window.innerWidth >= 1024 && menu.classList.contains("is-open")) closeMenu(false); });
  }

  /* ---- Onglets des démonstrations (accessibles au clavier) ---- */
  var tablist = document.querySelector('[role="tablist"]');
  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
    var select = function (tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) {
          panel.hidden = !on;
          panel.classList.toggle("is-active", on);
        }
      });
      if (focus) tab.focus();
      tab.scrollIntoView({ block: "nearest", inline: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
    };
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") next = tabs[0];
        if (e.key === "End") next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
  }

  /* ---- Apparition des sections au défilement ---- */
  var revealEls = document.querySelectorAll(".reveal");
  if (!reduceMotion && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---- Infobulle du bouton WhatsApp flottant, montrée une fois ---- */
  var floatBtn = document.querySelector(".wa-float");
  if (floatBtn && !reduceMotion) {
    setTimeout(function () {
      floatBtn.classList.add("show-tip");
      setTimeout(function () { floatBtn.classList.remove("show-tip"); }, 4000);
    }, 6000);
  }
})();
