(function () {
    "use strict";

    const envoltorio = document.querySelector("[data-notificaciones]");
    if (!envoltorio) {
        return;
    }

    const boton = envoltorio.querySelector("[data-notificaciones-toggle]");
    const panel = envoltorio.querySelector("[data-notificaciones-panel]");
    if (!boton || !panel) {
        return;
    }

    const colocar = () => {
        const rect = boton.getBoundingClientRect();
        const margen = 8;
        const ancho = Math.min(panel.offsetWidth || 352, window.innerWidth - 24);
        let left = rect.right - ancho;
        if (left < 12) {
            left = 12;
        }
        if (left + ancho > window.innerWidth - 12) {
            left = Math.max(12, window.innerWidth - ancho - 12);
        }
        panel.style.top = `${Math.round(rect.bottom + margen)}px`;
        panel.style.left = `${Math.round(left)}px`;
        panel.style.right = "auto";
    };

    const cerrar = () => {
        panel.hidden = true;
        boton.setAttribute("aria-expanded", "false");
        window.removeEventListener("resize", colocar);
        window.removeEventListener("scroll", colocar, true);
    };

    const abrir = () => {
        panel.hidden = false;
        boton.setAttribute("aria-expanded", "true");
        colocar();
        window.addEventListener("resize", colocar);
        window.addEventListener("scroll", colocar, true);
    };

    const alternar = () => {
        if (panel.hidden) {
            abrir();
        } else {
            cerrar();
        }
    };

    boton.addEventListener("click", (event) => {
        event.stopPropagation();
        alternar();
    });

    document.addEventListener("click", (event) => {
        if (!envoltorio.contains(event.target)) {
            cerrar();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            cerrar();
        }
    });
})();
