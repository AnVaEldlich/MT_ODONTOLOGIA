(function () {
    "use strict";

    function abrirDialogo(dialog) {
        if (dialog && typeof dialog.showModal === "function" && !dialog.open) {
            dialog.showModal();
        }
    }

    function cerrarDialogo(dialog) {
        if (dialog && typeof dialog.close === "function" && dialog.open) {
            dialog.close();
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

    enlazar("citas-proximas-abrir", "citas-proximas-dialog", "citas-proximas-cerrar");
    enlazar("citas-total-abrir", "citas-total-dialog", "citas-total-cerrar");
    enlazar("seguidos-abrir", "seguidos-dialog", "seguidos-cerrar");
    enlazar("seguidores-abrir", "seguidores-dialog", "seguidores-cerrar");

    document.querySelectorAll("[data-abre-dialog]").forEach(function (el) {
        const abrir = function () {
            const cerrarId = el.getAttribute("data-dialog-cerrar");
            if (cerrarId) {
                cerrarDialogo(document.getElementById(cerrarId));
            }
            abrirDialogo(document.getElementById(el.getAttribute("data-abre-dialog")));
        };
        el.addEventListener("click", abrir);
        el.addEventListener("keydown", function (event) {
            if (event.key !== "Enter" && event.key !== " ") {
                return;
            }
            if (el.tagName === "BUTTON" || el.tagName === "A") {
                return;
            }
            event.preventDefault();
            abrir();
        });
    });

    document.querySelectorAll("[data-dialog-cerrar]").forEach(function (boton) {
        if (boton.hasAttribute("data-abre-dialog")) {
            return;
        }
        boton.addEventListener("click", function () {
            cerrarDialogo(document.getElementById(boton.getAttribute("data-dialog-cerrar")));
        });
    });
})();
