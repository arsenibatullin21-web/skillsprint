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

const leaveDialogOpen = document.querySelector("#leave-dialog-open");
const leaveDialog = document.querySelector("#leave-group-dialog");
const leaveDialogClose = document.querySelector("#close-leave-dialog");

if (leaveDialogOpen && leaveDialog && leaveDialogClose) {
    leaveDialogOpen.addEventListener("click", () => {
        leaveDialog.showModal();
    });

    leaveDialogClose.addEventListener("click", () => {
        leaveDialog.close();
    });

    leaveDialog.addEventListener("click", (event) => {
        if (event.target === leaveDialog) {
            leaveDialog.close();
        }
    });
}
