const reactionOptions = document.querySelectorAll('[data-reaction-option]');
const reactionForm = document.querySelector('[data-reaction-form]');
const reactionRemoveInput = document.querySelector('[data-reaction-remove]');
const bookmarkButton = document.querySelector('[data-bookmark-button]');
const bookmarkForm = document.querySelector('[data-bookmark-form]');
const bookmarkInput = document.querySelector('[data-bookmark-input]');
const bookmarkRemoveInput = document.querySelector('[data-bookmark-remove]');
const bookmarkLabel = document.querySelector('[data-bookmark-label]');
const replyButtons = document.querySelectorAll('[data-reply-toggle]');
const deleteDialog = document.querySelector('[data-delete-dialog]');
const openDeleteDialogButton = document.querySelector('[data-open-delete-dialog]');
const closeDeleteDialogButton = document.querySelector('[data-close-delete-dialog]');

reactionOptions.forEach((option) => {
    const input = option.querySelector('input[type="radio"]');

    if (!input) {
        return;
    }

    option.addEventListener('click', (event) => {
        const isAlreadySelected = input.checked;

        if (!isAlreadySelected) {
            return;
        }

        event.preventDefault();

        if (reactionRemoveInput) {
            reactionRemoveInput.value = '1';
        }

        if (reactionForm) {
            reactionForm.submit();
        }
    });

    input.addEventListener('change', () => {
        if (!input.checked) {
            return;
        }

        if (reactionRemoveInput) {
            reactionRemoveInput.value = '0';
        }

        reactionOptions.forEach((currentOption) => {
            currentOption.classList.remove('is-active');
        });

        option.classList.add('is-active');

        if (reactionForm) {
            reactionForm.submit();
        }
    });
});

if (bookmarkButton && bookmarkInput && bookmarkLabel) {
    bookmarkInput.addEventListener('change', () => {
        const isBookmarked = bookmarkInput.checked;

        bookmarkButton.classList.toggle('is-active', isBookmarked);
        bookmarkLabel.textContent = isBookmarked ? 'Saved' : 'Bookmark';

        if (bookmarkRemoveInput) {
            bookmarkRemoveInput.value = isBookmarked ? '0' : '1';
        }

        if (bookmarkForm) {
            bookmarkForm.submit();
        }
    });
}

replyButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const comment = button.closest('.comment-item');
        const replyForm = comment.querySelector('[data-reply-form]');

        if (!replyForm) {
            return;
        }

        const isHidden = replyForm.classList.toggle('is-hidden');
        button.textContent = isHidden ? 'Reply' : 'Cancel reply';
    });
});

if (deleteDialog && openDeleteDialogButton) {
    openDeleteDialogButton.addEventListener('click', () => {
        deleteDialog.showModal();
    });
}

if (deleteDialog && closeDeleteDialogButton) {
    closeDeleteDialogButton.addEventListener('click', () => {
        deleteDialog.close();
    });
}
