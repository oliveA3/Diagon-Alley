"use strict";

"use strict";

document.addEventListener("DOMContentLoaded", function () {
	const inputA = document.getElementById("input_user_a");
	const inputB = document.getElementById("input_user_b");
	const warning = document.getElementById("coDebtorWarning");

	function validateCoDebtors() {
		const valA = inputA.value.trim();
		const valB = inputB.value.trim();

		if (valA !== "" && valA === valB) {
			warning.style.display = "block";
			inputB.setCustomValidity(
				"No puedes seleccionar el mismo codeudor."
			);
		} else {
			warning.style.display = "none";
			inputB.setCustomValidity("");
		}
	}

	inputA.addEventListener("input", validateCoDebtors);
	inputB.addEventListener("input", validateCoDebtors);
});
