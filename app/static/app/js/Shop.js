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

    // Handle filter dropdowns
    const headings = document.querySelectorAll('.hero .section1 .drop-filter-list .heading');

    headings.forEach(heading => {
        heading.addEventListener('click', function () {
            const filterList = this.nextElementSibling;

            // Toggle filter list display
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

    // Handle category filter buttons
    const categoryButtons = document.querySelectorAll('.filter-item-list-item[data-category]');
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            window.location.href = `?category=${category}`;
        });
    });
});

// Load more functionality
let page = 1;
function LoadMore() {
    page++;
    fetch(`?page=${page}`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newProducts = doc.querySelectorAll('.product-list .card');
            const productList = document.querySelector('.product-list');

            // Insert new products before the Load More button
            const loadMoreButton = document.querySelector('.button-container');
            newProducts.forEach(product => {
                productList.insertBefore(product, loadMoreButton);
            });

            // Hide Load More button if no more products
            if (newProducts.length === 0) {
                loadMoreButton.style.display = 'none';
            }
        });
}