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

document.addEventListener("DOMContentLoaded", function () {
  let updateBtns = document.querySelectorAll(".update-cart");

  updateBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      let productId = this.dataset.product;
      let action = this.dataset.action;
      console.log("Product ID:", productId, "Action:", action);

      updateUserOrder(productId, action);
    });
  });

  function updateUserOrder(productId, action) {
    let url = "/update_item/";

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"), // CSRF Token để bảo mật
      },
      body: JSON.stringify({ productId: productId, action: action }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Sản phẩm đã được thêm vào giỏ hàng:", data);
        alert("Sản phẩm đã được thêm vào giỏ hàng!");
        location.reload(); // Load lại trang để cập nhật giỏ hàng
      })
      .catch((error) => console.error("Lỗi:", error));
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      let cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

document.addEventListener("DOMContentLoaded", function () {
  createSlider(".image-section");

  function createSlider(sectionClass) {
    const section = document.querySelector(sectionClass);
    const imgList = section.querySelector(".img-list");
    const prevBtn = imgList.querySelector(".prev-btn");
    const nextBtn = imgList.querySelector(".next-btn");
    const display = section.querySelector(".img-show img");
    const imgs = imgList.querySelector(".list");
    const img = imgs.querySelectorAll("img");
    const scrollOffset = 300;
    imgs.style.scrollBehavior = "smooth";

    let currentIndex = 0; // Track the current index of the active image

    updateActiveImage();

    imgs.addEventListener("wheel", (evt) => {
      evt.preventDefault();
    });

    nextBtn.addEventListener("click", () => {
      currentIndex = (currentIndex + 1) % img.length;
      updateActiveImage();
      scrollToActiveImage();
    });

    prevBtn.addEventListener("click", () => {
      currentIndex = (currentIndex - 1 + img.length) % img.length;
      updateActiveImage();
      scrollToActiveImage();
    });

    img.forEach((image, index) => {
      image.addEventListener("click", () => {
        currentIndex = index;
        updateActiveImage();
        scrollToActiveImage();
      });
    });

    function updateActiveImage() {
      img.forEach((image, index) => {
        image.classList.remove("active");
        if (index === currentIndex) {
          image.classList.add("active");
          display.src = image.src;
        }
      });
    }

    function scrollToActiveImage() {
      if (currentIndex === 0) {
        imgs.scrollTop = 0;
      } else if (currentIndex === img.length - 1) {
        imgs.scrollTop = imgs.scrollHeight - imgs.clientHeight;
      } else {
        imgs.scrollTop = img[currentIndex].offsetTop - imgList.offsetTop;
      }
    }
  }
});

document.addEventListener("DOMContentLoaded", function () {
  changeAmount(
    "main .product .product-info .buy-info .input button",
    "main .product .product-info .buy-info .input .amount"
  );

  function changeAmount(btnSelector, amountSelector) {
    const btns = document.querySelectorAll(btnSelector);
    const amount = document.querySelector(amountSelector);

    btns.forEach(function(btn){
      btn.addEventListener("click",()=>{
        if(btn.classList.contains("minus")){
          var amountNum = parseInt(amount.textContent, 10);
          if(amountNum == 1) return;
          amountNum = amountNum - 1;
          amount.textContent = amountNum;
        } else {
          var amountNum = parseInt(amount.textContent, 10);
          amountNum = amountNum + 1;
          amount.textContent = amountNum;
        }
      })
    })    
  }
});