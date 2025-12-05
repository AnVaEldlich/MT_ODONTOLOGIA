// registerprofesional.js

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const form = document.getElementById('registerForm');
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const especialidadSelect = document.getElementById('especialidad');
    const ubicacionInput = document.getElementById('ubicacion');
    
    // Elementos del preview
    const previewNombre = document.getElementById('previewNombre');
    const previewApellidos = document.getElementById('previewApellidos');
    const previewEspecialidad = document.getElementById('previewEspecialidad');
    const previewUbicacionText = document.getElementById('previewUbicacionText');
    const previewUbicacion2 = document.getElementById('previewUbicacion2');
    
    // Mapa de especialidades
    const especialidadesMap = {
        'odontologia-general': 'Odontología General',
        'ortodoncia': 'Ortodoncia',
        'endodoncia': 'Endodoncia',
        'periodoncia': 'Periodoncia',
        'odontopediatria': 'Odontopediatría',
        'cirugia-oral': 'Cirugía Oral',
        'implantologia': 'Implantología',
        'estetica-dental': 'Estética Dental',
        'prostodoncia': 'Prostodoncia'
    };
    
    // Actualizar preview en tiempo real
    function updatePreview() {
        const nombre = firstNameInput.value.trim();
        const apellidos = lastNameInput.value.trim();
        const especialidad = especialidadSelect.value;
        const ubicacion = ubicacionInput.value.trim();
        
        // Actualizar nombre
        if (nombre || apellidos) {
            previewNombre.textContent = nombre || 'Tu Nombre';
            previewApellidos.textContent = apellidos ? ' ' + apellidos : '';
        } else {
            previewNombre.textContent = 'Tu Nombre';
            previewApellidos.textContent = '';
        }
        
        // Actualizar especialidad
        if (especialidad) {
            previewEspecialidad.textContent = especialidadesMap[especialidad];
        } else {
            previewEspecialidad.textContent = 'Tu Especialidad';
        }
        
        // Actualizar ubicación
        if (ubicacion) {
            previewUbicacionText.textContent = ' • ' + ubicacion;
            previewUbicacion2.textContent = ubicacion;
        } else {
            previewUbicacionText.textContent = '';
            previewUbicacion2.textContent = 'Ubicación de consulta';
        }
    }
    
    // Event listeners para actualizar preview
    if (firstNameInput) firstNameInput.addEventListener('input', updatePreview);
    if (lastNameInput) lastNameInput.addEventListener('input', updatePreview);
    if (especialidadSelect) especialidadSelect.addEventListener('change', updatePreview);
    if (ubicacionInput) ubicacionInput.addEventListener('input', updatePreview);
    
    // Toggle password visibility
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            
            if (passwordInput) {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                } else {
                    passwordInput.type = 'password';
                }
            }
        });
    });
    
    // Validación de teléfono en tiempo real
    const telefonoInput = document.getElementById('telefono');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', function(e) {
            // Permitir solo números y espacios
            this.value = this.value.replace(/[^0-9\s]/g, '');
        });
    }
    
    // Validación del formulario antes de enviar
    if (form) {
        form.addEventListener('submit', function(e) {
            const password1 = document.getElementById('password1').value;
            const password2 = document.getElementById('password2').value;
            const aceptaTerminos = document.getElementById('acepta_terminos').checked;
            
            // Validar contraseñas
            if (password1 !== password2) {
                e.preventDefault();
                alert('Las contraseñas no coinciden. Por favor, verifica.');
                return false;
            }
            
            if (password1.length < 8) {
                e.preventDefault();
                alert('La contraseña debe tener al menos 8 caracteres.');
                return false;
            }
            
            // Validar términos
            if (!aceptaTerminos) {
                e.preventDefault();
                alert('Debes aceptar los términos y condiciones para continuar.');
                return false;
            }
            
            // Mostrar loader o desactivar botón
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Creando cuenta...';
            }
        });
    }
    
    // Validación de email en tiempo real
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.setCustomValidity('Por favor, ingresa un email válido');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Auto-formatear teléfono
    if (telefonoInput) {
        telefonoInput.addEventListener('blur', function() {
            let phone = this.value.replace(/\s/g, '');
            if (phone.length === 10) {
                // Formato: 300 123 4567
                this.value = phone.substring(0, 3) + ' ' + 
                            phone.substring(3, 6) + ' ' + 
                            phone.substring(6);
            }
        });
    }
    
    // Animar el scroll al primer error
    const errorInputs = document.querySelectorAll('.error-text');
    if (errorInputs.length > 0) {
        errorInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});