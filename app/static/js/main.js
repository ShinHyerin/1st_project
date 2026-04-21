//document.addEventListener('DOMContentLoaded', function() {
//    var swiper = new Swiper(".mySwiper", {
//        loop: true,
//        spaceBetween: 0,
//        centeredSlides: true,
//        autoplay: {
//            delay: 5000,
//            disableOnInteraction: false,
//        },
//        pagination: {
//            el: ".swiper-pagination",
//            clickable: true,
//        },
//        navigation: {
//            nextEl: ".swiper-button-next",
//            prevEl: ".swiper-button-prev",
//        },
//    });
//});

document.addEventListener('DOMContentLoaded', function() {
    // Swiper 초기화 설정
    const swiper = new Swiper(".mySwiper", {
        // 슬라이드 높이를 가장 긴 슬라이드에 맞춰 자동으로 확장합니다.
        autoHeight: false,
        // 슬라이드들의 높이를 통일시킵니다. (기본값이 true인 경우가 많음)
        calculateHeight: true,
        loop: true,
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
    });
});