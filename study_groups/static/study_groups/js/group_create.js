const nameInput = document.querySelector("[data-slug-source]");
const slugPreview = document.querySelector("#slug-preview");
const previewName = document.querySelector("[data-preview-name]");
const previewDescription = document.querySelector("[data-preview-description]");
const descriptionInput = document.querySelector("#group-description");
const visibilityInputs = document.querySelectorAll("input[name='visibility']");
const visibilityBadge = document.querySelector(".visibility-badge");
const avatarInput = document.querySelector("[data-avatar-input]");
const avatarPreview = document.querySelector("[data-avatar-preview]");
const countSources = document.querySelectorAll("[data-count-source]");

function slugify(value) {
    return value
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 50);
}

function updateNamePreview() {
    const name = nameInput.value.trim();
    const slug = slugify(name) || "group-name";

    slugPreview.textContent = slug;
    previewName.textContent = name || "Group name";
    avatarPreview.textContent = name ? name[0] : "G";
}

function updateDescriptionPreview() {
    const description = descriptionInput.value.trim();
    previewDescription.textContent = description || "Your group description will appear here.";
}

function updateVisibilityPreview() {
    const selected = document.querySelector("input[name='visibility']:checked");

    if (!selected) {
        return;
    }

    visibilityBadge.textContent = selected.value;
    visibilityBadge.style.background = selected.value === "public" ? "#e9f7ef" : "#f3f4f6";
    visibilityBadge.style.color = selected.value === "public" ? "#237a4b" : "#737373";
}

function updateCounter(input) {
    const target = document.querySelector(input.dataset.countTarget);

    if (!target) {
        return;
    }

    target.textContent = `${input.value.length}/${input.maxLength}`;
}

countSources.forEach((input) => {
    updateCounter(input);
    input.addEventListener("input", () => updateCounter(input));
});

nameInput.addEventListener("input", updateNamePreview);
descriptionInput.addEventListener("input", updateDescriptionPreview);
visibilityInputs.forEach((input) => input.addEventListener("change", updateVisibilityPreview));

avatarInput.addEventListener("change", () => {
    const file = avatarInput.files[0];

    if (!file) {
        return;
    }

    const image = document.createElement("img");
    image.src = URL.createObjectURL(file);
    image.alt = "";

    avatarPreview.replaceChildren(image);
});

updateNamePreview();
updateDescriptionPreview();
updateVisibilityPreview();
