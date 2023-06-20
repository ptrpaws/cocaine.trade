'use strict';
function sortTable() {
    const table = document.getElementById("firmwareTable");
    if (!table) return;
    let switching = true, switchcount = 0, dir = "asc";

    while (switching) {
        switching = false;
        let rows = table.rows;

        for (let i = 1; i < (rows.length - 1); i++) {
            let x = parseInt(rows[i].getElementsByTagName("TD")[0].querySelector('.fw-link').innerHTML),
                y = parseInt(rows[i + 1].getElementsByTagName("TD")[0].querySelector('.fw-link').innerHTML);

            if ((dir === "asc" && x > y) ||
                (dir === "desc" && x < y)) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;
                break;
            }
        }

        if (!switching && switchcount === 0 && dir === "asc") {
            dir = "desc";
            switching = true;
        }
    }

    const ascArrow = document.getElementById("ascArrow"),
        descArrow = document.getElementById("descArrow");
    if (ascArrow) ascArrow.style.display = (dir === "asc") ? "" : "none";
    if (descArrow) descArrow.style.display = (dir === "desc") ? "" : "none";
}

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