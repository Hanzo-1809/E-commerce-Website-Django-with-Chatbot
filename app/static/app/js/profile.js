document.addEventListener("DOMContentLoaded", function () {
  initialSection();
  popupDisplay();

  function initialSection() {
    const sectionBar = document.querySelector("main .sectionbar");
    const sectionActiveItem = sectionBar.querySelectorAll(".sec");
    const sectionContent = document.querySelector("main .section-content");
    const sectionContentItem = sectionContent.querySelectorAll(".sec");
    const inputSection = document.querySelectorAll(
      "main .section-content .sec .info-box input"
    );
    const buttonSection = document.querySelector(
      "main .section-content .sec .submitBtn"
    );
    const displayImage = document.querySelector("main .heading .back2 img");
    const chooseImage = document.querySelector("main .heading .back2 button");

    // Active sectionbar
    sectionActiveItem.forEach((item, index) => {
      item.addEventListener("click", () => {
        // Remove 'active' class from all items in sectionActiveItem
        sectionActiveItem.forEach((activeItem) => {
          activeItem.classList.remove("active");
        });

        // Add 'active' class to the clicked item
        item.classList.add("active");

        // Remove 'active' class from all items in sectionContentItem
        sectionContentItem.forEach((contentItem) => {
          contentItem.classList.remove("active");
        });

        // Add 'active' class to the corresponding item in sectionContentItem
        sectionContentItem[index].classList.add("active");
        if (index == 1) {
          sectionBar.querySelector(".ri-edit-box-fill").style.display = "none";
        } else {
          sectionBar.querySelector(".ri-edit-box-fill").style.display =
            "inherit";
        }
      });
    });
    chooseImage.addEventListener("click", async () => {
      try {
        const [fileHandle] = await window.showOpenFilePicker({
          types: [
            {
              description: "Image files",
              accept: {
                "image/*": [".png", ".gif", ".jpeg", ".jpg", ".bmp"],
              },
            },
          ],
          multiple: false,
        });
        const file = await fileHandle.getFile();
        displayImage.src = URL.createObjectURL(file);
      } catch (error) {
        console.error("Error opening file:", error);
      }
    });

    inputSection.forEach((item) => {
      item.disabled = true;
    });
    buttonSection.style.display = "none";
    chooseImage.style.display = "none";

    sectionBar
      .querySelector(".ri-edit-box-fill")
      .addEventListener("click", () => {
        inputSection.forEach((item) => {
          item.disabled = false;
        });
        buttonSection.style.display = "flex";
        chooseImage.style.display = "inherit";
      });

    // On input changes
    const displayName = document.querySelector("main .heading .user .username");
    const defaultImg = displayImage.src;
    const lastNameInput = document.querySelector(
      'main .section-content .sec .info-box input[name="lastName"]'
    );
    const firstNameInput = document.querySelector(
      'main .section-content .sec .info-box input[name="firstName"]'
    );

    inputSection.forEach((item) => {
      item.addEventListener("input", updateDisplayName);
    });

    // Function to update display name
    function updateDisplayName() {
      displayName.innerText = lastNameInput.value + " " + firstNameInput.value;
    }

    // On Cancel and Reset button click
    const cancelButton = buttonSection.querySelector('button[type="reset"]');
    cancelButton.addEventListener("click", () => {
      // Reset last name and first name inputs
      lastNameInput.value = lastNameInput.defaultValue;
      firstNameInput.value = firstNameInput.defaultValue;
      displayImage.src = defaultImg;
      // Update display name
      updateDisplayName();
      inputSection.forEach((item) => {
        item.disabled = true;
      });
      buttonSection.style.display = "none";
      chooseImage.style.display = "none";
    });
  }
  function popupDisplay() {
    const sectionContent = document.querySelector("main .section-content");
  
    // Event delegation for view order buttons
    sectionContent.addEventListener("click", function(event) {
      const target = event.target;
      if (target.classList.contains("view-order")) {
        const popupOrder = target.closest(".item").querySelector(".popupOrder");
        if (popupOrder) {
          popupOrder.classList.add("active");
          const closeBtn = popupOrder.querySelector(".order-form .subheading i");
          closeBtn.addEventListener("click", function() {
            popupOrder.classList.remove("active");
          });
        }
      }
    });
  
    // Event delegation for view review buttons
    sectionContent.addEventListener("click", function(event) {
      const target = event.target;
      if (target.classList.contains("write-review")) {
        const popupReview = target.closest(".item").querySelector(".popupFeedback");
        if (popupReview) {
          popupReview.classList.add("active");
          const closeBtn = popupReview.querySelector(".feedback-form i");
          closeBtn.addEventListener("click", function() {
            popupReview.classList.remove("active");
          });
  
          // RATE BUTTONS
          const rateBtns = popupReview.querySelectorAll(".feedback-form .input-box .list-item .rate");
  
          rateBtns.forEach((btn) => {
            btn.addEventListener("click", () => {
              const listItem = btn.closest(".list-item");
              listItem.querySelectorAll(".rate").forEach((rateBtn) => {
                rateBtn.classList.remove("active");
              });
              btn.classList.add("active");
            });
          });
        }
      }
    });
  }
});
