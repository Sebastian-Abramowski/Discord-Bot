// Smooth scrolling animation
const allLinks = document.querySelectorAll("a:link");

allLinks.forEach(function (link) {
  link.addEventListener("click", function (e) {
    const href = link.getAttribute("href");
    if (href.startsWith("#")) {
      e.preventDefault();
      const href = link.getAttribute("href");

      // Scroll back to top
      if (href === "#") {
        window.scrollTo({
          top: 0,
          behavior: "smooth",
        });
      }
      // Scroll to other link
      else {
        const sectionEl = document.querySelector(href);
        sectionEl.scrollIntoView({
          behavior: "smooth",
        });
      }
      //Remove focus on some element
      setTimeout(function () {
        document.activeElement.blur();
      }, 1000);
    }
  });
});
