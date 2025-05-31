document.addEventListener('DOMContentLoaded', function () {
    active('.navigation-bar .icons .user-icon', '.navigation-bar .icons .drop-down-menu');

    function active(btnSelector, activeItemSelector) {
        const btn = document.querySelector(btnSelector);
        const section = document.querySelector(activeItemSelector);

        btn.addEventListener('click', () => {
            if (section.style.display === "none" || section.style.display === "") {
                section.style.display = "flex";
            } else {
                section.style.display = "none";
            }
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const headings = document.querySelectorAll('.hero .section1 .drop-filter-list .heading');

    headings.forEach(heading => {
        heading.addEventListener('click', function () {
            const filterList = this.nextElementSibling;

            // Kiểm tra và thay đổi trạng thái hiển thị của filter list
            if (filterList.style.display === "none" || filterList.style.display === "") {
                filterList.style.display = "flex";
                this.querySelector('i').classList.remove('ri-arrow-drop-right-line');
                this.querySelector('i').classList.add('ri-arrow-drop-down-line');
            } else {
                filterList.style.display = "none";
                this.querySelector('i').classList.remove('ri-arrow-drop-down-line');
                this.querySelector('i').classList.add('ri-arrow-drop-right-line');
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.hero .section1 .drop-filter-list .filter-item-list-item');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            if(button.classList.contains('active')){
                button.classList.remove('active');
            } else{
                button.classList.add('active');
            }
        });
    });
});