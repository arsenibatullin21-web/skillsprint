const activityToggle = document.querySelector("[data-toggle-activity]");
const hiddenActivities = document.querySelectorAll(".public-activity.is-hidden-extra");

if (activityToggle && hiddenActivities.length > 0) {
    activityToggle.addEventListener("click", () => {
        const shouldShow = activityToggle.dataset.expanded !== "true";

        hiddenActivities.forEach((activity) => {
            activity.classList.toggle("is-visible-extra", shouldShow);
        });

        activityToggle.dataset.expanded = String(shouldShow);
        activityToggle.textContent = shouldShow ? "Show fewer updates" : "Show more updates";
    });
}
