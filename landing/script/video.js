// Vídeo de apresentação: o botão de play some quando o vídeo começa e volta quando pausa.
// Sem arquivo de vídeo, nada acontece.
(() => {
  const presentationVideo = document.querySelector(".video-frame video");
  const videoPlayButton = document.querySelector(".video-play");

  videoPlayButton.addEventListener("click", () => {
    presentationVideo.play().catch(() => {});
  });
  presentationVideo.addEventListener("play", () => {
    videoPlayButton.hidden = true;
  });
  presentationVideo.addEventListener("pause", () => {
    videoPlayButton.hidden = false;
  });
})();
