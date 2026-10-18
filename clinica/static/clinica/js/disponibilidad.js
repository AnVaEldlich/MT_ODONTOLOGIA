(function () {
    "use strict";

    const caja = document.querySelector("[data-atajos-horario]");
    const form = caja && caja.closest("form");
    if (!caja || !form) {
        return;
    }

    caja.addEventListener("click", (event) => {
        const boton = event.target.closest("[data-dias]");
        if (!boton) {
            return;
        }
        const dias = boton.dataset.dias.split(",");
        form.querySelectorAll('input[name="dias"]').forEach((input) => {
            input.checked = dias.indexOf(input.value) !== -1;
        });
        const inicio = form.querySelector('[name="hora_inicio"]');
        const fin = form.querySelector('[name="hora_fin"]');
        if (inicio) {
            inicio.value = boton.dataset.inicio;
        }
        if (fin) {
            fin.value = boton.dataset.fin;
        }
    });
})();
