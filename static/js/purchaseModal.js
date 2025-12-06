"use strict"

document.addEventListener("DOMContentLoaded", function () {
	const modal = new bootstrap.Modal(
		document.getElementById("purchaseFeedbackModal")
	);
	const body = document.getElementById("feedbackModalBody");
	const title = document.getElementById("feedbackModalLabel");
	const header = document.querySelector(
		"#purchaseFeedbackModal .modal-header"
	);

	if (document.getElementById("purchaseContent")) {
		body.innerHTML = document.getElementById("purchaseContent").innerHTML;
		title.textContent = "Compra exitosa";

		header.classList.remove("bg-danger", "text-white");
		header.classList.add("bg-success", "text-white");

		modal.show();
	} else if (document.getElementById("errorContent")) {
		body.innerHTML = document.getElementById("errorContent").innerHTML;
		title.textContent = "Error en la compra";

		header.classList.remove("bg-success", "text-white");
		header.classList.add("bg-danger", "text-white");

		modal.show();
	}
});
