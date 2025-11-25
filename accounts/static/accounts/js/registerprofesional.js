// registerprofesional.js

document.addEventListener('DOMContentLoaded', function() {
  // Toggle password visibility
  const togglePassword = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('password');
  const eyeOpen = document.getElementById('eyeOpen');
  const eyeClosed = document.getElementById('eyeClosed');

  if (togglePassword) {
    togglePassword.addEventListener('click', function() {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      eyeOpen.classList.toggle('hidden');
      eyeClosed.classList.toggle('hidden');
    });
  }

  // Update preview in real-time
  const nombreInput = document.getElementById('nombre');
  const apellidosInput = document.getElementById('apellidos');
  const especialidadInput = document.getElementById('especialidad');
  const ubicacionInput = document.getElementById('ubicacion');

  const previewNombre = document.getElementById('previewNombre');
  const previewApellidos = document.getElementById('previewApellidos');
  const previewEspecialidad = document.getElementById('previewEspecialidad');
  const previewUbicacion = document.getElementById('previewUbicacion');
  const previewUbicacion2 = document.getElementById('previewUbicacion2');

  // Update nombre
  if (nombreInput) {
    nombreInput.addEventListener('input', function() {
      previewNombre.textContent = this.value || 'Tu nombre';
    });
  }

  // Update apellidos
  if (apellidosInput) {
    apellidosInput.addEventListener('input', function() {
      const apellidosText = this.value ? ' ' + this.value : '';
      previewApellidos.textContent = apellidosText;
    });
  }

  // Update especialidad
  if (especialidadInput) {
    especialidadInput.addEventListener('change', function() {
      const selectedText = this.options[this.selectedIndex].text;
      previewEspecialidad.textContent = this.value ? selectedText : 'Tu especialidad';
      updatePreviewInfo();
    });
  }

  // Update ubicacion
  if (ubicacionInput) {
    ubicacionInput.addEventListener('input', function() {
      const ubicacionText = this.value || 'Tu ciudad';
      previewUbicacion2.textContent = this.value || 'Ubicación de consulta';
      updatePreviewInfo();
    });
  }

  // Function to update the separator in preview info
  function updatePreviewInfo() {
    const especialidad = especialidadInput.value ? 
      especialidadInput.options[especialidadInput.selectedIndex].text : 'Tu especialidad';
    const ubicacion = ubicacionInput.value || '';
    
    if (ubicacion) {
      previewUbicacion.textContent = ' • ' + ubicacion;
    } else {
      previewUbicacion.textContent = '';
    }
  }

  // Form validation
  const registerForm = document.getElementById('registerForm');
  
  if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
      const password = document.getElementById('password').value;
      
      // Validate password length
      if (password.length < 8) {
        e.preventDefault();
        alert('La contraseña debe tener al menos 8 caracteres.');
        return false;
      }
      
      // Validate terms acceptance
      const aceptaTerminos = document.getElementById('aceptaTerminos');
      if (!aceptaTerminos.checked) {
        e.preventDefault();
        alert('Debes aceptar los términos y condiciones.');
        return false;
      }
      
      // If everything is OK, the form will submit normally
      // Django will handle the POST request
    });
  }

  // Optional: Phone number formatting (Colombia)
  const telefonoInput = document.getElementById('telefono');
  if (telefonoInput) {
    telefonoInput.addEventListener('input', function(e) {
      // Remove all non-numeric characters
      let value = this.value.replace(/\D/g, '');
      
      // Limit to 10 digits (for Colombia)
      if (value.length > 10) {
        value = value.substring(0, 10);
      }
      
      // Format as XXX XXX XXXX
      if (value.length > 6) {
        value = value.substring(0, 3) + ' ' + value.substring(3, 6) + ' ' + value.substring(6);
      } else if (value.length > 3) {
        value = value.substring(0, 3) + ' ' + value.substring(3);
      }
      
      this.value = value;
    });
  }
});