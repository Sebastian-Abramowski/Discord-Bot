// Set current year
const yearEl = document.querySelector(".year");
const currentYear = new Date().getFullYear();
yearEl.textContent = currentYear;

// Adjust widths of buttons inside .bot-box (based on the first one)
const firstBotBox = document.querySelector(".bot-box");
const buttonsInBotBox = firstBotBox.querySelectorAll(".btn-custom");

let maxWidth = 0;
buttonsInBotBox.forEach(function (button) {
  buttonWidth = button.offsetWidth;
  if (buttonWidth > maxWidth) {
    maxWidth = buttonWidth;
  }
});

const allBotBoxes = document.querySelectorAll(".bot-box");
allBotBoxes.forEach(function (botBox) {
  const allButtons = botBox.querySelectorAll(".btn-custom");
  allButtons.forEach(function (button) {
    button.style.width = maxWidth + "px";
  });
});
