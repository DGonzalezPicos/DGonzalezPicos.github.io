let currentSlide = 0;

function showSlide(index) {
    const slides = document.querySelectorAll('.slide');
    
    slides.forEach((slide, i) => {
        slide.style.transform = `translateX(${100 * (i - index)}%)`;
    });
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % 3; // Adjust the number based on the total number of slides
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + 3) % 3; // Adjust the number based on the total number of slides
    showSlide(currentSlide);
}

// Initial display
showSlide(currentSlide);
