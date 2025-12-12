"use strict";

document.addEventListener("DOMContentLoaded", function () {
    const selectA = document.getElementById("user_a");
    const selectB = document.getElementById("user_b");

    function updateOptions() {
        const selectedA = selectA.value;
        const selectedB = selectB.value;

        [...selectA.options].forEach(opt => opt.disabled = false);
        [...selectB.options].forEach(opt => opt.disabled = false);

        if (selectedA) {
            const optB = selectB.querySelector(`option[value="${selectedA}"]`);
            if (optB) optB.disabled = true;
        }

        if (selectedB) {
            const optA = selectA.querySelector(`option[value="${selectedB}"]`);
            if (optA) optA.disabled = true;
        }
    }

    selectA.addEventListener("change", updateOptions);
    selectB.addEventListener("change", updateOptions);
});
