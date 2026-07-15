const memberTabs = document.querySelectorAll("[data-filter]");
const memberCards = document.querySelectorAll("[data-member-card]");
const memberSearch = document.querySelector("[data-member-search]");
const emptyState = document.querySelector("[data-empty-state]");

const memberDialog = document.querySelector("#member-action-dialog");
const dialogCancel = document.querySelector("#member-dialog-cancel");
const dialogConfirm = document.querySelector("#member-dialog-confirm");
const dialogTitle = document.querySelector("[data-dialog-title]");
const dialogCopy = document.querySelector("[data-dialog-copy]");
const dialogIcon = document.querySelector("[data-dialog-icon]");

let activeFilter = "all";
let activeAction = null;
let activeForm = null;

function updateVisibleMembers() {
    const searchValue = memberSearch ? memberSearch.value.trim().toLowerCase() : "";
    let visibleCount = 0;

    memberCards.forEach((card) => {
        const role = card.dataset.role;
        const status = card.dataset.status;
        const matchesFilter = activeFilter === "all" || role === activeFilter || status === activeFilter;
        const matchesSearch = !searchValue || card.textContent.toLowerCase().includes(searchValue);
        const shouldShow = matchesFilter && matchesSearch;

        card.hidden = !shouldShow;

        if (shouldShow) {
            visibleCount += 1;
        }
    });

    if (emptyState) {
        emptyState.hidden = visibleCount > 0;
    }
}

memberTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        memberTabs.forEach((item) => item.classList.remove("is-active"));
        tab.classList.add("is-active");
        activeFilter = tab.dataset.filter;
        updateVisibleMembers();
    });
});

if (memberSearch) {
    memberSearch.addEventListener("input", updateVisibleMembers);
}

document.querySelectorAll("[data-member-action]").forEach((button) => {
    button.addEventListener("click", () => {
        activeForm = button.closest("form");
        activeAction = button.dataset.memberAction;
        const username = button.dataset.user;
        const isDanger = activeAction === "remove" || activeAction === "promote_owner";

        const titleMap = {
            promote: `Make ${username} a moderator?`,
            promote_owner: `Transfer ownership to ${username}?`,
            demote: `Demote ${username}?`,
            remove: `Remove ${username} from this group?`,
        };

        const copyMap = {
            promote: "This member will be able to review requests and help manage group members.",
            promote_owner: "This user will become the group owner. You will lose owner-level control after confirming.",
            demote: "This moderator will become a regular member and lose moderator permissions.",
            remove: "This user will lose access to the group and its private content.",
        };

        dialogTitle.textContent = titleMap[activeAction];
        dialogCopy.textContent = copyMap[activeAction];
        dialogIcon.textContent = isDanger ? "!" : "?";
        dialogIcon.classList.toggle("is-danger", isDanger);
        dialogConfirm.textContent = activeAction === "remove"
            ? "Remove member"
            : activeAction === "promote_owner"
                ? "Transfer ownership"
                : "Confirm";
        dialogConfirm.classList.toggle("is-danger", isDanger);

        memberDialog.showModal();
    });
});

if (dialogCancel && memberDialog) {
    dialogCancel.addEventListener("click", () => {
        memberDialog.close();
    });

    memberDialog.addEventListener("click", (event) => {
        if (event.target === memberDialog) {
            memberDialog.close();
        }
    });
}

if (dialogConfirm) {
    dialogConfirm.addEventListener("click", () => {
        if (!activeForm || !activeAction) {
            memberDialog.close();
            return;
        }

        activeForm.submit();
    });
}
