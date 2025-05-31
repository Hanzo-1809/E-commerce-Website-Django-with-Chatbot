document.addEventListener("DOMContentLoaded", () => {
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

		if (section) {
			section
				.querySelector(".drop-list-item.profile")
				.addEventListener("click", () => {
					document.querySelector(".profilePopup").classList.add("active");
					document.querySelector("body").style.height = "100vh";
					document.querySelector("body").style.overflow = "hidden";
				});
		}
	}


	// swap content-box
	var profileBtns = document.querySelectorAll(
		".profilePopup .contentBox .nav-aside .profile-btn"
	);
	var contentBoxes = document.querySelectorAll(
		".profilePopup .contentBox .content-aside"
	);

	profileBtns.forEach((btn, index) => {
		btn.addEventListener("click", () => {
			profileBtns.forEach((profileBtn) =>
				profileBtn.classList.remove("active")
			);
			contentBoxes.forEach((contentBox) =>
				contentBox.classList.remove("active")
			);

			// Add the active class to the corresponding content box
			btn.classList.add("active");
			if (contentBoxes[index]) {
				contentBoxes[index].classList.add("active");
			}
		});
	});
	function disableInput() {
		// disable all input in profile show
		var inputs = document.querySelectorAll(
			".profilePopup .contentBox .content-aside .info-box input"
		);
		var imgBtn = document.querySelector(
			".profilePopup .contentBox .aside-section .content-aside .info-box.box-img button"
		);
		inputs.forEach((input) => {
			input.disabled = true;
		});
		imgBtn.style.display = "none";
		var submitBtn = document.querySelector(
			".profilePopup .contentBox .content-aside .submitBtn"
		);
		submitBtn.style.display = "none";
	}
	function enableInput() {
		// disable all input in profile show
		var inputs = document.querySelectorAll(
			".profilePopup .contentBox .content-aside .info-box input"
		);
		inputs.forEach((input) => {
			input.disabled = false;
		});
		var imgBtn = document.querySelector(
			".profilePopup .contentBox .aside-section .content-aside .info-box.box-img button"
		);
		imgBtn.style.display = "block";
		var submitBtn = document.querySelector(
			".profilePopup .contentBox .content-aside .submitBtn"
		);
		submitBtn.style.display = "flex";

		const oldImg = document.querySelector(
			".profilePopup .contentBox .aside-section .content-aside .info-box.box-img img"
		).src;
		var imgUp = document.querySelector(".profilePopup .contentBox .aside-section .content-aside .info-box.box-img button").addEventListener("click", async () => {
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
				var img = document.querySelector(
					".profilePopup .contentBox .aside-section .content-aside .info-box.box-img img"
				);
				img.src = URL.createObjectURL(file);
			} catch (error) {
				console.error("Error opening file:", error);
			}
		});

		var cancelBtn = document
			.querySelector(
				'.profilePopup .contentBox .content-aside .submitBtn button[type="reset"]'
			)
			.addEventListener("click", () => {
				document.querySelector(
					".profilePopup .contentBox .aside-section .content-aside .info-box.box-img img"
				).src = oldImg;
			});
	}

	var editbtn = document.querySelector(
		".profilePopup .contentBox .aside-section .content-aside i"
	);
	editbtn.addEventListener("click", () => {
		enableInput();
	});
	var cancelEdit = document.querySelector(
		'.profilePopup .contentBox .content-aside .submitBtn button[type="reset"]'
	);
	cancelEdit.addEventListener("click", () => {
		disableInput();
	});

	document
		.querySelector(
			".profilePopup .contentBox .heading .content-aside-heading i"
		)
		.addEventListener("click", () => {
			document.querySelector(".profilePopup").classList.remove("active");
			document.querySelector("body").style.height = "auto";
			document.querySelector("body").style.overflow = "auto";
		});
	document
		.querySelector(
			".profilePopup .contentBox .content-aside .item .head .cell .view-order"
		)
		.addEventListener("click", () => {
			document
				.querySelector(
					".profilePopup .contentBox .content-aside .item .popupOrder"
				)
				.classList.add("active");
		});
	document
		.querySelector(
			".profilePopup .contentBox .content-aside .item .popupOrder .order-form .subheading i"
		)
		.addEventListener("click", () => {
			document
				.querySelector(
					".profilePopup .contentBox .content-aside .item .popupOrder"
				)
				.classList.remove("active");
		});

	// FEEDBACK POPUP

	document
		.querySelector(
			".profilePopup .contentBox .content-aside .item .head .cell .write-review"
		)
		.addEventListener("click", () => {
			document.querySelector(".popupFeedback").classList.add("active");
			document.body.style.overflow = "hidden"; // Prevent scrolling when the popup is active
		});

	function closepopupFeedback() {
		const popupFeedback = document.querySelector(".popupFeedback");
		popupFeedback.classList.remove("active");
		document.body.style.overflow = "auto";
	}

	function activeRate() {
		const rateBtns = document.querySelectorAll(
			".popupFeedback .feedback-form .input-box .list-item"
		);

		rateBtns.forEach((listItem) => {
			const rateElements = listItem.querySelectorAll(".rate");

			rateElements.forEach((btn) => {
				btn.addEventListener("click", () => {
					rateElements.forEach((rateBtn) => {
						rateBtn.classList.remove("active");
					});
					btn.classList.add("active");
				});
			});
		});
	}

	// Cancel button event
	const cancelBtn = document.querySelector(".popupFeedback .feedback-form i");
	if (cancelBtn) {
		cancelBtn.addEventListener("click", closepopupFeedback);
	}
	activeRate();
	disableInput();
});