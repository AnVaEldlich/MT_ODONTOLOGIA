document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const especialidadSelect = document.getElementById('especialidad');
    const ubicacionInput = document.getElementById('ubicacion');
    const telefonoInput = document.getElementById('telefono');

    const previewNombre = document.getElementById('previewNombre');
    const previewApellidos = document.getElementById('previewApellidos');
    const previewEspecialidad = document.getElementById('previewEspecialidad');
    const previewUbicacionText = document.getElementById('previewUbicacionText');
    const previewUbicacion2 = document.getElementById('previewUbicacion2');

    const especialidadesMap = {
        'odontologia-general': 'Odontología General',
        ortodoncia: 'Ortodoncia',
        endodoncia: 'Endodoncia',
        periodoncia: 'Periodoncia',
        odontopediatria: 'Odontopediatría',
        'cirugia-oral': 'Cirugía Oral',
        implantologia: 'Implantología',
        'estetica-dental': 'Estética Dental',
        prostodoncia: 'Prostodoncia',
    };

    function countPhoneDigits(value) {
        let digits = value.replace(/\D/g, '');
        if (digits.length === 12 && digits.startsWith('57')) {
            digits = digits.slice(2);
        }
        return digits;
    }

    function updatePreview() {
        const nombre = firstNameInput?.value.trim() || '';
        const apellidos = lastNameInput?.value.trim() || '';
        const especialidad = especialidadSelect?.value || '';
        const ubicacion = ubicacionInput?.value.trim() || '';

        if (previewNombre) {
            previewNombre.textContent = nombre || 'Tu Nombre';
        }
        if (previewApellidos) {
            previewApellidos.textContent = apellidos ? ' ' + apellidos : '';
        }
        if (previewEspecialidad) {
            previewEspecialidad.textContent = especialidad
                ? especialidadesMap[especialidad]
                : 'Tu Especialidad';
        }
        if (previewUbicacionText) {
            previewUbicacionText.textContent = ubicacion ? ' • ' + ubicacion : '';
        }
        if (previewUbicacion2) {
            previewUbicacion2.textContent = ubicacion || 'Ubicación de consulta';
        }
    }

    [firstNameInput, lastNameInput, especialidadSelect, ubicacionInput].forEach((el) => {
        if (el) {
            el.addEventListener('input', updatePreview);
            el.addEventListener('change', updatePreview);
        }
    });

    document.querySelectorAll('.password-toggle').forEach((toggle) => {
        toggle.addEventListener('click', function () {
            const passwordInput = document.getElementById(this.getAttribute('data-target'));
            if (passwordInput) {
                passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
            }
        });
    });

    if (telefonoInput) {
        telefonoInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^\d\s]/g, '');
        });
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            const password1 = document.getElementById('password1')?.value || '';
            const password2 = document.getElementById('password2')?.value || '';
            const aceptaTerminos = document.getElementById('acepta_terminos')?.checked;
            const phoneDigits = telefonoInput ? countPhoneDigits(telefonoInput.value) : '';

            if (password1 !== password2) {
                e.preventDefault();
                alert('Las contraseñas no coinciden. Por favor, verifica.');
                return;
            }

            if (password1.length < 8) {
                e.preventDefault();
                alert('La contraseña debe tener al menos 8 caracteres.');
                return;
            }

            if (phoneDigits.length !== 10) {
                e.preventDefault();
                alert('Ingresa un teléfono móvil de 10 dígitos (sin el +57).');
                telefonoInput?.focus();
                return;
            }

            if (!aceptaTerminos) {
                e.preventDefault();
                alert('Debes aceptar los términos y condiciones para continuar.');
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Creando cuenta...';
            }
        });
    }

    const errorInputs = document.querySelectorAll('.error-text');
    if (errorInputs.length > 0) {
        errorInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    updatePreview();
});
