// Configuración global
const CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:3000' 
        : 'https://tu-dominio.com',
    VALIDATION_DELAYS: {
        EMAIL: 500,
        IDENTIFICATION: 500,
        PROFESSIONAL_REGISTRATION: 500
    },
    REDIRECT_DELAY: 2000,
    ERROR_DISPLAY_TIME: 5000
};

// Estado global de la aplicación
const appState = {
    isSubmitting: false,
    validationCache: new Map(),
    debounceTimers: new Map()
};

// Utilidades
const utils = {
    // Debounce para reducir llamadas a la API
    debounce(func, delay, key) {
        if (appState.debounceTimers.has(key)) {
            clearTimeout(appState.debounceTimers.get(key));
        }
        
        const timer = setTimeout(() => {
            func();
            appState.debounceTimers.delete(key);
        }, delay);
        
        appState.debounceTimers.set(key, timer);
    },

    // Validación de email mejorada
    isValidEmail(email) {
        const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return emailRegex.test(email) && email.length <= 254;
    },

    // Validación de URL mejorada
    isValidURL(string) {
        try {
            const url = new URL(string);
            return ['http:', 'https:'].includes(url.protocol);
        } catch {
            return false;
        }
    },

    // Sanitizar entrada de usuario
    sanitizeInput(input) {
        return input.toString().trim().replace(/[<>]/g, '');
    },

    // Formatear teléfono
    formatPhone(phone) {
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 10) {
            return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
        }
        return cleaned;
    },

    // Crear elemento de error
    createErrorElement(message, className = 'field-error') {
        const errorDiv = document.createElement('div');
        errorDiv.className = className;
        errorDiv.style.cssText = `
            color: #dc2626;
            font-size: 0.75rem;
            margin-top: 0.25rem;
            display: block;
            animation: slideIn 0.3s ease-out;
        `;
        errorDiv.textContent = message;
        return errorDiv;
    }
};

// Manejo de campos del formulario
const fieldHandler = {
    setValid(field) {
        field.style.borderColor = '#10b981';
        field.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
        field.setAttribute('aria-invalid', 'false');
    },

    setInvalid(field) {
        field.style.borderColor = '#ef4444';
        field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
        field.setAttribute('aria-invalid', 'true');
    },

    reset(field) {
        field.style.borderColor = '';
        field.style.boxShadow = '';
        field.removeAttribute('aria-invalid');
    },

    showError(field, message) {
        this.hideError(field);
        const errorElement = utils.createErrorElement(message);
        field.parentNode.appendChild(errorElement);
        field.setAttribute('aria-describedby', 'error-' + field.id);
        errorElement.id = 'error-' + field.id;
    },

    hideError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.removeAttribute('aria-describedby');
    },

    resetAll() {
        const allFields = document.querySelectorAll('input, textarea, select');
        allFields.forEach(field => {
            this.reset(field);
            this.hideError(field);
        });
    }
};

// Validadores
const validators = {
    async validateEmail(email, field) {
        if (!email) return true;

        // Validación de formato
        if (!utils.isValidEmail(email)) {
            fieldHandler.setInvalid(field);
            fieldHandler.showError(field, 'Formato de email inválido');
            return false;
        }

        // Verificar cache
        const cacheKey = `email:${email}`;
        if (appState.validationCache.has(cacheKey)) {
            const cached = appState.validationCache.get(cacheKey);
            if (cached.exists) {
                fieldHandler.setInvalid(field);
                fieldHandler.showError(field, 'Este email ya está registrado');
                return false;
            } else {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
                return true;
            }
        }

        // Validación en servidor
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/validate-email/${encodeURIComponent(email)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            // Guardar en cache
            appState.validationCache.set(cacheKey, result);
            
            if (result.exists) {
                fieldHandler.setInvalid(field);
                fieldHandler.showError(field, 'Este email ya está registrado');
                return false;
            } else {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
                return true;
            }
        } catch (error) {
            console.warn('Error validating email:', error);
            // En caso de error de red, permitir continuar pero mostrar advertencia
            fieldHandler.setValid(field);
            fieldHandler.showError(field, 'No se pudo validar el email (verificar conexión)');
            return true;
        }
    },

    async validateIdentification(identification, field) {
        if (!identification) return true;

        const cacheKey = `identification:${identification}`;
        if (appState.validationCache.has(cacheKey)) {
            const cached = appState.validationCache.get(cacheKey);
            if (cached.exists) {
                fieldHandler.setInvalid(field);
                fieldHandler.showError(field, 'Esta identificación ya está registrada');
                return false;
            } else {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
                return true;
            }
        }

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/validate-identification/${encodeURIComponent(identification)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            appState.validationCache.set(cacheKey, result);
            
            if (result.exists) {
                fieldHandler.setInvalid(field);
                fieldHandler.showError(field, 'Esta identificación ya está registrada');
                return false;
            } else {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
                return true;
            }
        } catch (error) {
            console.warn('Error validating identification:', error);
            fieldHandler.setValid(field);
            fieldHandler.showError(field, 'No se pudo validar la identificación (verificar conexión)');
            return true;
        }
    },

    async validateProfessionalRegistration(registration, field) {
        if (!registration) return true;

        const cacheKey = `registration:${registration}`;
        if (appState.validationCache.has(cacheKey)) {
            const cached = appState.validationCache.get(cacheKey);
            if (cached.exists) {
                fieldHandler.setInvalid(field);
                fieldHandler.showError(field, 'Este número de registro profesional ya está registrado');
                return false;
            } else {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
                return true;
            }
        }

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/validate-professional-registration/${encodeURIComponent(registration)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            appState.validationCache.set(cacheKey, result);
            
            if (result.exists) {
                fieldHandler.setInvalid(field);
                fieldHandler.showError(field, 'Este número de registro profesional ya está registrado');
                return false;
            } else {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
                return true;
            }
        } catch (error) {
            console.warn('Error validating professional registration:', error);
            fieldHandler.setValid(field);
            fieldHandler.showError(field, 'No se pudo validar el registro (verificar conexión)');
            return true;
        }
    },

    validateRequired(field) {
        const value = field.value.trim();
        
        if (field.type === 'radio') {
            const radioGroup = document.querySelectorAll(`input[name="${field.name}"]`);
            const isChecked = Array.from(radioGroup).some(radio => radio.checked);
            
            if (!isChecked) {
                radioGroup.forEach(radio => fieldHandler.setInvalid(radio.parentElement));
                return false;
            } else {
                radioGroup.forEach(radio => fieldHandler.setValid(radio.parentElement));
                return true;
            }
        } else {
            if (!value) {
                fieldHandler.setInvalid(field);
                return false;
            } else {
                fieldHandler.setValid(field);
                return true;
            }
        }
    },

    validateSpecialties() {
        const checkedBoxes = document.querySelectorAll('input[name="especialidad[]"]:checked');
        const especialidadContainer = document.querySelector('.checkbox-grid')?.parentElement;
        
        if (!especialidadContainer) return true;
        
        if (checkedBoxes.length === 0) {
            especialidadContainer.style.borderColor = '#ef4444';
            fieldHandler.showError(especialidadContainer, 'Debe seleccionar al menos una especialidad');
            return false;
        } else {
            especialidadContainer.style.borderColor = '';
            fieldHandler.hideError(especialidadContainer);
            return true;
        }
    }
};

// Inicialización del formulario
function initializeForm() {
    const form = document.getElementById('odontologo-form');
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    // Event listener para el envío del formulario
    form.addEventListener('submit', handleFormSubmit);

    // Validación de campos requeridos
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', () => validators.validateRequired(field));
        field.addEventListener('input', () => {
            if (field.value.trim()) {
                fieldHandler.setValid(field);
                fieldHandler.hideError(field);
            }
        });
    });

    // Validación de régimen (radio buttons)
    const regimenRadios = form.querySelectorAll('input[name="regimen"]');
    regimenRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            fieldHandler.setValid(radio);
            fieldHandler.hideError(radio.parentElement);
        });
    });

    // Validación de email con debounce
    const emailField = form.querySelector('#email');
    if (emailField) {
        emailField.addEventListener('blur', () => {
            const email = utils.sanitizeInput(emailField.value);
            if (email) {
                utils.debounce(
                    () => validators.validateEmail(email, emailField),
                    CONFIG.VALIDATION_DELAYS.EMAIL,
                    'email'
                );
            }
        });
    }

    // Validación de identificación con debounce
    const identificacionField = form.querySelector('#identificacion');
    if (identificacionField) {
        identificacionField.addEventListener('blur', () => {
            const identification = utils.sanitizeInput(identificacionField.value);
            if (identification) {
                utils.debounce(
                    () => validators.validateIdentification(identification, identificacionField),
                    CONFIG.VALIDATION_DELAYS.IDENTIFICATION,
                    'identification'
                );
            }
        });
    }

    // Validación de registro profesional con debounce
    const registroProfesionalField = form.querySelector('#registroProfesional');
    if (registroProfesionalField) {
        registroProfesionalField.addEventListener('blur', () => {
            const registration = utils.sanitizeInput(registroProfesionalField.value);
            if (registration) {
                utils.debounce(
                    () => validators.validateProfessionalRegistration(registration, registroProfesionalField),
                    CONFIG.VALIDATION_DELAYS.PROFESSIONAL_REGISTRATION,
                    'registration'
                );
            }
        });
    }

    // Formato de teléfono
    const phoneField = form.querySelector('#telefono');
    if (phoneField) {
        phoneField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) value = value.slice(0, 10);
            e.target.value = value;
            
            if (value.length === 10) {
                fieldHandler.setValid(this);
                fieldHandler.hideError(this);
            } else if (value.length > 0 && value.length < 10) {
                fieldHandler.setInvalid(this);
                fieldHandler.showError(this, 'El teléfono debe tener 10 dígitos');
            } else {
                fieldHandler.hideError(this);
            }
        });
    }

    // Formato de NIT
    const nitField = form.querySelector('#nit');
    if (nitField) {
        nitField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^\d\-]/g, '');
            e.target.value = value;
        });
    }

    // Validación de URL
    const webField = form.querySelector('#web');
    if (webField) {
        webField.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url) {
                if (utils.isValidURL(url)) {
                    fieldHandler.setValid(this);
                    fieldHandler.hideError(this);
                } else {
                    fieldHandler.setInvalid(this);
                    fieldHandler.showError(this, 'URL inválida. Debe incluir http:// o https://');
                }
            }
        });
    }

    // Validación de especialidades
    const especialidadCheckboxes = form.querySelectorAll('input[name="especialidad[]"]');
    especialidadCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', validators.validateSpecialties);
    });
}

// Manejo del envío del formulario
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (appState.isSubmitting) {
        return; // Prevenir envíos múltiples
    }

    const form = e.target;
    const submitButton = form.querySelector('.submit-button');
    const confirmationMessage = document.getElementById('confirmation-message');
    
    if (!submitButton || !confirmationMessage) {
        console.error('Elementos del formulario no encontrados');
        return;
    }

    // Validar especialidades primero
    if (!validators.validateSpecialties()) {
        const especialidadContainer = document.querySelector('.checkbox-grid')?.parentElement;
        especialidadContainer?.scrollIntoView({ behavior: 'smooth' });
        return;
    }

    // Estado de carga
    appState.isSubmitting = true;
    submitButton.classList.add('loading');
    submitButton.textContent = 'Enviando...';
    submitButton.disabled = true;
    
    try {
        // Recopilar datos del formulario
        const formData = new FormData(form);
        const data = {};
        
        // Procesar campos normales y especialidades
        for (let [key, value] of formData.entries()) {
            if (key === 'especialidad[]') {
                if (!data.especialidad) {
                    data.especialidad = [];
                }
                data.especialidad.push(utils.sanitizeInput(value));
            } else {
                data[key] = utils.sanitizeInput(value);
            }
        }

        // Validar campos requeridos
        const requiredFields = ['nombre', 'identificacion', 'email', 'telefono', 'direccion', 'registroProfesional', 'nit', 'regimen'];
        const missingFields = requiredFields.filter(field => !data[field] || data[field].trim() === '');
        
        if (missingFields.length > 0) {
            throw new Error(`Los siguientes campos son requeridos: ${missingFields.join(', ')}`);
        }

        // Validaciones adicionales
        if (!utils.isValidEmail(data.email)) {
            throw new Error('El formato del email no es válido');
        }
        
        if (!/^\d{10}$/.test(data.telefono.replace(/\D/g, ''))) {
            throw new Error('El teléfono debe tener 10 dígitos');
        }

        if (!data.especialidad || data.especialidad.length === 0) {
            throw new Error('Debe seleccionar al menos una especialidad');
        }

        // Enviar datos al servidor
        const response = await fetch(`${CONFIG.API_BASE_URL}/register-dentist`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `Error del servidor (${response.status})`);
        }
        
        // Mostrar mensaje de éxito
        showSuccessMessage(confirmationMessage, '¡El formulario se ha enviado correctamente!');
        
        // Resetear formulario
        form.reset();
        fieldHandler.resetAll();
        appState.validationCache.clear();
        
        // Redirigir después del delay configurado
        setTimeout(() => {
            window.location.href = './TheHome.html';
        }, CONFIG.REDIRECT_DELAY);
        
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage(confirmationMessage, error.message || 'Error al enviar el formulario. Por favor, inténtalo de nuevo.');
    } finally {
        // Resetear estado del botón
        appState.isSubmitting = false;
        submitButton.classList.remove('loading');
        submitButton.textContent = 'Registrarme';
        submitButton.disabled = false;
    }
}

// Funciones para mostrar mensajes
function showSuccessMessage(element, message) {
    element.textContent = message;
    element.className = 'success-message';
    element.style.cssText = `
        display: block;
        background-color: #d1fae5;
        color: #047857;
        border: 1px solid #a7f3d0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
    `;
    element.scrollIntoView({ behavior: 'smooth' });
}

function showErrorMessage(element, message) {
    element.textContent = message;
    element.className = 'error-message';
    element.style.cssText = `
        display: block;
        background-color: #fee2e2;
        color: #dc2626;
        border: 1px solid #fecaca;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
    `;
    element.scrollIntoView({ behavior: 'smooth' });
    
    // Ocultar mensaje después del tiempo configurado
    setTimeout(() => {
        element.style.display = 'none';
        element.className = '';
        element.style.cssText = '';
    }, CONFIG.ERROR_DISPLAY_TIME);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeForm);

// Agregar estilos CSS para animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .submit-button.loading {
        cursor: not-allowed;
        opacity: 0.7;
    }
    
    .field-error {
        animation: slideIn 0.3s ease-out;
    }
`;
document.head.appendChild(style);