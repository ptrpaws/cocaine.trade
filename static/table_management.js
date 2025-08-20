'use strict';
document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".hide-column");
  checkboxes.forEach(checkbox => {
    const column = checkbox.dataset.column;
    const savedValue = localStorage.getItem("column_" + column);

    if (savedValue !== null) {
      checkbox.checked = savedValue === "true";
    } else {
      checkbox.checked = false;
    }

    checkbox.addEventListener("change", function () {
      localStorage.setItem("column_" + column, checkbox.checked);
      const trs = document.querySelectorAll("#firmwareTable tr");
      trs.forEach(tr => {
        let td = tr.children[column];
        if (td) td.style.display = checkbox.checked ? "" : "none";
      });
    });

    const event = new Event('change');
    checkbox.dispatchEvent(event);
  });
});