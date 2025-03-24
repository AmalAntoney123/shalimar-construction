document.addEventListener("DOMContentLoaded", function () {
    // Simulated Login System
    function login() {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        if (email === "client@example.com" && password === "password123") {
            document.getElementById("loginPopup").style.display = "none";
            document.getElementById("eMonitorPage").style.display = "block";
            updateProgress(60); // Simulate 60% completion
            loadCompletedImages();
        } else {
            alert("Invalid login credentials.");
        }
    }

    window.login = login; // Make function accessible from HTML

    // Update Progress Bar
    function updateProgress(percent) {
        let progressBar = document.getElementById("progressBar");
        progressBar.style.width = percent + "%";
        progressBar.textContent = percent + "%";
    }

    // Load Completed Work Images
    function loadCompletedImages() {
        let completedImages = document.getElementById("completedImages");
        let images = ["image1.jpg", "image2.jpg", "image3.jpg"];

        images.forEach((img) => {
            let imageElement = document.createElement("img");
            imageElement.src = img;
            completedImages.appendChild(imageElement);
        });
    }
});
