const joinDialogOpen = document.querySelector("#join-dialog-open");
const joinDialog = document.querySelector("#join-group-dialog");
const joinDialogClose = document.querySelector("#close-join-dialog");

if (joinDialogOpen && joinDialog && joinDialogClose) {
    joinDialogOpen.addEventListener("click", () => {
        joinDialog.showModal();
    });

    joinDialogClose.addEventListener("click", () => {
        joinDialog.close();
    });

    joinDialog.addEventListener("click", (event) => {
        if (event.target === joinDialog) {
            joinDialog.close();
        }
    });
}
