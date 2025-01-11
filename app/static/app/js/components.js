/** Modal */
function toggleModal(id) {
    let modal = document.getElementById(id);
    let body = document.body;
    modal.classList.toggle("modal--fade-in");
    if (modal.classList.contains("modal--fade-in")) {
        body.style.overflow = "hidden"; // Prevent scroll
    } else {
        body.style.overflow = "auto";
    }
}