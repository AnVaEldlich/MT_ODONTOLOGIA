// main.js - Script principal integrado con backend

// Variables globales
let currentTab = 'patient';

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('main.js cargado correctamente');
    
    // Inicialización
    initApp();
});

// Función principal de inicialización
function initApp() {
    initTabs();
    setupEventListeners();
    setupLogoNavigation();
    setupSidebarNavigation();
    console.log('Aplicación inicializada correctamente');
}

// Función para inicializar las pestañas
function initTabs() {
    // Activar la pestaña por defecto
    switchTab('patient');
}

// Configurar todos los event listeners
function setupEventListeners() {
    // Event listeners para formulario de pacientes
    setupFormListeners('patient');
    
    // Event listeners para formulario de doctores
    setupFormListeners('doctor');
    
    // Botones de cambio de pestaña
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabType = this.getAttribute('data-tab');
            if (tabType) {
                switchTab(tabType);
            }
        });
    });
}

// Configurar event listeners específicos para cada formulario
function setupFormListeners(userType) {
    const prefix = userType; // 'patient' o 'doctor'
    
    // Inputs de validación
    const emailInput = document.getElementById(`${prefix}-email`);
    const passwordInput = document.getElementById(`${prefix}-password`);
    const identificationInput = document.getElementById(`${prefix}-identificacion`); // Para doctores
    
    if (emailInput) {
        emailInput.addEventListener('input', () => validateForm(userType));
        
        // Para pacientes validamos contraseña, para doctores identificación
        if (userType === 'patient' && passwordInput) {
            passwordInput.addEventListener('input', () => validateForm(userType));
        } else if (userType === 'doctor' && identificationInput) {
            identificationInput.addEventListener('input', () => validateForm(userType));
        }
    }
    
    // Botón de toggle de contraseña (solo para pacientes)
    if (userType === 'patient') {
        const toggleBtn = document.getElementById(`${prefix}-password-toggle`);
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => togglePassword(userType));
        }
    }
    
    // Envío del formulario
    const loginForm = document.getElementById(`${prefix}-login-form`);
    if (loginForm) {
        loginForm.addEventListener('submit', (event) => handleSubmit(event, userType));
    }
}

// Configurar navegación del logo
function setupLogoNavigation() {
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.addEventListener('click', function() {
            const currentPage = window.location.pathname.split('/').pop();
            if (currentPage !== 'index.html' && currentPage !== '') {
                window.location.href = '../index.html';
            }
        });
    }
}

// Configurar navegación del sidebar
function setupSidebarNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const currentPage = window.location.pathname.split('/').pop() || 'TheHome.html';
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPage) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Navegación prevenida: ya estás en esta página');
            });
        }
    });
}

// Función para cambiar de pestaña y mostrar el formulario correspondiente
function switchTab(tabType) {
    // Validar tipo de pestaña
    if (!['patient', 'doctor'].includes(tabType)) {
        console.error('Tipo de pestaña inválido:', tabType);
        return;
    }
    
    const tabs = document.querySelectorAll('.tab-button');
    const activeTab = document.querySelector(`[data-tab="${tabType}"]`);
    
    // Remover clase active de todas las pestañas
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Agregar clase active a la pestaña seleccionada
    if (activeTab) {
        activeTab.classList.add('active');
        currentTab = tabType;
        
        // Mostrar el formulario correspondiente
        showForm(tabType);
        
        // Actualizar clase del contenedor
        updateContainerClass(tabType);
        
        // Resetear ambos formularios
        resetForm('patient');
        resetForm('doctor');
        
        console.log(`Pestaña cambiada a: ${tabType}`);
    } else {
        console.error('No se encontró la pestaña:', tabType);
    }
}

// Función para mostrar el formulario correspondiente
function showForm(tabType) {
    const patientWrapper = document.getElementById('patient-form-wrapper');
    const doctorWrapper = document.getElementById('doctor-form-wrapper');
    
    if (tabType === 'patient') {
        patientWrapper.classList.remove('hidden');
        patientWrapper.classList.add('active');
        doctorWrapper.classList.remove('active');
        doctorWrapper.classList.add('hidden');
    } else {
        doctorWrapper.classList.remove('hidden');
        doctorWrapper.classList.add('active');
        patientWrapper.classList.remove('active');
        patientWrapper.classList.add('hidden');
    }
}

// Función para actualizar la clase del contenedor
function updateContainerClass(tabType) {
    const formContainer = document.querySelector('.form-container');
    if (formContainer) {
        formContainer.classList.remove('patient-mode', 'doctor-mode');
        formContainer.classList.add(`${tabType}-mode`);
    }
}

// Función para validar formulario específico
function validateForm(userType) {
    const prefix = userType;
    const emailInput = document.getElementById(`${prefix}-email`);
    const submitBtn = document.getElementById(`${prefix}-submit-btn`);
    const emailError = document.getElementById(`${prefix}-email-error`);
    
    if (!emailInput || !submitBtn) {
        console.warn(`Elementos del formulario ${userType} no encontrados`);
        return;
    }
    
    const email = emailInput.value.trim();
    
    // Validación de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isEmailValid = email && emailRegex.test(email);
    
    // Manejar estado de error del email
    if (email && !isEmailValid) {
        emailInput.classList.add('error');
        if (emailError) emailError.classList.add('show');
    } else {
        emailInput.classList.remove('error');
        if (emailError) emailError.classList.remove('show');
    }
    
    let isSecondFieldValid = false;
    
    if (userType === 'patient') {
        // Para pacientes: validar contraseña
        const passwordInput = document.getElementById(`${prefix}-password`);
        if (passwordInput) {
            const password = passwordInput.value;
            isSecondFieldValid = password.length >= 6;
        }
    } else {
        // Para doctores: validar identificación
        const identificationInput = document.getElementById(`${prefix}-identificacion`);
        if (identificationInput) {
            const identification = identificationInput.value.trim();
            isSecondFieldValid = identification.length >= 6; // Mínimo 6 caracteres para ID
        }
    }
    
    // Habilitar/deshabilitar botón de envío
    const isFormValid = isEmailValid && isSecondFieldValid;
    submitBtn.disabled = !isFormValid;
    
    // Cambiar estilo del botón según validez
    if (isFormValid) {
        submitBtn.classList.add('valid');
    } else {
        submitBtn.classList.remove('valid');
    }
}

// Función para mostrar/ocultar la contraseña (solo para pacientes)
function togglePassword(userType) {
    if (userType !== 'patient') return;
    
    const passwordInput = document.getElementById(`${userType}-password`);
    const toggleButton = document.getElementById(`${userType}-password-toggle`);
    
    if (!passwordInput || !toggleButton) {
        console.warn(`Elementos de toggle de contraseña ${userType} no encontrados`);
        return;
    }
    
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    
    // Actualizar icono del botón
    const icon = toggleButton.querySelector('i');
    if (icon) {
        if (isPassword) {
            icon.className = 'fas fa-eye-slash';
            toggleButton.setAttribute('aria-label', 'Ocultar contraseña');
        } else {
            icon.className = 'fas fa-eye';
            toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
        }
    }
}

// Función para resetear formulario específico
function resetForm(userType) {
    const prefix = userType;
    const form = document.getElementById(`${prefix}-login-form`);
    const submitBtn = document.getElementById(`${prefix}-submit-btn`);
    const emailInput = document.getElementById(`${prefix}-email`);
    const emailError = document.getElementById(`${prefix}-email-error`);
    
    if (form) form.reset();
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.remove('valid');
    }
    
    if (emailInput) emailInput.classList.remove('error');
    
    if (userType === 'patient') {
        const passwordInput = document.getElementById(`${prefix}-password`);
        if (passwordInput && passwordInput.type === 'text') {
            passwordInput.type = 'password';
            const toggleButton = document.getElementById(`${prefix}-password-toggle`);
            if (toggleButton) {
                const icon = toggleButton.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-eye';
                    toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
                }
            }
        }
    }
    
    if (emailError) emailError.classList.remove('show');
    
    console.log(`Formulario ${userType} reseteado`);
}

// Función REAL para manejar el envío del formulario con backend
async function handleSubmit(event, userType) {
    event.preventDefault();
    
    const prefix = userType;
    const emailInput = document.getElementById(`${prefix}-email`);
    const submitBtn = document.getElementById(`${prefix}-submit-btn`);
    
    if (!emailInput || !submitBtn) {
        console.error(`Elementos del formulario ${userType} no encontrados`);
        return;
    }
    
    const email = emailInput.value.trim();
    
    // Validación final antes del envío
    if (!email) {
        showMessage('Por favor, introduce tu email', 'error');
        return;
    }
    
    // Mostrar estado de carga
    const originalText = submitBtn.textContent;
    const loadingText = userType === 'patient' ? 
        'Iniciando sesión...' : 
        'Verificando credenciales...';
    
    submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
    submitBtn.disabled = true;
    
    try {
        if (userType === 'patient') {
            await handlePatientLogin(email, prefix);
        } else {
            await handleDoctorLogin(email, prefix);
        }
        
    } catch (error) {
        console.error('Error en el login:', error);
        showMessage(error.message || 'Error de conexión con el servidor', 'error');
    } finally {
        // Restaurar botón
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            validateForm(userType);
        }, 1000);
    }
}

// Función para manejar login de pacientes
async function handlePatientLogin(email, prefix) {
    const passwordInput = document.getElementById(`${prefix}-password`);
    if (!passwordInput) {
        throw new Error('Campo de contraseña no encontrado');
    }
    
    const password = passwordInput.value;
    
    if (!password || password.length < 6) {
        throw new Error('La contraseña debe tener al menos 6 caracteres');
    }
    
    const response = await fetch("http://localhost:3000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Guardamos datos en localStorage
        localStorage.setItem("user", JSON.stringify(data.user));
        
        showMessage('Inicio de sesión exitoso. Redirigiendo...', 'success');
        
        // Redirigimos al perfil después de 1.5 segundos
        setTimeout(() => {
            window.location.href = "perfil.html";
        }, 1500);
    } else {
        throw new Error(data.message || "Error al iniciar sesión");
    }
}

// Función para manejar login de doctores
async function handleDoctorLogin(email, prefix) {
    const identificationInput = document.getElementById(`${prefix}-identificacion`);
    if (!identificationInput) {
        throw new Error('Campo de identificación no encontrado');
    }
    
    const identificacion = identificationInput.value.trim();
    
    if (!identificacion || identificacion.length < 6) {
        throw new Error('La identificación debe tener al menos 6 caracteres');
    }
    
    const response = await fetch("http://localhost:3000/login-dentist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, identificacion })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Guardamos los datos del odontólogo
        localStorage.setItem("doctor", JSON.stringify(data.doctor));
        
        showMessage('Acceso profesional autorizado. Redirigiendo...', 'success');
        
        // Redirigimos a la página de perfil del odontólogo después de 1.5 segundos
        setTimeout(() => {
            window.location.href = "perfildoctor.html";
        }, 1500);
    } else {
        throw new Error(data.message || "Error al iniciar sesión");
    }
}

// Función para mostrar mensajes al usuario
function showMessage(message, type = 'info') {
    // Crear elemento de mensaje si no existe
    let messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        messageContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 300px;
        `;
        document.body.appendChild(messageContainer);
    }
    
    // Crear mensaje
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.style.cssText = `
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        background-color: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    `;
    messageEl.textContent = message;
    
    messageContainer.appendChild(messageEl);
    
    // Animar entrada
    setTimeout(() => {
        messageEl.style.opacity = '1';
        messageEl.style.transform = 'translateX(0)';
    }, 10);
    
    // Remover después de 4 segundos
    setTimeout(() => {
        messageEl.style.opacity = '0';
        messageEl.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 300);
    }, 4000);
}

// Hacer funciones disponibles globalmente si se necesitan desde el HTML
window.switchTab = switchTab;
window.togglePassword = togglePassword;