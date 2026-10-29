// Trabalhos por serviço: os filtros de "Veja alguns dos nossos trabalhos" usam os mesmos serviços dos cards
// de "Nossos serviços" (clicar num card abre os detalhes do serviço, ver script/service-details.js)
(() => {
  const SERVICE_NAMES = {
    georreferenciamento: "Georreferenciamento",
    car: "CAR",
    credito: "Crédito Rural",
  };

  const projectFilters = Array.from(document.querySelectorAll(".projects-menu button"));
  const projectsGrid = document.querySelector(".projects-grid");
  const projectImages = Array.from(projectsGrid.querySelectorAll("img"));
  const projectsEmptyMessage = document.querySelector(".projects-empty");

  // Foto grande do serviço selecionado; as fotos da grade viram miniaturas clicáveis
  const mainImage = document.createElement("img");
  mainImage.className = "projects-main";
  mainImage.alt = "";
  projectsGrid.parentNode.insertBefore(mainImage, projectsGrid);

  function showMainImage(image) {
    projectImages.forEach((thumb) => thumb.classList.toggle("is-current", thumb === image));
    mainImage.hidden = !image;
    if (image) {
      mainImage.src = image.currentSrc || image.src;
      mainImage.alt = image.alt;
    }
  }

  projectsGrid.addEventListener("click", (event) => {
    if (event.target.tagName === "IMG") showMainImage(event.target);
  });

  function selectService(service) {
    projectFilters.forEach((button) => {
      const selected = button.dataset.service === service;
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });

    const visibleImages = projectImages.filter((image) => {
      const show = image.dataset.service === service;
      image.hidden = !show;
      return show;
    });
    const visibleCount = visibleImages.length;
    showMainImage(visibleImages[0]);

    // Serviço sem fotos publicadas
    projectsEmptyMessage.hidden = visibleCount > 0;
    if (visibleCount === 0) {
      projectsEmptyMessage.textContent = `Em breve, mais trabalhos de ${SERVICE_NAMES[service]} por aqui.`;
    }
  }

  projectFilters.forEach((button) => {
    button.addEventListener("click", () => selectService(button.dataset.service));
  });

  selectService("georreferenciamento");
})();
