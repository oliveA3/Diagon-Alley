"use strict";

document.addEventListener("DOMContentLoaded", function () {
	const modal = new bootstrap.Modal(
		document.getElementById("usageFeedbackModal")
	);
	const body = document.getElementById("feedbackModalBody");
	const title = document.getElementById("feedbackModalLabel");

	if (document.getElementById("usageContent")) {
		body.innerHTML = document.getElementById("usageContent").innerHTML;
		title.textContent = "Producto usado";

		modal.show();
	}
});
