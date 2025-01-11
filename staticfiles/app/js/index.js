// Add fade-in animations when elements come into view
const fadeIns = document.querySelectorAll(".fade-in");

const observer = new IntersectionObserver(
    entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    },
    { threshold: 0.2 }
);

fadeIns.forEach(fadeIn => observer.observe(fadeIn));

/**
let currentSlide = 0;

const slides = document.querySelectorAll('.carousel__slide');
const prevButton = document.querySelector('.carousel__control.prev');
const nextButton = document.querySelector('.carousel__control.next');

function updateSlide(index) {
    const totalSlides = slides.length;

    slides.forEach((slide, i) => {
        slide.style.transform = `translateX(${(i - index) * 100}%)`;
    });
}

function goToNextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    updateSlide(currentSlide);
}

function goToPrevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    updateSlide(currentSlide);
}

nextButton.addEventListener('click', goToNextSlide);
prevButton.addEventListener('click', goToPrevSlide);

// Initialize carousel
updateSlide(currentSlide);
*/