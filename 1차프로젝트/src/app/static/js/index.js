document.addEventListener('DOMContentLoaded', () => {

    // ===== 1️⃣ 캐러셀 =====
    const sliderWrapper = document.querySelector('.slider-wrapper');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (sliderWrapper && slides.length > 0) {

        const firstClone = slides[0].cloneNode(true);
        const lastClone = slides[slides.length - 1].cloneNode(true);

        sliderWrapper.appendChild(firstClone);
        sliderWrapper.insertBefore(lastClone, sliderWrapper.firstChild);

        const originalCount = slides.length;

        let currentIndex = 1;
        let isMoving = false;

        sliderWrapper.style.transform = `translateX(-100%)`;

        function goToSlide(index) {
            if (isMoving) return;
            isMoving = true;

            currentIndex = index;

            sliderWrapper.style.transition = 'transform 0.6s ease';
            sliderWrapper.style.transform = `translateX(-${currentIndex * 100}%)`;

            setTimeout(() => {

                if (currentIndex === originalCount + 1) {
                    sliderWrapper.style.transition = 'none';
                    currentIndex = 1;
                    sliderWrapper.style.transform = `translateX(-100%)`;
                }

                if (currentIndex === 0) {
                    sliderWrapper.style.transition = 'none';
                    currentIndex = originalCount;
                    sliderWrapper.style.transform = `translateX(-${originalCount * 100}%)`;
                }

                isMoving = false;
            }, 600);
        }

        nextBtn.addEventListener('click', () => goToSlide(currentIndex + 1));
        prevBtn.addEventListener('click', () => goToSlide(currentIndex - 1));

        setInterval(() => {
            if (!isMoving) goToSlide(currentIndex + 1);
        }, 4000);
    }


    // ===== 2️⃣ reveal (완전 안정 버전) =====

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {

            const targets = entry.target.querySelectorAll('.reveal-left, .reveal-up');

            if (entry.isIntersecting) {
                targets.forEach((el, index) => {
                    setTimeout(() => {
                        el.classList.add('active');
                    }, index * 150);
                });
            } else {
                targets.forEach(el => el.classList.remove('active'));
            }

        });
    }, {
        threshold: 0.05,
        root: null, // 🔥 핵심: 무조건 viewport 기준
    });

    document.querySelectorAll('.scroll-section').forEach(section => {
        revealObserver.observe(section);
    });

});