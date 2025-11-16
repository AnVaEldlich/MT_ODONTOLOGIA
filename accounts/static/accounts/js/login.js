        function handleLogin() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                alert('Por favor completa todos los campos');
                return;
            }
            
            alert('Iniciando sesión...\nEsta es una plantilla de demostración.');
        }

        document.getElementById('password').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleLogin();
            }
        });