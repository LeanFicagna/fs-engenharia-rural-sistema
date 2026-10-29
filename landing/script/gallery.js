// Galeria em tela cheia do "Conheça nosso dia a dia": clicar numa foto abre a foto grande,
// com setas para passar as fotos. Também funciona com o teclado (Esc, ← e →) e deslizando o dedo.
// Depois das fotos da grade vêm as da lista .team-gallery__more, que só aparecem aqui.
(() => {
  const cards = Array.from(document.querySelectorAll(".team-gallery .insta-card"));
  if (cards.length === 0) return;

  const gridPhotos = cards.map((card) => {
    const image = card.querySelector("img");
    const title = card.querySelector(".insta-card__title");
    return { src: image.currentSrc || image.src, alt: image.alt, caption: title ? title.textContent.trim() : "" };
  });

  const morePhotos = Array.from(document.querySelectorAll(".team-gallery__more a")).map((link) => ({
    src: link.getAttribute("href"),
    alt: link.textContent.trim(),
    caption: link.dataset.caption || "",
  }));

  const photos = gridPhotos.concat(morePhotos);

  // Selo "+N" no último card, para mostrar que a galeria tem mais fotos que a grade
  if (morePhotos.length > 0) {
    const lastCard = cards[cards.length - 1];
    const badge = document.createElement("span");
    badge.className = "insta-card__more";
    badge.textContent = `+${morePhotos.length}`;
    lastCard.appendChild(badge);
    lastCard.setAttribute("aria-label", `${lastCard.getAttribute("aria-label")} (e mais ${morePhotos.length} fotos na galeria)`);
  }

  const ICONS = {
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  };

  const lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.hidden = true;
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("aria-label", "Fotos do nosso dia a dia");
  lightbox.innerHTML = `
    <button type="button" class="lightbox__button lightbox__close" aria-label="Fechar">${ICONS.close}</button>
    <button type="button" class="lightbox__button lightbox__prev" aria-label="Foto anterior">${ICONS.prev}</button>
    <figure class="lightbox__figure">
      <img class="lightbox__img" alt="" />
      <figcaption class="lightbox__caption"></figcaption>
      <p class="lightbox__counter"></p>
    </figure>
    <button type="button" class="lightbox__button lightbox__next" aria-label="Próxima foto">${ICONS.next}</button>
  `;
  document.body.appendChild(lightbox);

  const image = lightbox.querySelector(".lightbox__img");
  const caption = lightbox.querySelector(".lightbox__caption");
  const counter = lightbox.querySelector(".lightbox__counter");
  const closeButton = lightbox.querySelector(".lightbox__close");

  let current = 0;
  let opener = null;

  function show(index) {
    current = (index + photos.length) % photos.length; // passa da última para a primeira e vice-versa
    const photo = photos[current];
    image.src = photo.src;
    image.alt = photo.alt;
    caption.textContent = photo.caption;
    counter.textContent = `${current + 1} / ${photos.length}`;

    // Já baixa a próxima e a anterior, para não ter espera ao passar
    [current + 1, current - 1].forEach((neighbor) => {
      new Image().src = photos[(neighbor + photos.length) % photos.length].src;
    });
  }

  function open(index) {
    opener = cards[index]; // ao fechar, o foco volta para a foto que abriu a galeria
    show(index);
    lightbox.hidden = false;
    document.documentElement.classList.add("lightbox-open");
    closeButton.focus();
  }

  function close() {
    lightbox.hidden = true;
    document.documentElement.classList.remove("lightbox-open");
    if (opener) opener.focus();
  }

  cards.forEach((card, index) => {
    card.addEventListener("click", () => open(index));
  });

  closeButton.addEventListener("click", close);
  lightbox.querySelector(".lightbox__prev").addEventListener("click", () => show(current - 1));
  lightbox.querySelector(".lightbox__next").addEventListener("click", () => show(current + 1));

  // Clicar no fundo escuro (fora da foto e dos botões) fecha
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) close();
  });

  document.addEventListener("keydown", (event) => {
    if (lightbox.hidden) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowLeft") show(current - 1);
    if (event.key === "ArrowRight") show(current + 1);
  });

  // Deslizar o dedo para os lados passa as fotos
  let touchStartX = null;
  lightbox.addEventListener("touchstart", (event) => {
    touchStartX = event.touches[0].clientX;
  }, { passive: true });
  lightbox.addEventListener("touchend", (event) => {
    if (touchStartX === null) return;
    const deltaX = event.changedTouches[0].clientX - touchStartX;
    if (Math.abs(deltaX) > 40) show(deltaX < 0 ? current + 1 : current - 1);
    touchStartX = null;
  });
})();
