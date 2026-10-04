(function () {
    "use strict";

    const dialog = document.getElementById("seguidos-dialog");
    const abrir = document.getElementById("seguidos-abrir");
    const cerrar = document.getElementById("seguidos-cerrar");
    if (!dialog || !abrir) {
        return;
    }

    abrir.addEventListener("click", function () {
        dialog.showModal();
    });
    if (cerrar) {
        cerrar.addEventListener("click", function () {
            dialog.close();
        });
    }
})();
