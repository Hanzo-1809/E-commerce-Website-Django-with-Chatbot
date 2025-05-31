var ele = document.getElementsByClassName("password");
var passwordInput = ele[0].getElementsByTagName("input")[0];
var eye = ele[0].getElementsByTagName("i")[0];

eye.addEventListener("click", () => {
    if (passwordInput.type === "password") {
        passwordInput.type = 'text';
        eye.classList.value = "ri-eye-line";
    } else {
        passwordInput.type = 'password';
        eye.classList.value = "ri-eye-off-line";
    }
});