document.addEventListener("DOMContentLoaded", function () {
  createSlider("#section2");
  createSlider("#section3");
  createSlider("#section5");

  function createSlider(sectionClass) {
    const section = document.querySelector(sectionClass);
    const cardList = section.querySelector(".slider-wrapper");
    const prevBtn = cardList.querySelector(".prev-btn");
    const nextBtn = cardList.querySelector(".next-btn");
    const cards = section.querySelector(".slider-wrapper .slider-wrapper-item");
    const scrollOffset = 300;
    cards.style.scrollBehavior = "smooth";

    let isScrolling = false; // Biến để kiểm tra xem cuộn có đang diễn ra hay không

    cardList.addEventListener("wheel", (evt) => {
      evt.preventDefault();

      if (!isScrolling) {
        // Nếu không đang cuộn
        isScrolling = true; // Đặt cờ là đang cuộn
        cards.scrollLeft += evt.deltaY * 5;

        // Sau một khoảng thời gian, đặt lại cờ là không cuộn
        setTimeout(() => {
          isScrolling = false;
        }, 400);
      }
    });
    nextBtn.addEventListener("click", () => {
      cards.scrollLeft += scrollOffset;
      if (cards.scrollLeft + cards.clientWidth >= cards.scrollWidth) {
        cards.scrollLeft = 0;
      }
    });

    prevBtn.addEventListener("click", () => {
      cards.scrollLeft -= scrollOffset;
      if (cards.scrollLeft <= 0) {
        cards.scrollLeft = cards.scrollWidth - cards.clientWidth;
      }
    });
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const slider = document.querySelector("body .slider");
  const slides = slider.querySelectorAll("p");

  let index = 0;

  function showSlide() {
    slides.forEach((slide) => slide.classList.remove("active"));
    slides[index].classList.add("active");
  }

  function nextSlide() {
    slides[index].classList.remove("active");
    index = (index + 1) % slides.length;
    slides[index].classList.add("active");
  }

  setInterval(nextSlide, 6000);
});

// book of week
document.addEventListener("DOMContentLoaded", function () {
  var links = document.querySelectorAll("#section4 .wrapper .links a");
  var tab = document.querySelectorAll(
    "#section4 .wrapper .tab-contents .tab-content "
  );

  links.forEach(function (link, index) {
    link.addEventListener("click", function () {
      var items = tab[index].querySelectorAll(
        ".top-rank-wrapper .top-rank .item"
      );
      var content = tab[index].querySelectorAll(
        "#section4 .wrapper .tab-contents .tab-content .top-rank-wrapper .top-rank-content .item"
      );

      links.forEach(function (link) {
        link.classList.remove("active");
      });
      content.forEach(function (contentItem) {
        contentItem.classList.remove("active");
      });
      items.forEach(function (item) {
        item.classList.remove("active");
      });
      tab.forEach(function (item) {
        item.classList.remove("active");
      });

      this.classList.add("active");
      tab[index].classList.add("active");
      items[0].classList.add("active");
      content[0].classList.add("active");

      items.forEach(function (item, index) {
        item.addEventListener("mouseover", function () {
          items.forEach(function (item) {
            item.classList.remove("active");
          });
          content.forEach(function (item) {
            item.classList.remove("active");
          });

          this.classList.add("active");
          content[index].classList.add("active");
        });
      });
    });
  });
});


// Navigation icon
document.addEventListener("DOMContentLoaded", function () {
  active(
    ".navigation-bar .icons .user-icon",
    ".navigation-bar .icons .drop-down-menu"
  );

  function active(btnSelector, activeItemSelector) {
    const btn = document.querySelector(btnSelector);
    const section = document.querySelector(activeItemSelector);

    btn.addEventListener("click", () => {
      if (section.style.display === "none" || section.style.display === "") {
        section.style.display = "flex";
      } else {
        section.style.display = "none";
      }
    });
  }
});