// Detalhes dos serviços: clicar num card de "Nossos serviços" abre uma janela com a descrição completa,
// com setas para passar pelos serviços (como a galeria). Também funciona com o teclado (Esc, ← e →)
// e deslizando o dedo. O texto vem do .service-card__details de cada card, no index.html.
(() => {
  const cards = Array.from(document.querySelectorAll(".service-card"));
  if (cards.length === 0) return;

  const services = cards.map((card) => ({
    title: card.querySelector("h3").textContent.trim(),
    image: card.querySelector("img"),
    details: card.querySelector(".service-card__details"),
  }));

  const ICONS = {
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  };

  const modal = document.createElement("div");
  modal.className = "service-modal";
  modal.hidden = true;
  modal.setAttribute("role", "dialog");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("aria-labelledby", "service-modal-title");
  modal.innerHTML = `
    <button type="button" class="lightbox__button service-modal__close" aria-label="Fechar">${ICONS.close}</button>
    <button type="button" class="lightbox__button service-modal__prev" aria-label="Serviço anterior">${ICONS.prev}</button>
    <article class="service-modal__panel">
      <img class="service-modal__img" alt="" />
      <div class="service-modal__body">
        <p class="service-modal__counter"></p>
        <h3 class="service-modal__title" id="service-modal-title"></h3>
        <div class="service-modal__text"></div>
      </div>
    </article>
    <button type="button" class="lightbox__button service-modal__next" aria-label="Próximo serviço">${ICONS.next}</button>
  `;
  document.body.appendChild(modal);

  const panel = modal.querySelector(".service-modal__panel");
  const image = modal.querySelector(".service-modal__img");
  const counter = modal.querySelector(".service-modal__counter");
  const title = modal.querySelector(".service-modal__title");
  const text = modal.querySelector(".service-modal__text");
  const closeButton = modal.querySelector(".service-modal__close");

  let current = 0;
  let opener = null;

  function show(index) {
    current = (index + services.length) % services.length; // passa do último para o primeiro e vice-versa
    const service = services[current];
    image.src = service.image.currentSrc || service.image.src;
    image.alt = service.image.alt;
    counter.textContent = `${current + 1} / ${services.length}`;
    title.textContent = service.title;
    text.innerHTML = service.details ? service.details.innerHTML : "";
    panel.scrollTop = 0;
  }

  function open(index) {
    opener = cards[index]; // ao fechar, o foco volta para o card que abriu a janela
    show(index);
    modal.hidden = false;
    document.documentElement.classList.add("lightbox-open"); // trava a rolagem da página (lightbox.css)
    closeButton.focus();
  }

  function close() {
    modal.hidden = true;
    document.documentElement.classList.remove("lightbox-open");
    if (opener) opener.focus();
  }

  cards.forEach((card, index) => {
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Ver detalhes: ${services[index].title}`);
    card.addEventListener("click", () => open(index));
    card.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      open(index);
    });
  });

  closeButton.addEventListener("click", close);
  modal.querySelector(".service-modal__prev").addEventListener("click", () => show(current - 1));
  modal.querySelector(".service-modal__next").addEventListener("click", () => show(current + 1));

  // Clicar no fundo escuro (fora da janela e dos botões) fecha
  modal.addEventListener("click", (event) => {
    if (event.target === modal) close();
  });

  document.addEventListener("keydown", (event) => {
    if (modal.hidden) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowLeft") show(current - 1);
    if (event.key === "ArrowRight") show(current + 1);
  });

  // Deslizar o dedo para os lados passa os serviços (só conta o movimento mais lateral que vertical,
  // para não atrapalhar a rolagem do texto)
  let touchStartX = null;
  let touchStartY = null;
  modal.addEventListener("touchstart", (event) => {
    touchStartX = event.touches[0].clientX;
    touchStartY = event.touches[0].clientY;
  }, { passive: true });
  modal.addEventListener("touchend", (event) => {
    if (touchStartX === null) return;
    const deltaX = event.changedTouches[0].clientX - touchStartX;
    const deltaY = event.changedTouches[0].clientY - touchStartY;
    if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) show(deltaX < 0 ? current + 1 : current - 1);
    touchStartX = null;
  });
})();
