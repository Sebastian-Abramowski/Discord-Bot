let inputContainer = document.querySelector(".input-container");
let button = inputContainer.querySelector(".copy-button");
button.addEventListener("click", function () {
  let input = inputContainer.querySelector(".input");
  input.setSelectionRange(0, 15);
  navigator.clipboard.writeText(input.value);

  button.classList.add("active");
  window.getSelection().removeAllRanges();
  setTimeout(function () {
    button.classList.remove("active");
  }, 2000);
});
