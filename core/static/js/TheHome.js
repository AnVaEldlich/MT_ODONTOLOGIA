document.addEventListener("DOMContentLoaded", () => {
    // Manejo del formulario de pacientes
    const patientForm = document.getElementById("patient-login-form");
    if (patientForm) {
        patientForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("patient-email").value;
            const password = document.getElementById("patient-password").value;

            // Mostrar indicador de carga
            const submitBtn = document.getElementById("patient-submit-btn");
            const originalText = submitBtn.textContent;
            submitBtn.textContent = "Verificando...";
            submitBtn.disabled = true;

            try {
                const res = await fetch("http://localhost:3000/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });

                const data = await res.json();

                if (data.success) {
                    // Redirigimos al perfil sin usar localStorage
                    // Los datos del usuario se pasarán via URL params o se obtendrán del servidor
                    window.location.href = `perfil.html?userId=${data.user.id}`;
                } else {
                    alert(data.message || "Credenciales inválidas. Verifique su email y contraseña.");
                }
            } catch (err) {
                console.error("Error:", err);
                alert("Error de conexión con el servidor. Intente nuevamente.");
            } finally {
                // Restaurar botón
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Manejo del formulario de doctores
    const doctorForm = document.getElementById("doctor-login-form");
    if (doctorForm) {
        doctorForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("doctor-email").value;
            const identificacion = document.getElementById("doctor-identificacion").value;

            // Mostrar indicador de carga
            const submitBtn = document.getElementById("doctor-submit-btn");
            const originalText = submitBtn.textContent;
            submitBtn.textContent = "Verificando...";
            submitBtn.disabled = true;

            try {
                const res = await fetch("http://localhost:3000/login-dentist", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, identificacion })
                });

                const data = await res.json();

                if (data.success) {
                    // Redirigimos a la página de perfil del odontólogo sin usar localStorage
                    window.location.href = `perfildoctor.html?doctorId=${data.doctor.id}`;
                } else {
                    alert(data.message || "Credenciales inválidas. Verifique su email e identificación.");
                }
            } catch (err) {
                console.error("Error:", err);
                alert("Error de conexión con el servidor. Intente nuevamente.");
            } finally {
                // Restaurar botón
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Manejo de la activación del botón submit para el formulario de pacientes
    if (patientForm) {
        const patientEmail = document.getElementById("patient-email");
        const patientPassword = document.getElementById("patient-password");
        const patientSubmitBtn = document.getElementById("patient-submit-btn");

        const validatePatientForm = () => {
            const emailValid = patientEmail.value.trim() !== "" && 
                              /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(patientEmail.value);
            const passwordValid = patientPassword.value.trim().length >= 6;
            const isValid = emailValid && passwordValid;
            
            patientSubmitBtn.disabled = !isValid;
            if (isValid) {
                patientSubmitBtn.classList.add("valid");
            } else {
                patientSubmitBtn.classList.remove("valid");
            }
        };

        patientEmail.addEventListener("input", validatePatientForm);
        patientPassword.addEventListener("input", validatePatientForm);
        
        // Validar al cargar la página
        validatePatientForm();
    }

    // Manejo de la activación del botón submit para el formulario de doctores
    if (doctorForm) {
        const doctorEmail = document.getElementById("doctor-email");
        const doctorIdentificacion = document.getElementById("doctor-identificacion");
        const doctorSubmitBtn = document.getElementById("doctor-submit-btn");

        const validateDoctorForm = () => {
            const emailValid = doctorEmail.value.trim() !== "" && 
                              /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(doctorEmail.value);
            const idValid = doctorIdentificacion.value.trim().length >= 6;
            const isValid = emailValid && idValid;
            
            doctorSubmitBtn.disabled = !isValid;
            if (isValid) {
                doctorSubmitBtn.classList.add("valid");
            } else {
                doctorSubmitBtn.classList.remove("valid");
            }
        };

        doctorEmail.addEventListener("input", validateDoctorForm);
        doctorIdentificacion.addEventListener("input", validateDoctorForm);
        
        // Validar al cargar la página
        validateDoctorForm();
    }

    // Manejo de la visualización de la contraseña
    const passwordToggle = document.getElementById("patient-password-toggle");
    if (passwordToggle) {
        passwordToggle.addEventListener("click", () => {
            const passwordInput = document.getElementById("patient-password");
            const icon = passwordToggle.querySelector("i");
            
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                icon.classList.remove("fa-eye");
                icon.classList.add("fa-eye-slash");
            } else {
                passwordInput.type = "password";
                icon.classList.remove("fa-eye-slash");
                icon.classList.add("fa-eye");
            }
        });
    }

    // Manejo de las pestañas (tabs)
    const tabs = document.querySelectorAll(".tab-button");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // Remover clase active de todas las pestañas
            tabs.forEach(t => t.classList.remove("active"));
            
            // Agregar clase active a la pestaña clickeada
            tab.classList.add("active");

            // Mostrar el formulario correspondiente
            const formType = tab.dataset.tab;
            const formContainer = document.querySelector(".form-container");
            
            document.querySelectorAll(".form-wrapper").forEach(wrapper => {
                wrapper.classList.add("hidden");
                wrapper.classList.remove("active");
            });

            const targetWrapper = document.getElementById(`${formType}-form-wrapper`);
            if (targetWrapper) {
                targetWrapper.classList.remove("hidden");
                targetWrapper.classList.add("active");
            }

            // Actualizar el estilo del contenedor según el tipo de usuario
            formContainer.className = `form-container ${formType}-mode`;
        });
    });
});