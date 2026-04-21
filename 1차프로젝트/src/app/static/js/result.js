// result.js

document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       1. HERO 등장 애니메이션
    ========================= */
    const hero = document.querySelector(".report-hero-card");

    if (hero) {
        hero.style.opacity = 0;
        hero.style.transform = "translateY(30px)";

        setTimeout(() => {
            hero.style.transition = "all 0.8s ease";
            hero.style.opacity = 1;
            hero.style.transform = "translateY(0)";
        }, 200);
    }


    /* =========================
       2. 카드 순차 등장
    ========================= */
    const cards = document.querySelectorAll(
        ".warning-card, .result-card, .info-card, .input-card"
    );

    cards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = "translateY(40px)";

        setTimeout(() => {
            card.style.transition = "all 0.7s ease";
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, 300 + index * 120); // ⭐ 순차 등장 핵심
    });


    /* =========================
       3. 스크롤 등장 (고급)
    ========================= */
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, {
        threshold: 0.15
    });

    document.querySelectorAll(".info-card, .input-card").forEach(el => {
        el.style.opacity = 0;
        el.style.transform = "translateY(40px)";
        el.style.transition = "all 0.7s ease";

        observer.observe(el);
    });


    /* =========================
       4. hover 부드럽게 (옵션)
    ========================= */
    document.querySelectorAll(".info-card, .result-card").forEach(card => {
        card.addEventListener("mouseenter", () => {
            card.style.transition = "all 0.25s ease";
        });
    });

});


/* =========================
   5. 이미지 저장 (html2canvas)
========================= */
function saveAsImage() {
    const target = document.querySelector(".result-container");

    html2canvas(target, {
        scale: 2, // 고해상도
        useCORS: true
    }).then(canvas => {
        const link = document.createElement("a");
        link.download = "health-report.png";
        link.href = canvas.toDataURL();
        link.click();
    });
}

function saveAsImage() {
    // 1. 실제 존재하는 컨테이너 클래스명으로 변경
    const container = document.querySelector('.result-container');

    if (!container) {
        console.error("저장할 컨테이너(.result-container)를 찾을 수 없습니다.");
        return;
    }

    // 2. 버튼이 사진에 같이 찍히지 않도록 잠시 숨김
    const saveBtn = document.querySelector('.btn-save');
    if (saveBtn) saveBtn.style.display = 'none';

    // 3. ⭐ 카드 디자인(그림자 등)이 잘 캡처되도록 임시 스타일 적용 ⭐
    // html2canvas가 둥근 모서리와 그림자를 더 잘 인식하게 도와줍니다.
    container.style.borderRadius = "20px"; // 카드 테두리 둥글게
    container.style.overflow = "hidden"; // 카드 내부 요소가 넘치지 않도록
    container.style.boxShadow = "0 10px 20px rgba(0,0,0,0.1)"; // 카드 그림자 강제 적용 (캡처용)

    html2canvas(container, {
        useCORS: true,      // 이미지(그래프 등)가 뜰 수 있도록 허용
        allowTaint: false,  // true일 경우 보안 이슈로 데이터 추출이 안 될 수 있음
        // scale: 2,        // (선택) 고화질을 원하면 주석 해제 (캡처 속도는 느려짐)
        logging: true       // 개발자 도구(F12)에서 진행 상황 확인 가능
    }).then(canvas => {
        // 4. ⭐ 캡처 후 임시 스타일 원상복구 ⭐
        container.style.borderRadius = "";
        container.style.overflow = "";
        container.style.boxShadow = "";

        const link = document.createElement('a');
        link.download = '건강_분석_리포트.png';
        link.href = canvas.toDataURL('image/png');
        link.click();

        // 5. 버튼 다시 보이게 복구
        if (saveBtn) saveBtn.style.display = 'block';
    }).catch(err => {
        // 오류 발생 시에도 스타일 원상복구 및 버튼 복구
        container.style.borderRadius = "";
        container.style.overflow = "";
        container.style.boxShadow = "";
        console.error("이미지 저장 중 오류 발생:", err);
        if (saveBtn) saveBtn.style.display = 'block';
    });
}