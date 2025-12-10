"use strict"

document.addEventListener("DOMContentLoaded", function () {
    const infoModalEl = document.getElementById("infoModal");
    const infoModal = new bootstrap.Modal(infoModalEl);
    infoModal.show();

    infoModalEl.addEventListener("hidden.bs.modal", function () {
        window.location.href = "/home";
    });
});
