const milestoneList = document.querySelector("#update-milestone-list");
const addMilestoneButton = document.querySelector("#add-update-milestone");
const milestoneTemplate = document.querySelector("#update-milestone-template");
const totalMilestoneForms = document.querySelector(
    "#id_milestone-TOTAL_FORMS"
);

function updateMilestonePositions() {
    const rows = milestoneList.querySelectorAll(".milestone-row:not([hidden])");

    rows.forEach((row, index) => {
        row.querySelector(".milestone-position").textContent = index + 1;
    });
}

function updateCharacterCount(field) {
    const group = field.closest(".field-group");
    const output = group?.querySelector("[data-character-count]");

    if (output) {
        output.value = field.value.length;
    }
}

document.querySelectorAll("[data-character-field]").forEach((field) => {
    updateCharacterCount(field);
    field.addEventListener("input", () => updateCharacterCount(field));
});

addMilestoneButton.addEventListener("click", () => {
    const formIndex = Number(totalMilestoneForms.value);
    const newFormHtml = milestoneTemplate.innerHTML.replaceAll(
        "__prefix__",
        formIndex
    );

    milestoneList.insertAdjacentHTML("beforeend", newFormHtml);
    totalMilestoneForms.value = formIndex + 1;
    updateMilestonePositions();

    const newTitle = milestoneList.querySelector(
        `input[name="milestone-${formIndex}-title"]`
    );
    newTitle?.focus();
});

milestoneList.addEventListener("click", (event) => {
    const removeButton = event.target.closest(".remove-milestone");

    if (!removeButton) {
        return;
    }

    const row = removeButton.closest(".milestone-row");
    const deleteInput = row.querySelector('input[name$="-DELETE"]');

    if (deleteInput) {
        deleteInput.checked = true;
        row.hidden = true;
    } else {
        row.remove();
    }

    updateMilestonePositions();
});

milestoneList.addEventListener("change", (event) => {
    if (!event.target.matches('input[name$="-is_completed"]')) {
        return;
    }

    event.target
        .closest(".milestone-row")
        .classList.toggle("is-completed", event.target.checked);
});
