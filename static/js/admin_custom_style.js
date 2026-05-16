document.addEventListener("DOMContentLoaded", function () {
    const checkbox = document.querySelector("#id_is_sponsored");
    const nameRow = document.querySelector(".field-sponsor_name");
    const expiryRow = document.querySelector(".field-expires_at");

    if (!checkbox || !nameRow || !expiryRow) return;

    const rows = [nameRow, expiryRow];

    // Setup initial transition styles
    rows.forEach(row => {
        row.style.transition = "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
        row.style.overflow = "hidden";
    });

    function toggleSponsoredFields(isInit = false) {
        if (checkbox.checked) {
            rows.forEach(row => {
                row.style.display = "flex"; 
                // Small delay to allow the browser to register display: flex
                setTimeout(() => {
                    row.style.opacity = "1";
                    row.style.maxHeight = "100px"; // Large enough to fit the row
                    row.style.marginTop = "1rem";  // Restore original spacing
                    row.style.transform = "translateY(0)";
                }, 10);
            });
        } else {
            rows.forEach(row => {
                row.style.opacity = "0";
                row.style.maxHeight = "0";
                row.style.marginTop = "0";
                row.style.transform = "translateY(-10px)";
                
                // Only hide the display after the animation finishes
                if (!isInit) {
                    setTimeout(() => {
                        if (!checkbox.checked) row.style.display = "none";
                    }, 400); 
                } else {
                    row.style.display = "none";
                }
            });
        }
    }

    // Set initial state
    toggleSponsoredFields(true);

    checkbox.addEventListener("change", () => toggleSponsoredFields(false));
});