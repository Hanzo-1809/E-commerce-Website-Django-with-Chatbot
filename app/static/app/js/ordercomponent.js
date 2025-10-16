document.addEventListener("DOMContentLoaded", function () {
  // Load data
  const items = document.querySelectorAll(
    "main .hero .list-items .item:not(.heading)"
  );

  // Function to calculate totals
  function caltotal() {
    const subtotal = document.querySelector(
      ".popup .order-form .payments .subtotal label:nth-child(2)"
    );
    const vat = document.querySelector(
      ".popup .order-form .payments .VAT label:nth-child(2)"
    );
    const total = document.querySelector(
      ".popup .order-form .payments .total label:nth-child(2)"
    );

    let subtotalCost = 0;
    document
      .querySelectorAll(".popup .order-form .list-items .item .cost")
      .forEach((cost) => {
        subtotalCost += parseFloat(
          cost.textContent.replace("$", "").replace(/\./g, "").trim()
        );
      });

    const vatcost = subtotalCost * 0.1;
    const totalCost = subtotalCost + vatcost;

    subtotal.textContent = subtotalCost.toLocaleString("vi-VN") + " $";
    vat.textContent = vatcost.toLocaleString("vi-VN") + " $";
    total.textContent = totalCost.toLocaleString("vi-VN") + " $";
  }

  // Function to handle the cancel button event
  function addCancelEvent() {
    const cancelBtn = document.querySelector(
      ".popup .order-form .submit button[id='cancel']"
    );
    const orderform = document.querySelector(".popup");
    if (cancelBtn && orderform) {
      cancelBtn.addEventListener("click", () => {
        orderform.classList.remove("active");
        cancelBtn.addEventListener("click", closePopup);
      });
    }
  }

  // Event listener for buttons to show popup and add items
  document
    .querySelectorAll("main .hero .details .buy-btn button")
    .forEach((button) => {
      button.addEventListener("click", () => {
        const popup = document.querySelector(".popup");
        popup.classList.add("active");
        document.body.style.overflow = 'hidden';

        // Clear existing items in the order summary
        const listItem = document.querySelector(
          ".popup .order-form .list-items"
        );
        listItem.innerHTML = "";

        // Add new items to order summary
        items.forEach((item) => {
          const checkbox = item.querySelector('.tmp input[type="checkbox"]');
          if (checkbox.checked) {
            const imgSrc = item.querySelector(".book-img img").src;
            const name = item.querySelector(".details .book-name").textContent;
            const amount = parseInt(item.querySelector(".book-amount .amount").textContent);
            const cost = parseFloat(item.querySelector(".book-price").textContent.replace("$", "").replace(/,/g, '').trim());
            const newItem = document.createElement("div");
            newItem.classList.add("item");
            const totalCost = cost * amount;
            newItem.innerHTML = `
            <div class="image"><img src="${imgSrc}" alt="" srcset=""></div>
            <div class="details">
                <div class="name">${name}</div>
                <div class="amount">x${amount}</div>
            </div>
            <div class="cost">${totalCost.toLocaleString("vi-VN")} $</div>
          `;

            listItem.appendChild(newItem);
          }
        });

        // Calculate totals after adding items
        caltotal();
        // Ensure the cancel event is added when the popup is active
        addCancelEvent();
      });
    });

  // Edit button functionality
  const editbtn = document.querySelector(".popup .order-form .subheading i");
  const editform = document.querySelector(".popup .order-form .user-info");
  if (editbtn && editform) {
    editbtn.addEventListener("click", function () {
      if (!editform.classList.contains("active")) {
        editform.classList.add("active");
        editbtn.classList.remove("ri-edit-fill");
        editbtn.classList.add("ri-check-line");
        editbtn.style.color = "green";
        const checkIcon = document.createElement("i");
        checkIcon.classList.add("ri-close-circle-line");
        editbtn.parentNode.insertBefore(checkIcon, editbtn.nextSibling);

        editform
          .querySelectorAll(".input-box label:nth-child(2)")
          .forEach((label) => {
            const input = document.createElement("input");
            input.type =
              label.getAttribute("for") === "user-phone" ||
                label.getAttribute("for") === "zipcode"
                ? "number"
                : "text";
            input.name = label.getAttribute("for");
            input.placeholder = label.textContent;
            label.parentNode.replaceChild(input, label);
          });

        checkIcon.addEventListener("click", () => {
          editform.querySelectorAll(".input-box input").forEach((input) => {
            const label = document.createElement("label");
            label.htmlFor = input.getAttribute("name");
            label.textContent = input.placeholder;
            input.parentNode.replaceChild(label, input);
          });
          checkIcon.remove();
          editbtn.classList.replace("ri-check-line", "ri-edit-fill");
          editbtn.style.color = "var(--color1)";
          editform.classList.remove("active");
        });
      } else {
        editform.querySelectorAll(".input-box input").forEach((input) => {
          const label = document.createElement("label");
          label.htmlFor = input.getAttribute("name");
          label.textContent = input.value !== "" ? input.value : input.placeholder;
          input.parentNode.replaceChild(label, input);
        });
        const closeIcon = editbtn.parentNode.querySelector(
          ".ri-close-circle-line"
        );
        if (closeIcon) {
          closeIcon.remove();
        }
        editbtn.classList.replace("ri-check-line", "ri-edit-fill");
        editbtn.style.color = "var(--color1)";
        editform.classList.remove("active");
      }
    });
  }
  function closePopup() {
    const popup = document.querySelector(".popup");
    popup.classList.remove("active");

    document.body.style.overflow = 'auto';
  }

  // Cancel button event
  const cancelBtn = document.querySelector(".popup .order-form .submit button[id='cancel']");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", closePopup);
  }
});
