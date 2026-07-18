const bookmarkSearchInput = document.querySelector('[data-bookmark-search]');
const bookmarkCards = document.querySelectorAll('[data-bookmark-card]');
const bookmarkNoResults = document.querySelector('[data-bookmark-no-results]');
const bookmarkTabs = document.querySelectorAll('[data-bookmark-filter]');

function updateBookmarkResults() {
    const query = bookmarkSearchInput ? bookmarkSearchInput.value.trim().toLowerCase() : '';
    let visibleCount = 0;

    bookmarkCards.forEach((card) => {
        const text = (card.dataset.bookmarkText || '').toLowerCase();
        const isVisible = !query || text.includes(query);

        card.classList.toggle('is-hidden', !isVisible);

        if (isVisible) {
            visibleCount += 1;
        }
    });

    if (bookmarkNoResults) {
        bookmarkNoResults.classList.toggle('is-hidden', visibleCount !== 0);
    }
}

if (bookmarkSearchInput) {
    bookmarkSearchInput.addEventListener('input', updateBookmarkResults);
}

bookmarkTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
        bookmarkTabs.forEach((currentTab) => currentTab.classList.remove('is-active'));
        tab.classList.add('is-active');
    });
});
