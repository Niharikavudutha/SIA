const slides = document.querySelectorAll('.slide');
const backgrounds = document.querySelectorAll('.background-image');
 
let slideIndex = 0;
let bgIndex = 0;

// Rotate text slides
function showSlide(i) {
  slides.forEach((slide, idx) => {
    slide.classList.remove('active');
    if (i === idx) slide.classList.add('active');
  });
}
function rotateSlides() {
  slideIndex = (slideIndex + 1) % slides.length;
  showSlide(slideIndex);
}
setInterval(rotateSlides, 6000);
 
// Rotate background images
function rotateBackground() {
  backgrounds.forEach((bg, i) => {
    bg.classList.remove('active');
    if (i === bgIndex) bg.classList.add('active');
  });
  bgIndex = (bgIndex + 1) % backgrounds.length;
}
setInterval(rotateBackground, 6000);
 
// Toggle QR and Bot every few seconds
const qrSection = document.getElementById("qr-section");
const botSection = document.getElementById("bot-section");
function toggleBotQR() {
  qrSection.classList.toggle("hidden");
  botSection.classList.toggle("hidden");
 
  setTimeout(toggleBotQR, 8000); // Toggle every 8 seconds
}
toggleBotQR(); // start the loop


