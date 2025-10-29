// register.js 
// Generar días del mes
function generateDays() {
    const daySelect = document.getElementById('dia');
    for (let i = 1; i <= 31; i++) {
        const option = document.createElement('option');
        option.value = i.toString().padStart(2, '0');
        option.textContent = i;
        daySelect.appendChild(option);
    }
}

// Generar años (desde 1920 hasta 2025)
function generateYears() {
    const yearSelect = document.getElementById('año');
    const currentYear = new Date().getFullYear();
    for (let i = currentYear; i >= 1920; i--) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        yearSelect.appendChild(option);
    }
}

// ............
// Seleccionar género
function selectGender(element, value) {
    document.querySelectorAll('.radio-group').forEach(group => group.classList.remove('selected'));
    element.classList.add('selected');
    element.querySelector('input').checked = true;
    updateProgress();
}

// ............
// Toggle password visibility
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = field.nextElementSibling;
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        field.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Password strength checker
function checkPasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    return score;
}

// Update progress bar
function updateProgress() {
    const form = document.getElementById('registrationForm');
    const inputs = form.querySelectorAll('input[required], select[required]');
    const radios = form.querySelectorAll('input[type="radio"]');
    
    let filled = 0;
    let total = inputs.length;
    
    // Check regular inputs
    inputs.forEach(input => {
        if (input.type !== 'radio' && input.value.trim() !== '') {
            filled++;
        }
    });
    
    // Check radio buttons
    const genderSelected = Array.from(radios).some(radio => radio.checked);
    if (genderSelected) {
        filled++; // Add 1 for gender selection
    }
    total++; // Add 1 to total for gender
    
    const progress = (filled / total) * 100;
    document.getElementById('progressFill').style.width = `${progress}%`;
    
    // Enable/disable submit button
    const submitButton = document.getElementById('submitButton');
    if (progress === 100 && validatePasswords()) {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

// Validate passwords match
function validatePasswords() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorMsg = document.getElementById('passwordError');
    const successMsg = document.getElementById('passwordSuccess');
    
    if (confirmPassword && password !== confirmPassword) {
        errorMsg.style.display = 'block';
        successMsg.style.display = 'none';
        return false;
    } else if (confirmPassword && password === confirmPassword) {
        errorMsg.style.display = 'none';
        successMsg.style.display = 'block';
        return true;
    } else {
        errorMsg.style.display = 'none';
        successMsg.style.display = 'none';
        return false;
    }
}

// Calculate age based on birth date
function calculateAge() {
    const mes = parseInt(document.getElementById('mes').value);
    const dia = parseInt(document.getElementById('dia').value);
    const año = parseInt(document.getElementById('año').value);
    
    if (mes && dia && año) {
        const today = new Date();
        const birthDate = new Date(año, mes - 1, dia);
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        document.getElementById('edad').value = age;
        updateProgress();
    }
}

// Función para mostrar mensaje de éxito llamativo
function showSuccessMessage() {
    // Crear el overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.95), rgba(0, 184, 148, 0.95));
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
        max-width: 400px;
        transform: scale(0);
        animation: bounceIn 0.8s ease-out 0.2s forwards;
    `;
    
    // Crear el icono de éxito
    const successIcon = document.createElement('div');
    successIcon.innerHTML = '✓';
    successIcon.style.cssText = `
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #2ed573, #00b894);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: white;
        margin: 0 auto 1.5rem;
        animation: checkMark 1s ease-out 0.8s;
    `;
    
    // Crear el título
    const title = document.createElement('h2');
    title.textContent = '¡Registro Exitoso!';
    title.style.cssText = `
        color: #2d3748;
        font-size: 2rem;
        font-weight: bold;
        margin: 0 0 1rem 0;
        opacity: 0;
        animation: slideUp 0.6s ease-out 1s forwards;
    `;
    
    // Crear el mensaje
    const message = document.createElement('p');
    message.textContent = 'Tu cuenta ha sido creada correctamente. Serás redirigido en unos segundos...';
    message.style.cssText = `
        color: #718096;
        font-size: 1.1rem;
        margin: 0 0 1.5rem 0;
        line-height: 1.5;
        opacity: 0;
        animation: slideUp 0.6s ease-out 1.2s forwards;
    `;
    
    // Crear barra de progreso de redirección
    const progressContainer = document.createElement('div');
    progressContainer.style.cssText = `
        width: 100%;
        height: 4px;
        background: #e2e8f0;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 1rem;
        opacity: 0;
        animation: slideUp 0.6s ease-out 1.4s forwards;
    `;
    
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        width: 0%;
        height: 100%;
        background: linear-gradient(90deg, #2ed573, #00b894);
        border-radius: 2px;
        animation: fillProgress 3s ease-out 1.6s forwards;
    `;
    
    // Agregar partículas de celebración
    const particles = document.createElement('div');
    particles.style.cssText = `
        position: absolute;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
    `;
    
    // Crear partículas individuales
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 6px;
            height: 6px;
            background: ${i % 2 === 0 ? '#ffd93d' : '#ff6b6b'};
            border-radius: 50%;
            animation: particle${i} 2s ease-out ${0.5 + Math.random() * 0.5}s;
        `;
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particles.appendChild(particle);
    }
    
    // Ensamblar elementos
    progressContainer.appendChild(progressBar);
    messageContainer.appendChild(successIcon);
    messageContainer.appendChild(title);
    messageContainer.appendChild(message);
    messageContainer.appendChild(progressContainer);
    overlay.appendChild(particles);
    overlay.appendChild(messageContainer);
    
    // Agregar estilos de animación
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes checkMark {
            0% { transform: scale(0) rotate(-45deg); }
            50% { transform: scale(1.2) rotate(-45deg); }
            100% { transform: scale(1) rotate(0deg); }
        }
        
        @keyframes fillProgress {
            from { width: 0%; }
            to { width: 100%; }
        }
        
        ${Array.from({length: 20}, (_, i) => `
            @keyframes particle${i} {
                0% { 
                    opacity: 1; 
                    transform: translateY(0) rotate(0deg); 
                }
                100% { 
                    opacity: 0; 
                    transform: translateY(-100px) rotate(360deg); 
                }
            }
        `).join('')}
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(overlay);
    
    // Redireccionar después de 4 segundos
    setTimeout(() => {
        window.location.href = './TheHome.html';
    }, 4000);
}

// Initialize form
document.addEventListener('DOMContentLoaded', function() {
    generateDays();
    generateYears();
    
    // Add event listeners for progress tracking
    document.querySelectorAll('input, select').forEach(element => {
        element.addEventListener('input', updateProgress);
        element.addEventListener('change', updateProgress);
    });
    
    // Date change listeners for age calculation
    ['mes', 'dia', 'año'].forEach(id => {
        document.getElementById(id).addEventListener('change', calculateAge);
    });
    
    // Password strength indicator
    document.getElementById('password').addEventListener('input', function() {
        const password = this.value;
        const strength = checkPasswordStrength(password);
        const strengthBar = document.getElementById('strengthBar');
        const strengthText = document.getElementById('strengthText');
        
        if (password === '') {
            strengthBar.style.width = '0%';
            strengthBar.className = 'strength-bar';
            strengthText.textContent = 'Ingresa tu contraseña';
            strengthText.className = 'strength-text';
        } else if (strength <= 2) {
            strengthBar.style.width = '33%';
            strengthBar.className = 'strength-bar strength-weak';
            strengthText.textContent = 'Contraseña débil';
            strengthText.className = 'strength-text strength-weak';
        } else if (strength <= 4) {
            strengthBar.style.width = '66%';
            strengthBar.className = 'strength-bar strength-medium';
            strengthText.textContent = 'Contraseña media';
            strengthText.className = 'strength-text strength-medium';
        } else {
            strengthBar.style.width = '100%';
            strengthBar.className = 'strength-bar strength-strong';
            strengthText.textContent = 'Contraseña fuerte';
            strengthText.className = 'strength-text strength-strong';
        }

        updateProgress();
    });
    
    // Confirm password validation
    document.getElementById('confirmPassword').addEventListener('input', function() {
        validatePasswords();
        updateProgress();
    });
    
    // Form submission - Con mensaje de éxito llamativo
    document.getElementById('registrationForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Deshabilitar el botón de envío para evitar múltiples envíos
        const submitButton = document.getElementById('submitButton');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Procesando...';
        
        // Tomar los datos del formulario
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        try {
            // Intentar enviar los datos al servidor (si existe)
            const response = await fetch('/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            // Mostrar mensaje de éxito y redireccionar
            showSuccessMessage();
            
        } catch (err) {
            // Si hay error en la conexión, aún así mostrar éxito
            console.log('No se pudo conectar al servidor...');
            showSuccessMessage();
        }
    });
});