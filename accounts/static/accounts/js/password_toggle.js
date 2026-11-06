(function () {
    "use strict";

    document.querySelectorAll("[data-password-toggle]").forEach(function (boton) {
        const campoId = boton.getAttribute("aria-controls");
        const envoltorio = boton.closest(".password-wrapper");
        const campo = campoId
            ? document.getElementById(campoId)
            : (envoltorio ? envoltorio.querySelector("input") : null);
        if (!campo) {
            return;
        }
        const iconoVer = boton.querySelector(".i-ojo");
        const iconoOcultar = boton.querySelector(".i-ojo-oculto");

        boton.addEventListener("click", function () {
            const visible = campo.type === "text";
            campo.type = visible ? "password" : "text";
            boton.setAttribute("aria-pressed", visible ? "false" : "true");
            boton.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
            if (iconoVer) {
                iconoVer.hidden = !visible;
            }
            if (iconoOcultar) {
                iconoOcultar.hidden = visible;
            }
        });
    });
})();
