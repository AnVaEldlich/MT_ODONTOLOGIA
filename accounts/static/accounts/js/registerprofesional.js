(function () {
    "use strict";

    const form = document.getElementById("registerForm");
    if (!form) {
        return;
    }

    const nombre = form.querySelector("#id_first_name");
    const apellidos = form.querySelector("#id_last_name");
    const especialidad = form.querySelector("#id_especialidad");
    const ubicacion = form.querySelector("#id_ubicacion");
    const telefono = form.querySelector("#id_telefono");
    const password1 = form.querySelector("#id_password1");
    const password2 = form.querySelector("#id_password2");
    const previewNombre = form.querySelector('[data-preview="nombre"]');
    const previewEspecialidad = form.querySelector('[data-preview="especialidad"]');
    const previewUbicacion = form.querySelector('[data-preview="ubicacion"]');

    function textoOpcion(select, vacio) {
        if (!select || !select.value) {
            return vacio;
        }
        return select.selectedOptions[0].textContent.trim();
    }

    function actualizarPreview() {
        if (previewNombre) {
            const completo = [nombre && nombre.value.trim(), apellidos && apellidos.value.trim()]
                .filter(Boolean)
                .join(" ");
            previewNombre.textContent = completo || "Tu nombre";
        }
        if (previewEspecialidad) {
            previewEspecialidad.textContent = textoOpcion(especialidad, "Tu especialidad");
        }
        if (previewUbicacion) {
            previewUbicacion.textContent = (ubicacion && ubicacion.value.trim()) || "Ciudad o sede";
        }
    }

    [nombre, apellidos, ubicacion].forEach(function (campo) {
        if (campo) {
            campo.addEventListener("input", actualizarPreview);
        }
    });
    if (especialidad) {
        especialidad.addEventListener("change", actualizarPreview);
    }
    actualizarPreview();

    if (telefono) {
        telefono.addEventListener("input", function () {
            this.value = this.value.replace(/[^0-9\s]/g, "");
        });
    }

    function passwordsMatch() {
        if (!password1 || !password2) {
            return true;
        }
        const aviso = password2.closest(".field") && password2.closest(".field").querySelector(".err");
        const fallan = password2.value.length > 0 && password1.value !== password2.value;
        password2.setAttribute("aria-invalid", fallan ? "true" : "false");
        if (aviso && aviso.dataset.live === "1") {
            aviso.hidden = !fallan;
        }
        return !fallan;
    }

    if (password2) {
        const caja = password2.closest(".field");
        if (caja && !caja.querySelector(".err")) {
            const aviso = document.createElement("p");
            aviso.className = "err";
            aviso.dataset.live = "1";
            aviso.hidden = true;
            aviso.textContent = "Las contraseñas no coinciden.";
            caja.appendChild(aviso);
        } else if (caja) {
            const aviso = caja.querySelector(".err");
            if (aviso) {
                aviso.dataset.live = "1";
            }
        }
        password1.addEventListener("input", passwordsMatch);
        password2.addEventListener("input", passwordsMatch);
    }

    form.addEventListener("submit", function (event) {
        if (!passwordsMatch()) {
            event.preventDefault();
            password2.focus();
            return;
        }
        const boton = form.querySelector('button[type="submit"]');
        if (boton) {
            boton.disabled = true;
            boton.textContent = "Creando tu cuenta...";
        }
    });

    const primerError = form.querySelector(".field.has-error");
    if (primerError) {
        primerError.scrollIntoView({ behavior: "smooth", block: "center" });
        const foco = primerError.querySelector("input, select");
        if (foco) {
            foco.focus();
        }
    }
})();
