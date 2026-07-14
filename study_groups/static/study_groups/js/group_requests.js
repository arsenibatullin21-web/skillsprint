const requestTabs = document.querySelectorAll("[data-filter]");
const requestCards = document.querySelectorAll("[data-request-card]");
const requestSearch = document.querySelector("[data-request-search]");
const emptyState = document.querySelector("[data-empty-state]");

const reviewDialog = document.querySelector("#request-review-dialog");
const dialogCancel = document.querySelector("#request-dialog-cancel");
const dialogConfirm = document.querySelector("#request-dialog-confirm");
const dialogTitle = document.querySelector("[data-dialog-title]");
const dialogCopy = document.querySelector("[data-dialog-copy]");
const dialogIcon = document.querySelector("[data-dialog-icon]");

let activeFilter = "all";
let activeAction = null;
let activeForm = null;

function updateVisibleRequests() {
    const searchValue = requestSearch ? requestSearch.value.trim().toLowerCase() : "";
    let visibleCount = 0;

    requestCards.forEach((card) => {
        const matchesStatus = activeFilter === "all" || card.dataset.status === activeFilter;
        const matchesSearch = !searchValue || card.textContent.toLowerCase().includes(searchValue);
        const shouldShow = matchesStatus && matchesSearch;

        card.hidden = !shouldShow;

        if (shouldShow) {
            visibleCount += 1;
        }
    });

    if (emptyState) {
        emptyState.hidden = visibleCount > 0;
    }
}

requestTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        requestTabs.forEach((item) => item.classList.remove("is-active"));
        tab.classList.add("is-active");
        activeFilter = tab.dataset.filter;
        updateVisibleRequests();
    });
});

if (requestSearch) {
    requestSearch.addEventListener("input", updateVisibleRequests);
}

document.querySelectorAll("[data-dialog-action]").forEach((button) => {
    button.addEventListener("click", () => {
        activeForm = button.closest("form");
        activeAction = button.dataset.dialogAction;
        const username = button.dataset.user;
        const isReject = activeAction === "reject";

        dialogTitle.textContent = isReject ? `Reject ${username}?` : `Accept ${username}?`;
        dialogCopy.textContent = isReject
            ? "This user will not become a member. They may send another request later."
            : "This user will become an active member of the group.";
        dialogIcon.textContent = isReject ? "!" : "?";
        dialogIcon.classList.toggle("is-danger", isReject);
        dialogConfirm.textContent = isReject ? "Reject request" : "Accept request";
        dialogConfirm.classList.toggle("is-danger", isReject);

        reviewDialog.showModal();
    });
});

if (dialogCancel && reviewDialog) {
    dialogCancel.addEventListener("click", () => {
        reviewDialog.close();
    });

    reviewDialog.addEventListener("click", (event) => {
        if (event.target === reviewDialog) {
            reviewDialog.close();
        }
    });
}

if (dialogConfirm) {
    dialogConfirm.addEventListener("click", () => {
        if (!activeForm || !activeAction) {
            reviewDialog.close();
            return;
        }

        activeForm.submit();
    });
}
