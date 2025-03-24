// Selectors for header-related elements
let navbar = document.querySelector('.header .navbar');
let searchForm = document.querySelector('.header .search-form');
let loginForm = document.querySelector('.login-form-container');
let overlay = document.getElementById("overlay");
let contactInfo = document.querySelector('.contact-info');
let projectTrackingBtn = document.getElementById("projectTrackingBtn");
let closeBtn = document.querySelector('.login-form button'); // Close button inside login form
let loginBtn = document.querySelector('#login-btn');
let closeLoginBtn = document.querySelector('#close-login-btn');

// Function to remove all active states
function removeActiveStates() {
    navbar?.classList.remove('active');
    searchForm?.classList.remove('active');
    loginForm?.classList.remove('active');
    contactInfo?.classList.remove('active');
    overlay.style.display = "none"; // Hide overlay
}

// Toggle navbar
document.querySelector('#menu-btn')?.addEventListener("click", () => {
    navbar.classList.toggle('active');
    searchForm.classList.remove('active');
    loginForm.classList.remove('active');
    overlay.style.display = "none"; // Hide overlay when toggling menu
});

// Toggle search form
document.querySelector('#search-btn')?.addEventListener("click", () => {
    searchForm.classList.toggle('active');
    navbar.classList.remove('active');
    loginForm.classList.remove('active');
    overlay.style.display = "none"; // Hide overlay when toggling search form
});

// Close login popup when clicking overlay or close button
function closePopup() {
    loginForm.classList.remove("active");
    overlay.style.display = "none"; // Hide overlay
}

overlay?.addEventListener("click", closePopup);
closeBtn?.addEventListener("click", closePopup);

// Show contact info
document.querySelector('#info-btn')?.addEventListener("click", () => {
    contactInfo.classList.add('active');
});

// Close contact info
document.querySelector('#close-contact-info')?.addEventListener("click", () => {
    contactInfo.classList.remove('active');
});

// Remove all active elements on scroll
window.addEventListener("scroll", removeActiveStates);

// === Initialize Swiper Sliders ===

// General Swiper Config
const swiperConfig = {
    loop: true,
    grabCursor: true,
    spaceBetween: 20
};

// Swiper instances
new Swiper(".home-slider", {
    ...swiperConfig,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    }
});

new Swiper(".reviews-slider", {
    ...swiperConfig,
    breakpoints: {
        640: { slidesPerView: 1 },
        768: { slidesPerView: 2 },
        991: { slidesPerView: 3 },
    }
});

new Swiper(".blogs-slider", {
    ...swiperConfig,
    breakpoints: {
        640: { slidesPerView: 1 },
        768: { slidesPerView: 2 },
        991: { slidesPerView: 3 },
    }
});

new Swiper(".logo-slider", {
    ...swiperConfig,
    breakpoints: {
        450: { slidesPerView: 2 },
        640: { slidesPerView: 3 },
        768: { slidesPerView: 4 },
        1000: { slidesPerView: 5 },
    }
});

loginBtn.onclick = () => {
    loginForm.classList.add('active');
}

closeLoginBtn.onclick = () => {
    loginForm.classList.remove('active');
}
