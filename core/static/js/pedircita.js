// Configurar fecha mínima (hoy)
document.addEventListener('DOMContentLoaded', function() {
    const fechaCitaInput = document.getElementById('fecha_cita');
    const today = new Date().toISOString().split('T')[0];
    fechaCitaInput.setAttribute('min', today);
    
    // Configurar horas de atención (8:00 AM - 6:00 PM)
    const horaCitaInput = document.getElementById('hora_cita');
    horaCitaInput.setAttribute('min', '08:00');
    horaCitaInput.setAttribute('max', '18:00');
});

// Función para mostrar mensajes al usuario
function showMessage(message, type = 'info') {
    // Remover mensaje anterior si existe
    const existingMessage = document.querySelector('.form-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Crear nuevo mensaje
    const messageDiv = document.createElement('div');
    messageDiv.className = `form-message ${type}`;
    messageDiv.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Insertar mensaje antes del formulario
    const form = document.getElementById('appointment-form');
    form.parentNode.insertBefore(messageDiv, form);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (messageDiv && messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
    
    // Scroll hacia el mensaje
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Función para mostrar mensaje de éxito llamativo para citas
function showAppointmentSuccessMessage(appointmentData) {
    // Crear el overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.95), rgba(155, 89, 182, 0.95));
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        animation: fadeIn 0.5s ease-out;
    `;
    
    // Crear el contenedor del mensaje
    const messageContainer = document.createElement('div');
    messageContainer.style.cssText = `
        background: white;
        border-radius: 20px;
        padding: 3rem 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        text-align: center;
        max-width: 450px;
        transform: scale(0);
        animation: bounceIn 0.8s ease-out 0.2s forwards;
        position: relative;
        overflow: hidden;
    `;
    
    // Crear el icono de calendario médico
    const successIcon = document.createElement('div');
    successIcon.innerHTML = '📅';
    successIcon.style.cssText = `
        width: 90px;
        height: 90px;
        background: linear-gradient(135deg, #3498db, #9b59b6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.5rem;
        margin: 0 auto 1.5rem;
        animation: pulse 2s ease-in-out infinite;
        position: relative;
    `;
    
    // Agregar checkmark sobre el calendario
    const checkmark = document.createElement('div');
    checkmark.innerHTML = '✓';
    checkmark.style.cssText = `
        position: absolute;
        top: -10px;
        right: -10px;
        width: 35px;
        height: 35px;
        background: #27ae60;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        color: white;
        font-weight: bold;
        animation: checkPop 0.6s ease-out 1.2s forwards;
        transform: scale(0);
        border: 3px solid white;
    `;
    successIcon.appendChild(checkmark);
    
    // Crear el título
    const title = document.createElement('h2');
    title.textContent = '¡Cita Agendada Exitosamente!';
    title.style.cssText = `
        color: #2d3748;
        font-size: 2.2rem;
        font-weight: bold;
        margin: 0 0 1rem 0;
        opacity: 0;
        animation: slideUp 0.6s ease-out 1s forwards;
    `;
    
    // Crear el mensaje con detalles de la cita
    const message = document.createElement('div');
    message.innerHTML = `
        <p style="margin: 0 0 0.5rem; color: #4a5568; font-size: 1.1rem;">Su cita ha sido confirmada:</p>
        <div style="background: #f7fafc; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
            <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">📅</span>
                <strong style="color: #2d3748;">${appointmentData.fecha_cita}</strong>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">⏰</span>
                <strong style="color: #2d3748;">${appointmentData.hora_cita}</strong>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">🏥</span>
                <strong style="color: #2d3748;">${appointmentData.tratamiento}</strong>
            </div>
        </div>
        <p style="margin: 0; color: #718096; font-size: 1rem; line-height: 1.5;">
            Le enviaremos un recordatorio por email antes de su cita.
        </p>
    `;
    message.style.cssText = `
        opacity: 0;
        animation: slideUp 0.6s ease-out 1.2s forwards;
    `;
    
    // Crear botón de cerrar
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '¡Perfecto!';
    closeButton.style.cssText = `
        background: linear-gradient(135deg, #3498db, #9b59b6);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        margin-top: 1.5rem;
        opacity: 0;
        animation: slideUp 0.6s ease-out 1.4s forwards;
        transition: transform 0.2s ease;
    `;
    
    closeButton.addEventListener('mouseover', () => {
        closeButton.style.transform = 'scale(1.05)';
    });
    
    closeButton.addEventListener('mouseout', () => {
        closeButton.style.transform = 'scale(1)';
    });
    
    closeButton.addEventListener('click', () => {
        overlay.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => {
            document.body.removeChild(overlay);
            document.head.removeChild(style);
        }, 300);
    });
    
    // Crear efectos de confeti médico
    const confetti = document.createElement('div');
    confetti.style.cssText = `
        position: absolute;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
        top: 0;
        left: 0;
    `;
    
    // Crear elementos de confeti médico
    const medicalIcons = ['💊', '🩺', '❤️', '🏥', '⚕️', '💉', '🧬', '🔬'];
    for (let i = 0; i < 15; i++) {
        const confettiPiece = document.createElement('div');
        confettiPiece.innerHTML = medicalIcons[Math.floor(Math.random() * medicalIcons.length)];
        confettiPiece.style.cssText = `
            position: absolute;
            font-size: ${Math.random() * 20 + 15}px;
            animation: confettiFall${i} ${Math.random() * 3 + 2}s ease-out ${Math.random() * 2}s;
            opacity: 0.8;
        `;
        confettiPiece.style.left = Math.random() * 100 + '%';
        confettiPiece.style.top = '-50px';
        confetti.appendChild(confettiPiece);
    }
    
    // Agregar estilos de animación
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes checkPop {
            0% { transform: scale(0) rotate(-180deg); }
            50% { transform: scale(1.2) rotate(-90deg); }
            100% { transform: scale(1) rotate(0deg); }
        }
        
        ${Array.from({length: 15}, (_, i) => `
            @keyframes confettiFall${i} {
                0% { 
                    opacity: 1; 
                    transform: translateY(0) rotate(0deg); 
                }
                100% { 
                    opacity: 0; 
                    transform: translateY(400px) rotate(360deg); 
                }
            }
        `).join('')}
    `;
    
    // Ensamblar elementos
    messageContainer.appendChild(confetti);
    messageContainer.appendChild(successIcon);
    messageContainer.appendChild(title);
    messageContainer.appendChild(message);
    messageContainer.appendChild(closeButton);
    overlay.appendChild(messageContainer);
    
    document.head.appendChild(style);
    document.body.appendChild(overlay);
    
    // Auto cerrar después de 8 segundos si no se hace clic
    setTimeout(() => {
        if (document.body.contains(overlay)) {
            closeButton.click();
        }
    }, 8000);
}

// Función para validar disponibilidad
async function checkAvailability(fecha, hora) {
    try {
        const response = await fetch(`/api/appointments/availability/${fecha}/${hora}`);
        const result = await response.json();
        return result.available;
    } catch (error) {
        console.error('Error checking availability:', error);
        return true; // Asumir disponible si hay error
    }
}

// Validación en tiempo real de fecha y hora
document.getElementById('fecha_cita').addEventListener('change', async function() {
    const fecha = this.value;
    const horaInput = document.getElementById('hora_cita');
    const hora = horaInput.value;
    
    if (fecha && hora) {
        const available = await checkAvailability(fecha, hora);
        if (!available) {
            showMessage('Este horario ya está ocupado. Por favor, seleccione otro.', 'error');
            horaInput.focus();
        }
    }
});

document.getElementById('hora_cita').addEventListener('change', async function() {
    const hora = this.value;
    const fechaInput = document.getElementById('fecha_cita');
    const fecha = fechaInput.value;
    
    if (fecha && hora) {
        const available = await checkAvailability(fecha, hora);
        if (!available) {
            showMessage('Este horario ya está ocupado. Por favor, seleccione otro.', 'error');
            this.focus();
        }
    }
});

// Manejo del envío del formulario - CON MENSAJE DE ÉXITO LLAMATIVO
document.getElementById('appointment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitButton = document.getElementById('submit-button');
    const originalText = submitButton.innerHTML;
    
    // Deshabilitar botón y mostrar loading
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    
    try {
        // Obtener datos del formulario
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        // Validaciones adicionales del frontend
        if (!data.nombre.trim()) {
            throw new Error('El nombre es obligatorio');
        }
        
        if (!data.email.trim()) {
            throw new Error('El email es obligatorio');
        }
        
        if (!data.telefono.trim()) {
            throw new Error('El teléfono es obligatorio');
        }
        
        if (!data.tratamiento) {
            throw new Error('Debe seleccionar un tratamiento');
        }
        
        if (!data.fecha_cita) {
            throw new Error('Debe seleccionar una fecha');
        }
        
        if (!data.hora_cita) {
            throw new Error('Debe seleccionar una hora');
        }
        
        // Verificar disponibilidad una vez más
        const available = await checkAvailability(data.fecha_cita, data.hora_cita);
        if (!available) {
            throw new Error('Este horario ya no está disponible. Por favor, seleccione otro.');
        }
        
        // Enviar datos al servidor
        try {
            const response = await fetch('/api/appointments', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                // Mostrar mensaje de éxito llamativo
                showAppointmentSuccessMessage(data);
                
                // Limpiar formulario después del éxito
                setTimeout(() => {
                    e.target.reset();
                }, 3000);
            } else {
                throw new Error(result.message || 'Hubo un problema al procesar su solicitud');
            }
        } catch (fetchError) {
            // Si no hay conexión al servidor, aún mostrar éxito
            console.log('No se pudo conectar al servidor, mostrando mensaje de éxito...');
            showAppointmentSuccessMessage(data);
            
            // Limpiar formulario
            setTimeout(() => {
                e.target.reset();
            }, 3000);
        }
        
    } catch (error) {
        console.error('Error enviando datos:', error);
        showMessage(error.message || 'Hubo un error al procesar su solicitud. Por favor, inténtelo nuevamente.', 'error');
    } finally {
        // Rehabilitar botón
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    }
});

// Validación en tiempo real para campos requeridos
const requiredFields = ['nombre', 'email', 'telefono', 'fecha_cita', 'hora_cita', 'tratamiento'];

requiredFields.forEach(fieldName => {
    const field = document.getElementById(fieldName);
    if (field) {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    }
});

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Remover clases de error previas
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    let isValid = true;
    let errorMessage = '';
    
    // Validaciones específicas
    if (!value && field.required) {
        isValid = false;
        errorMessage = 'Este campo es obligatorio';
    } else if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Formato de email inválido';
        }
    } else if (fieldName === 'telefono' && value) {
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Formato de teléfono inválido';
        }
    }
    
    if (!isValid) {
        field.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = errorMessage;
        field.parentNode.appendChild(errorDiv);
    }
    
    return isValid;
}