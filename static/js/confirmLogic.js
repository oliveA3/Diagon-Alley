"use strict"

document.addEventListener("DOMContentLoaded", function () {
	let pendingForm = null;

	window.showConfirm = function (button) {
		pendingForm = button.closest("form");

		const title = button.dataset.title;
		const message = button.dataset.message;

		document.getElementById("confirmModalLabel").textContent = title;
		document.getElementById("confirmMessage").textContent = message;

		const modal = new bootstrap.Modal(
			document.getElementById("confirmModal")
		);
		modal.show();
	};

	document
		.getElementById("confirmBtn")
		.addEventListener("click", function () {
			if (pendingForm) {
				pendingForm.submit();
			}
		});
});
