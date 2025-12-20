"use strict";

document.addEventListener("DOMContentLoaded", function() {
    const body = document.body;
    const today = new Date();
    const month = today.getMonth(); // 0 = January, 11 = December
    const day = today.getDate();

    // Christmas season: December 1-31 OR January 1-5
    if ((month === 11 && day >= 1 && day <= 31) || (month === 0 && day >= 1 && day <= 5)) {
        body.classList.add("christmas");

        const container = document.createElement("div");
        container.classList.add("containter");

        const sizes = ["little", "normal", "big", "giant"];
        sizes.forEach(size => {
            const snowDiv = document.createElement("div");
            snowDiv.classList.add("snow", size);
            container.appendChild(snowDiv);
        });

        body.appendChild(container);

    } else {
        body.classList.remove("christmas");
    }

    // Special case: January 4th
    if (month === 1 && day === 4) {
        body.classList.add("amalia");
    } else {
        body.classList.remove("amalia");
    }
});
