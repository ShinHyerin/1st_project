window.addEventListener("scroll", () => {
    const nav = document.querySelector(".navbar");
    if (window.scrollY > 50) {
        nav.classList.add("scrolled");
    } else {
        nav.classList.remove("scrolled");
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("hamburgerBtn");
    const nav = document.getElementById("navLinks");

    if (btn && nav) {
        btn.addEventListener("click", () => {
            btn.classList.toggle("active");
            nav.classList.toggle("active");
        });
    }
});