document.addEventListener('DOMContentLoaded', function() {
    const rowsPerPage = 10;
    const table = document.getElementById('historyTable');
    if(!table) return;

    const rows = Array.from(table.getElementsByClassName('history-row'));
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const pageNumbers = document.getElementById('pageNumbers');

    let currentPage = 1;
    const pageCount = Math.ceil(rows.length / rowsPerPage);

    function displayRows(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });

        updatePagination();
    }

    function updatePagination() {
        pageNumbers.innerHTML = '';
        for (let i = 1; i <= pageCount; i++) {
            const span = document.createElement('span');
            span.textContent = i;
            span.className = 'page-num' + (i === currentPage ? ' active' : '');
            span.onclick = () => {
                currentPage = i;
                displayRows(currentPage);
            };
            pageNumbers.appendChild(span);
        }

        document.getElementById('prevPage').disabled = (currentPage === 1);
        document.getElementById('nextPage').disabled = (currentPage === pageCount);
    }

    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayRows(currentPage);
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        if (currentPage < pageCount) {
            currentPage++;
            displayRows(currentPage);
        }
    });

    // 초기 실행 (데이터가 10개 이하일 때 페이지네이션 숨김 처리 가능)
    if (rows.length <= rowsPerPage) {
        document.getElementById('pagination').style.display = 'none';
    } else {
        displayRows(currentPage);
    }
});