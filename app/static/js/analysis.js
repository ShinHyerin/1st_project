/**
 * 군집별 평균 데이터 프리셋
 */
const presets = {
    0: {
        height: 162.5, weight: 51.2, high_active: 0, mid_active: 5,
        sitting: 620, energy: 1550, fat: 32, na: 2600, sugar: 42, ldl: 108, hdl: 58
    },
    1: {
        height: 174.2, weight: 71.5, high_active: 45, mid_active: 55,
        sitting: 320, energy: 2450, fat: 52, na: 3400, sugar: 48, ldl: 95, hdl: 68
    },
    2: {
        height: 169.8, weight: 84.7, high_active: 5, mid_active: 10,
        sitting: 550, energy: 2750, fat: 82, na: 4700, sugar: 78, ldl: 162, hdl: 38
    }
};

/**
 * 버튼 클릭 시 해당 군집의 데이터를 입력 필드에 자동 주입
 * @param {number} id - 군집 번호 (0, 1, 2)
 */
function setPreset(id) {
    const data = presets[id];

    if (!data) return;

    // 객체의 키(height, weight 등)를 순회하며 해당 ID를 가진 input의 value를 변경
    for (const key in data) {
        const input = document.getElementById(key);
        if (input) {
            input.value = data[key];

            // 시각적 피드백을 위해 값이 바뀐 필드에 일시적인 강조 효과를 줄 수도 있습니다.
            input.style.transition = 'background-color 0.5s';
            input.style.backgroundColor = '#f0f7ff';
            setTimeout(() => {
                input.style.backgroundColor = 'white';
            }, 500);
        }
    }

    console.log(`Cluster ${id} preset loaded.`);
}

document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".input-card");

    cards.forEach((card, i) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";

        setTimeout(() => {
            card.style.transition = "all 0.6s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, i * 120);
    });
});