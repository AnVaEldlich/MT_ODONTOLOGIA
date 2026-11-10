(function () {
    "use strict";

    const espera = 700;

    document.querySelectorAll(".barra-auto").forEach(function (contenedor) {
        let temporizador = 0;
        contenedor.addEventListener("scroll", function () {
            contenedor.classList.add("con-scroll");
            window.clearTimeout(temporizador);
            temporizador = window.setTimeout(function () {
                contenedor.classList.remove("con-scroll");
            }, espera);
        }, { passive: true });
    });
})();
