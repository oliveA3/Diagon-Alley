"use strict";

const userASelect = document.getElementById("user_a");
const userBSelect = document.getElementById("user_b");

function updateUserBOptions() {
	const selectedA = userASelect.value;

	for (let option of userBSelect.options) {
		option.disabled = option.value === selectedA;
	}
}
function updateUserAOptions() {
	const selectedB = userBSelect.value;

	for (let option of userASelect.options) {
		option.disabled = option.value === selectedB;
	}
}

userASelect.addEventListener("change", updateUserBOptions);
userBSelect.addEventListener("change", updateUserAOptions);
window.addEventListener("DOMContentLoaded", updateUserBOptions);
window.addEventListener("DOMContentLoaded", updateUserAOptions);