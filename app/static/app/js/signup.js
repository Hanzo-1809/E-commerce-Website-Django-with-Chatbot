document.addEventListener("DOMContentLoaded", () => {
    var elements = document.getElementsByClassName("password");
    
    Array.from(elements).forEach(e => {
        var passwordInput = e.getElementsByTagName("input")[0];
        var eye = e.getElementsByTagName("i")[0];
        eye.addEventListener("click", () => {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                eye.classList.value = "ri-eye-line";
            } else {
                passwordInput.type = "password";
                eye.classList.value = "ri-eye-off-line";
            }
        });
    });

    var password = document.getElementById("password");
    var confirmPassword = document.getElementById("confirmPassword");
    var form = document.querySelector(".signupForm");
    var submitButton = form.querySelector("button[type='submit']");
    var termOfUse = document.getElementById("TermOfUse");

    function checkPasswordMatch() {
        if(confirmPassword.value !== ""){
            if (password.value !== confirmPassword.value) {
                confirmPassword.parentNode.classList.add("error");
            } else {
                confirmPassword.parentNode.classList.remove("error");
            }
        }
    }

    function validateForm() {
        var emailInput = form.querySelector("input[name='email']");
        var email = emailInput.value;
        var passwordValue = password.value;
        var confirmPasswordValue = confirmPassword.value;
        var isFormValid =
            email.trim() !== "" &&
            passwordValue.trim() !== "" &&
            confirmPasswordValue.trim() !== "" &&
            termOfUse.checked;

        submitButton.disabled = !isFormValid;
        if (submitButton.disabled) {
            submitButton.style.pointerEvents = "none";
            submitButton.style.backgroundColor = "gray";
        } else {
            submitButton.style.pointerEvents = "auto";
            submitButton.style.backgroundColor = "";
        }
    }

    password.addEventListener("input", checkPasswordMatch);
    confirmPassword.addEventListener("input", checkPasswordMatch);
    form.addEventListener("input", validateForm);
    termOfUse.addEventListener("change", validateForm);

    form.addEventListener("submit", function (event) {
        if (password.value.length < 8) {
            event.preventDefault();
            alert("Password must be at least 8 characters long.");
        }
    });

    // Initial validation
    validateForm();
});