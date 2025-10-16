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

// Amount change
document.addEventListener("DOMContentLoaded", function () {
  const minusButtons = document.querySelectorAll(".minus");
  const plusButtons = document.querySelectorAll(".add");
  const amounts = document.querySelectorAll(".amount");

  minusButtons.forEach((btn, index) => {
    btn.addEventListener("click", () => {
      const currentAmount = parseInt(amounts[index].textContent, 10);
      if (currentAmount > 1) {
        amounts[index].textContent = currentAmount - 1;
      }
    });
  });

  plusButtons.forEach((btn, index) => {
    btn.addEventListener("click", () => {
      const currentAmount = parseInt(amounts[index].textContent, 10);
      amounts[index].textContent = currentAmount + 1;
    });
  });
});

// Delete btn
document.addEventListener("DOMContentLoaded", function () {
  const deleteButtons = document.querySelectorAll(".tmp1");

  deleteButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".item");
      if (item.classList.contains("heading")) return;
      item.remove();
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const mainCheckbox = document.querySelector(
    '.heading.item .tmp input[type="checkbox"]'
  );
  const itemCheckboxes = document.querySelectorAll(
    '.item .tmp input[type="checkbox"]'
  );

  mainCheckbox.addEventListener("change", function () {
    itemCheckboxes.forEach((checkbox) => {
      checkbox.checked = mainCheckbox.checked;
    });
  });
});

// order summary
document.addEventListener("DOMContentLoaded", function () {
  const updateOrderSummary = () => {
    const items = document.querySelectorAll("main .hero .list-items .item:not(.heading)");
    let totalItems = 0;
    const totalCost = Array.from(items).reduce((acc, item) => {
      const checkbox = item.querySelector('.tmp input[type="checkbox"]');
      if (checkbox.checked) {
        const amount = parseInt(item.querySelector(".amount").textContent, 10);
        totalItems += amount; // Update totalItems count
        const price = parseFloat(
          item.querySelector(".book-price").textContent.replace(/[^\d.-]/g, '')
        );
        return acc + amount * price;
      }
      return acc;
    }, 0);
    document.querySelector(".total-item .Total-num").textContent = totalItems;
    document.querySelector(".total-cost .cost").textContent =
      totalCost.toLocaleString("vi-VN") + " $";

    // Add new items to order summary
    const orderSummaryList = document.querySelector(".total-item");
    orderSummaryList.innerHTML =
      '<div class="heading"><div class="Total">Total Items:</div><div class="Total-num">' +
      totalItems +
      "</div></div>";
    items.forEach((item) => {
      const checkbox = item.querySelector('.tmp input[type="checkbox"]');
      if (checkbox.checked) {
        const bookName = item.querySelector(".book-name").textContent;
        const amount = item.querySelector(".amount").textContent;
        const newItem = document.createElement("div");
        newItem.classList.add("item");
        newItem.innerHTML =
          '<div class="book-name">' +
          bookName +
          '</div><div class="book-amount">' +
          amount +
          "</div>";
        orderSummaryList.appendChild(newItem);
      }
    });
  };

  // Update order summary on page load
  updateOrderSummary();

  // Update order summary when item is deleted
  document.querySelectorAll(".tmp1").forEach((button) => {
    button.addEventListener("click", () => {
      setTimeout(updateOrderSummary, 100); // Wait for the DOM to update
    });
  });

  // Update order summary when amounts are changed
  document.querySelectorAll(".minus, .add").forEach((button) => {
    button.addEventListener("click", () => {
      setTimeout(updateOrderSummary, 100); // Wait for the DOM to update
    });
  });

  document
    .querySelectorAll('.item .tmp input[type="checkbox"]')
    .forEach((checkbox) => {
      checkbox.addEventListener("click", () => {
        setTimeout(updateOrderSummary, 100); // Wait for the DOM to update
      });
    });

  // document.querySelectorAll("main .hero .details .buy-btn button").forEach((button) => {
  //   button.addEventListener('click', () => {
  //     var popup = document.querySelector(".popup");
  //     if (popup) {
  //       popup.classList.add("active");
  //     }
  //   });
  // });

});

