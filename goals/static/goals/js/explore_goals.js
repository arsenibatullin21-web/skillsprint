const goalSearch = document.querySelector("#goal-search");
const statusFilter = document.querySelector("#status-filter");
const progressFilter = document.querySelector("#progress-filter");
const goalSort = document.querySelector("#sort-goals");
const resultCount = document.querySelector("#goal-result-count");
const goalList = document.querySelector("#explore-goal-list");
const emptyState = document.querySelector("#explore-empty-state");
const clearFilterButtons = document.querySelectorAll(
    "#clear-goal-filters, [data-clear-filters]"
);
const goalCards = Array.from(goalList.querySelectorAll(".explore-goal"));

function matchesProgress(progress, filter) {
    if (filter === "starting") {
        return progress <= 25;
    }

    if (filter === "underway") {
        return progress >= 26 && progress <= 74;
    }

    if (filter === "near") {
        return progress >= 75 && progress <= 99;
    }

    if (filter === "complete") {
        return progress === 100;
    }

    return true;
}

function sortGoals(cards) {
    const sort = goalSort.value;

    if (sort === "newest") {
        return cards.sort(
            (first, second) =>
                Number(second.dataset.created) - Number(first.dataset.created)
        );
    }

    if (sort === "deadline") {
        return cards.sort(
            (first, second) =>
                Number(first.dataset.deadline) - Number(second.dataset.deadline)
        );
    }

    if (sort === "progress") {
        return cards.sort(
            (first, second) =>
                Number(second.dataset.progress) - Number(first.dataset.progress)
        );
    }

    return cards.sort(
        (first, second) =>
            goalCards.indexOf(first) - goalCards.indexOf(second)
    );
}

function updateGoalResults() {
    const query = goalSearch.value.trim().toLowerCase();
    const status = statusFilter.value;
    const progress = progressFilter.value;

    const visibleCards = goalCards.filter((card) => {
        const searchableText = `${card.dataset.title} ${card.dataset.owner}`
            .toLowerCase();
        const matchesQuery = searchableText.includes(query);
        const matchesStatus =
            status === "all" || card.dataset.status === status;
        const matchesProgressFilter = matchesProgress(
            Number(card.dataset.progress),
            progress
        );

        return matchesQuery && matchesStatus && matchesProgressFilter;
    });

    goalCards.forEach((card) => {
        card.hidden = !visibleCards.includes(card);
    });

    sortGoals(visibleCards).forEach((card) => {
        goalList.appendChild(card);
    });

    resultCount.textContent = visibleCards.length;
    emptyState.hidden = visibleCards.length !== 0;
}

function clearFilters() {
    goalSearch.value = "";
    statusFilter.value = "all";
    progressFilter.value = "all";
    goalSort.value = "recommended";
    updateGoalResults();
    goalSearch.focus();
}

goalSearch.addEventListener("input", updateGoalResults);
statusFilter.addEventListener("change", updateGoalResults);
progressFilter.addEventListener("change", updateGoalResults);
goalSort.addEventListener("change", updateGoalResults);

clearFilterButtons.forEach((button) => {
    button.addEventListener("click", clearFilters);
});

updateGoalResults();
