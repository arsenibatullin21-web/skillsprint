const progressRange = document.querySelector("#progress-range");
const progressValue = document.querySelector("#progress-value");
const progressChange = document.querySelector("#progress-change");
const progressPresets = document.querySelectorAll("[data-progress-preset]");
const progressNote = document.querySelector("#progress-note");
const noteCharacterCount = document.querySelector("#note-character-count");
const previousProgress = Number(
    progressRange.dataset.previousProgress || 0
);

function updateProgressDisplay() {
    const value = Number(progressRange.value);
    const difference = value - previousProgress;

    progressValue.value = `${value}%`;
    progressChange.textContent = `${difference > 0 ? "+" : ""}${difference}%`;
    progressRange.style.setProperty("--range-progress", `${value}%`);

    progressChange.classList.toggle("is-positive", difference > 0);
    progressChange.classList.toggle("is-negative", difference < 0);
    progressChange.classList.toggle("is-neutral", difference === 0);

    progressPresets.forEach((button) => {
        button.classList.toggle(
            "is-selected",
            Number(button.dataset.progressPreset) === value
        );
    });
}

progressRange.addEventListener("input", updateProgressDisplay);

progressPresets.forEach((button) => {
    button.addEventListener("click", () => {
        progressRange.value = button.dataset.progressPreset;
        updateProgressDisplay();
    });
});

progressNote.addEventListener("input", () => {
    noteCharacterCount.value = progressNote.value.length;
});

updateProgressDisplay();
