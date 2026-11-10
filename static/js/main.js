// LC Robot & Eventos — comportamento mínimo, sem bibliotecas.
(function () {
  "use strict";
  var raiz = document.documentElement;
  raiz.classList.add("js");
  var reduz = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // cabeçalho sólido ao rolar + barra de orçamento no celular
  var topo = document.getElementById("topo");
  var barra = document.querySelector(".barra-zap");
  var hero = document.getElementById("inicio");
  var fim = document.getElementById("contato");
  function aoRolar() {
    var y = window.scrollY;
    topo.classList.toggle("solido", y > 40);
    if (barra && hero) {
      var noFim = fim && y + window.innerHeight > fim.offsetTop + 120;
      barra.classList.toggle("visivel", y > hero.offsetHeight * 0.7 && !noFim);
    }
  }
  window.addEventListener("scroll", aoRolar, { passive: true });
  aoRolar();

  // menu móvel
  var burger = document.querySelector(".burger");
  var menu = document.getElementById("menu");
  function fechaMenu() {
    menu.classList.remove("aberto");
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Abrir menu");
    document.body.style.overflow = "";
  }
  burger.addEventListener("click", function () {
    var abre = !menu.classList.contains("aberto");
    menu.classList.toggle("aberto", abre);
    burger.setAttribute("aria-expanded", String(abre));
    burger.setAttribute("aria-label", abre ? "Fechar menu" : "Abrir menu");
    document.body.style.overflow = abre ? "hidden" : "";
    if (abre) topo.classList.add("solido");
  });
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) fechaMenu(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") fechaMenu(); });
  window.matchMedia("(min-width: 900px)").addEventListener("change", fechaMenu);

  // revelar ao rolar
  var itens = document.querySelectorAll(".reveal");
  if (reduz || !("IntersectionObserver" in window)) {
    itens.forEach(function (el) { el.classList.add("dentro"); });
  } else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("dentro"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    itens.forEach(function (el) { io.observe(el); });
  }

  // vídeo do hero: respeita redução de movimento
  var vid = document.querySelector(".hero-video");
  if (vid && reduz) { vid.removeAttribute("autoplay"); vid.pause(); }

  // lightbox
  var lb = document.getElementById("lb");
  if (lb && typeof lb.showModal === "function") {
    var img = lb.querySelector("img");
    var ultimo = null;
    document.querySelectorAll("[data-lightbox]").forEach(function (b) {
      b.addEventListener("click", function () {
        ultimo = b;
        img.src = b.getAttribute("data-lightbox");
        img.alt = b.getAttribute("data-alt") || "";
        lb.showModal();
      });
    });
    lb.addEventListener("click", function (e) { if (e.target === lb || e.target.closest(".lb-fechar")) lb.close(); });
    lb.addEventListener("close", function () { img.removeAttribute("src"); if (ultimo) ultimo.focus(); });
  }

  // botões de WhatsApp sem número configurado: leva para o contato, sem link falso
  document.querySelectorAll("[data-pendente]").forEach(function (a) {
    a.setAttribute("title", "WhatsApp ainda não configurado");
  });
})();
