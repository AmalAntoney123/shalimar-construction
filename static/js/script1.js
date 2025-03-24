// Selectors for header-related elements
let navbar = document.querySelector(".header .navbar");
let searchForm = document.querySelector(".header .search-form");
let loginForm = document.querySelector(".login-form");
let overlay = document.getElementById("overlay");
let contactInfo = document.querySelector(".contact-info");
let closeBtn = document.querySelector(".login-form button"); // Close button inside login form
let costOutput = document.getElementById("costOutput");

// Function to remove all active states
function removeActiveStates() {
    navbar?.classList.remove("active");
    searchForm?.classList.remove("active");
    loginForm?.classList.remove("active");
    contactInfo?.classList.remove("active");
    overlay.style.display = "none"; // Hide overlay
}

// Toggle navbar
let menuBtn = document.querySelector("#menu-btn");
if (menuBtn) {
    menuBtn.addEventListener("click", () => {
        navbar?.classList.toggle("active");
        removeActiveStates();
    });
}

// Toggle search form
let searchBtn = document.querySelector("#search-btn");
if (searchBtn) {
    searchBtn.addEventListener("click", () => {
        searchForm?.classList.toggle("active");
        removeActiveStates();
    });
}

// Close login popup when clicking overlay or close button
function closePopup() {
    loginForm?.classList.remove("active");
    overlay.style.display = "none"; // Hide overlay
}
overlay?.addEventListener("click", closePopup);
closeBtn?.addEventListener("click", closePopup);

// Show contact info
let infoBtn = document.querySelector("#info-btn");
if (infoBtn) {
    infoBtn.addEventListener("click", () => {
        contactInfo?.classList.add("active");
    });
}

// Close contact info
let closeContactBtn = document.querySelector("#close-contact-info");
if (closeContactBtn) {
    closeContactBtn.addEventListener("click", () => {
        contactInfo?.classList.remove("active");
    });
}

// Remove all active elements on scroll
window.addEventListener("scroll", removeActiveStates);

// === Cost Estimation Logic ===
document.getElementById("costForm")?.addEventListener("input", calculateCost);

function calculateCost() {
    let area = parseFloat(document.getElementById("area").value);
    let floors = parseFloat(document.getElementById("floors").value);
    let constructionType = document.getElementById("constructionType").value;
    let output = document.getElementById("costOutput"); // Get output span

    // Reset output for fresh calculation
    output.style.color = "green"; // Default color

    // Validate input values
    if (isNaN(area) || area <= 0 || isNaN(floors) || floors <= 0) {
        output.innerText = "Invalid Input!";
        output.style.color = "red"; // Error message in red
        return;
    }

    // Define rates per square foot
    let ratePerSqFt = {
        standard: 1700,
        premium: 2000,
        luxury: 2500
    };

    // Calculate the cost
    let cost = area * floors * ratePerSqFt[constructionType];

    // Display the estimated cost
    output.innerText = "₹" + cost.toLocaleString();
}
