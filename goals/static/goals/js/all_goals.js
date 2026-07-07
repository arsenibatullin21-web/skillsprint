const goalTabs = document.querySelectorAll("[data-filter]");
const goalRows = document.querySelectorAll(".goal-row");
const visibleGoalCount = document.querySelector("#visible-goal-count");
const emptyGoalsState = document.querySelector("#empty-goals-state");
const summaryCounters = document.querySelectorAll("[data-summary-count]");

function countGoals(status) {
    if (status === "all") {
        return goalRows.length;
    }

    return Array.from(goalRows).filter((goal) => goal.dataset.status === status).length;
}

function updateSummary() {
    summaryCounters.forEach((counter) => {
        counter.textContent = countGoals(counter.dataset.summaryCount);
    });
}

function filterGoals(status) {
    let visibleCount = 0;

    goalRows.forEach((goal) => {
        const shouldShow = status === "all" || goal.dataset.status === status;

        goal.hidden = !shouldShow;

        if (shouldShow) {
            visibleCount += 1;
        }
    });

    visibleGoalCount.textContent = visibleCount;
    emptyGoalsState.hidden = visibleCount > 0;
}

goalTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        goalTabs.forEach((item) => item.classList.remove("is-active"));
        tab.classList.add("is-active");
        filterGoals(tab.dataset.filter);
    });
});

updateSummary();
filterGoals("all");
