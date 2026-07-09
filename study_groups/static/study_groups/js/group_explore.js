const groupCards = document.querySelectorAll(".explore-group-card");
const searchInput = document.querySelector("#group-search");
const topicFilter = document.querySelector("#topic-filter");
const sizeFilter = document.querySelector("#size-filter");
const sortSelect = document.querySelector("#sort-groups");
const resultCount = document.querySelector("#group-result-count");
const emptyState = document.querySelector("#empty-groups-state");
const clearButtons = document.querySelectorAll("#clear-group-filters, [data-clear-filters]");
const groupGrid = document.querySelector("#group-grid");
const joinButtons = document.querySelectorAll(".join-group-action");

function matchesSize(memberCount, size) {
    if (size === "small") {
        return memberCount <= 10;
    }

    if (size === "medium") {
        return memberCount >= 11 && memberCount <= 30;
    }

    if (size === "large") {
        return memberCount >= 31;
    }

    return true;
}

function sortCards() {
    const cards = Array.from(groupCards);

    cards.sort((first, second) => {
        if (sortSelect.value === "members") {
            return Number(second.dataset.members) - Number(first.dataset.members);
        }

        if (sortSelect.value === "newest") {
            return Number(second.dataset.created) - Number(first.dataset.created);
        }

        return 0;
    });

    cards.forEach((card) => groupGrid.appendChild(card));
}

function filterGroups() {
    const searchValue = searchInput.value.trim().toLowerCase();
    const selectedTopic = topicFilter.value;
    const selectedSize = sizeFilter.value;
    let visibleCount = 0;

    groupCards.forEach((card) => {
        const cardText = card.textContent.toLowerCase();
        const memberCount = Number(card.dataset.members);
        const topicMatches = selectedTopic === "all" || card.dataset.topic === selectedTopic;
        const sizeMatches = matchesSize(memberCount, selectedSize);
        const searchMatches = !searchValue || cardText.includes(searchValue);
        const shouldShow = topicMatches && sizeMatches && searchMatches;

        card.hidden = !shouldShow;

        if (shouldShow) {
            visibleCount += 1;
        }
    });

    resultCount.textContent = visibleCount;
    emptyState.hidden = visibleCount > 0;
}

function resetFilters() {
    searchInput.value = "";
    topicFilter.value = "all";
    sizeFilter.value = "all";
    sortSelect.value = "recommended";
    sortCards();
    filterGroups();
}

searchInput.addEventListener("input", filterGroups);
topicFilter.addEventListener("change", filterGroups);
sizeFilter.addEventListener("change", filterGroups);
sortSelect.addEventListener("change", () => {
    sortCards();
    filterGroups();
});

clearButtons.forEach((button) => {
    button.addEventListener("click", resetFilters);
});

joinButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const joined = button.classList.toggle("is-joined");
        button.textContent = joined ? "Joined" : "Join";
    });
});

sortCards();
filterGroups();
