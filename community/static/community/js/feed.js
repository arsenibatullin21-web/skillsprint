const feedSearch = document.querySelector("[data-feed-search]");
const feedPosts = Array.from(document.querySelectorAll("[data-feed-post]"));
const feedTabs = Array.from(document.querySelectorAll("[data-feed-filter]"));
const feedNoResults = document.querySelector("[data-feed-no-results]");
const feedPage = document.querySelector("[data-current-user-id]");

let activeFeedFilter = "all";

function normalizeText(value) {
    return value.trim().toLowerCase();
}

function updateFeed() {
    const searchTerm = feedSearch ? normalizeText(feedSearch.value) : "";
    let visibleCount = 0;
    const currentUserId = feedPage?.dataset.currentUserId || "";

    feedPosts.forEach((post) => {
        const matchesSearch = normalizeText(post.textContent).includes(searchTerm);
        const matchesAuthor = activeFeedFilter === "all" || post.dataset.authorId === currentUserId;
        const isVisible = matchesSearch && matchesAuthor;

        post.classList.toggle("is-hidden", !isVisible);

        if (isVisible) {
            visibleCount += 1;
        }
    });

    if (feedNoResults) {
        feedNoResults.classList.toggle("is-hidden", visibleCount > 0 || feedPosts.length === 0);
    }
}

function setActiveFilter(filter) {
    activeFeedFilter = filter;

    feedTabs.forEach((tab) => {
        tab.classList.toggle("is-active", tab.dataset.feedFilter === filter);
    });

    updateFeed();
}

feedSearch?.addEventListener("input", updateFeed);

feedTabs.forEach((tab) => {
    tab.addEventListener("click", () => setActiveFilter(tab.dataset.feedFilter));
});

document.querySelectorAll("[data-reaction-button], [data-bookmark-button]").forEach((button) => {
    button.addEventListener("click", () => {
        button.classList.toggle("is-active");
    });
});
