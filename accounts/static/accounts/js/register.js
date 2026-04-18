        let currentSection = 1;

        function updateSteps() {
            document.querySelectorAll('.step').forEach((step, index) => {
                if (index + 1 <= currentSection) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });

            document.querySelectorAll('.form-section').forEach((section, index) => {
                if (index + 1 === currentSection) {
                    section.classList.add('active');
                } else {
                    section.classList.remove('active');
                }
            });

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function validateSection(sectionNum) {
            const section = document.getElementById(`section${sectionNum}`);
            const inputs = section.querySelectorAll('input[required], select[required]');
            
            for (let input of inputs) {
                if (!input.value.trim()) {
                    input.focus();
                    alert('Por favor completa todos los campos obligatorios');
                    return false;
                }
            }
            return true;
        }

        function nextSection() {
            if (validateSection(currentSection)) {
                if (currentSection < 3) {
                    currentSection++;
                    updateSteps();
                }
            }
        }

        function prevSection() {
            if (currentSection > 1) {
                currentSection--;
                updateSteps();
            }
        }

        function submitForm() {
            if (!validateSection(3)) return;

            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const terms = document.getElementById('terms').checked;

            if (password !== confirmPassword) {
                alert('Las contraseñas no coinciden');
                return;
            }

            if (password.length < 8) {
                alert('La contraseña debe tener al menos 8 caracteres');
                return;
            }

            if (!terms) {
                alert('Debes aceptar los términos y condiciones');
                return;
            }

            alert('¡Registro exitoso!\n\nBienvenido a MT ODONTOLOGIA. Tu sonrisa perfecta nos inspira.\n\nEsta es una plantilla de demostración.');
        }

        document.getElementById('ninguna').addEventListener('change', function() {
            if (this.checked) {
                document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(cb => {
                    if (cb.id !== 'ninguna') cb.checked = false;
                });
            }
        });