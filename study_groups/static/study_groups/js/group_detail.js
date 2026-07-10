const joinAction = document.querySelector("[data-join-action]");
const membershipLabel = document.querySelector("[data-membership-label]");

if (joinAction && membershipLabel) {
    joinAction.addEventListener("click", () => {
        const isJoined = joinAction.classList.toggle("is-joined");

        joinAction.textContent = isJoined ? "Joined" : joinAction.dataset.publicLabel;
        membershipLabel.textContent = isJoined ? "Member" : "Not joined";
    });
}
