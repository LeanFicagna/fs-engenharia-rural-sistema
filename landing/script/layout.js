// Barra superior e rodapé
(() => {
  const toggle = document.querySelector(".navbar-toggle");
  const menu = document.querySelector(".navbar-menu");

  toggle.addEventListener("click", () => {
    menu.classList.toggle("is-open");
  });

  document.getElementById("copyright-year").textContent = new Date().getFullYear();
})();
