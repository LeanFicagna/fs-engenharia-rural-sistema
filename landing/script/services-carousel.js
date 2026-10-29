// Carrossel de "Nossos serviços" (Swiper, carregado do CDN)
// Inicia no "load" para garantir que o Swiper (CDN, defer) já esteja disponível
window.addEventListener("load", () => {
  new Swiper(".services-carousel", {
    spaceBetween: 20,
    slidesPerView: 1, // fallback padrão

    breakpoints: {
      480: {
        slidesPerView: 2
      },
      1024: {
        slidesPerView: 4
      }
    },

    pagination: {
      el: ".swiper-pagination",
      clickable: true
    },

    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev"
    }
  });
});
