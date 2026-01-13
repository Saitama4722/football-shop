(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach((alert) => {
      setTimeout(() => {
        alert.classList.add("fade");
        alert.classList.remove("show");
      }, 4000);
    });
  });
})();
