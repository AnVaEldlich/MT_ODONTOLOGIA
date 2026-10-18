(function () {
    "use strict";

    function abrirDialogo(dialog) {
        if (dialog && typeof dialog.showModal === "function") {
            dialog.showModal();
        }
    }

    function enlazar(abrirId, dialogId, cerrarId) {
        const dialog = document.getElementById(dialogId);
        const abrir = document.getElementById(abrirId);
        const cerrar = document.getElementById(cerrarId);
        if (!dialog) {
            return;
        }
        if (abrir) {
            abrir.addEventListener("click", function () {
                abrirDialogo(dialog);
            });
        }
        if (cerrar) {
            cerrar.addEventListener("click", function () {
                dialog.close();
            });
        }
    }

    enlazar("seguidos-abrir", "seguidos-dialog", "seguidos-cerrar");
    enlazar("seguidores-abrir", "seguidores-dialog", "seguidores-cerrar");

    document.querySelectorAll("[data-abre-dialog]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            abrirDialogo(document.getElementById(boton.getAttribute("data-abre-dialog")));
        });
    });
})();
