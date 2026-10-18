(function () {
    function abrir(dialog) {
        if (!dialog) {
            return;
        }
        if (typeof dialog.showModal === "function" && !dialog.open) {
            dialog.showModal();
        }
    }

    function cerrar(dialog) {
        if (dialog && typeof dialog.close === "function" && dialog.open) {
            dialog.close();
        }
    }

    document.querySelectorAll("[data-abre-dialog]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            var cerrarId = boton.getAttribute("data-dialog-cerrar");
            if (cerrarId) {
                cerrar(document.getElementById(cerrarId));
            }
            abrir(document.getElementById(boton.getAttribute("data-abre-dialog")));
        });
    });

    document.querySelectorAll("[data-dialog-cerrar]").forEach(function (boton) {
        if (boton.hasAttribute("data-abre-dialog")) {
            return;
        }
        boton.addEventListener("click", function () {
            cerrar(document.getElementById(boton.getAttribute("data-dialog-cerrar")));
        });
    });

    document.querySelectorAll("dialog[data-abrir-al-cargar]").forEach(function (dialog) {
        abrir(dialog);
    });

    document.querySelectorAll("[data-atajos-horario]").forEach(function (grupo) {
        var form = grupo.closest("form");
        if (!form) {
            return;
        }
        grupo.querySelectorAll("[data-dias]").forEach(function (atajo) {
            atajo.addEventListener("click", function () {
                var dias = (atajo.getAttribute("data-dias") || "").split(",");
                form.querySelectorAll('input[name="dias"]').forEach(function (caja) {
                    caja.checked = dias.indexOf(caja.value) !== -1;
                });
                var inicio = form.querySelector('input[name="hora_inicio"]');
                var fin = form.querySelector('input[name="hora_fin"]');
                if (inicio) {
                    inicio.value = atajo.getAttribute("data-inicio") || "";
                }
                if (fin) {
                    fin.value = atajo.getAttribute("data-fin") || "";
                }
            });
        });
    });
})();
