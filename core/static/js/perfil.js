document.addEventListener('DOMContentLoaded', function() {
    // Obtener datos del usuario del localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    
    // Función para obtener saludo según la hora del día
    function getGreeting() {
        const hour = new Date().getHours();
        if (hour >= 5 && hour < 12) {
            return 'Buenos días';
        } else if (hour >= 12 && hour < 18) {
            return 'Buenas tardes';
        } else {
            return 'Buenas noches';
        }
    }
    
    // Actualizar saludo en el encabezado
    const userGreeting = document.getElementById('user-greeting');
    if (userGreeting) {
        userGreeting.textContent = `${getGreeting()}, ${user.username}`;
    }
    
    if (!user) {
        // Si no hay usuario logueado, redirigir
        window.location.href = "TheHome.html";
    } else {
        // Obtener las iniciales para el avatar
        const getInitials = (name) => {
            return name ? name.charAt(0).toUpperCase() : '?';
        };
        
        const userInitials = getInitials(user.username);
        
        // Actualizar nombre de usuario en el encabezado
        const userNameHeader = document.getElementById('user-name');
        if (userNameHeader) {
            userNameHeader.textContent = user.username || 'Usuario';
        }
        
        // Datos simulados para citas, historial y pagos
        const citasData = [
            {
                id: 1,
                fecha: "2025-09-15",
                hora: "09:00",
                especialista: "Dr. María González",
                tipo: "Limpieza dental",
                estado: "confirmada"
            },
            {
                id: 2,
                fecha: "2025-10-02",
                hora: "14:30",
                especialista: "Dr. Carlos Ramírez",
                tipo: "Consulta general",
                estado: "pendiente"
            },
            {
                id: 3,
                fecha: "2025-08-20",
                hora: "11:00",
                especialista: "Dra. Ana López",
                tipo: "Ortodoncia",
                estado: "completada"
            }
        ];
        
        const historialData = [
            {
                id: 1,
                fecha: "2025-08-20",
                especialista: "Dra. Ana López",
                tratamiento: "Consulta de ortodoncia",
                diagnostico: "Maloclusión clase II",
                notas: "Se recomienda tratamiento ortodóntico con brackets"
            },
            {
                id: 2,
                fecha: "2025-07-15",
                especialista: "Dr. María González",
                tratamiento: "Limpieza dental profunda",
                diagnostico: "Gingivitis leve",
                notas: "Mejorar técnica de cepillado. Control en 6 meses"
            },
            {
                id: 3,
                fecha: "2025-06-10",
                especialista: "Dr. Carlos Ramírez",
                tratamiento: "Empaste dental",
                diagnostico: "Caries en molar inferior derecho",
                notas: "Restauración con resina compuesta. Evolución favorable"
            }
        ];
        
        const pagosData = [
            {
                id: 1,
                fecha: "2025-08-20",
                concepto: "Consulta de ortodoncia",
                monto: 85000,
                estado: "pagado",
                metodoPago: "Tarjeta de crédito"
            },
            {
                id: 2,
                fecha: "2025-09-01",
                concepto: "Limpieza dental",
                monto: 65000,
                estado: "pendiente",
                metodoPago: "-"
            },
            {
                id: 3,
                fecha: "2025-07-15",
                concepto: "Empaste dental",
                monto: 120000,
                estado: "pagado",
                metodoPago: "Efectivo"
            }
        ];

        // Crear sección de perfil
        document.getElementById("perfil-container").innerHTML = `
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="profile-info">
                        <h2 class="profile-name">${user.username || ''} ${user.apellidos || ''}</h2>
                        <p class="profile-role">Paciente</p>
                    </div>
                </div>
                
                <div class="profile-details">
                    <div class="detail-item">
                        <div class="detail-icon">
                            <i class="fas fa-envelope"></i>
                        </div>
                        <div class="detail-content">
                            <div class="detail-label">Correo electrónico</div>
                            <div class="detail-value">${user.email || 'No especificado'}</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-icon">
                            <i class="fas fa-phone"></i>
                        </div>
                        <div class="detail-content">
                            <div class="detail-label">Teléfono</div>
                            <div class="detail-value">${user.telefono || 'No especificado'}</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-icon">
                            <i class="fas fa-venus-mars"></i>
                        </div>
                        <div class="detail-content">
                            <div class="detail-label">Género</div>
                            <div class="detail-value">${user.genero || 'No especificado'}</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-icon">
                            <i class="fas fa-birthday-cake"></i>
                        </div>
                        <div class="detail-content">
                            <div class="detail-label">Edad</div>
                            <div class="detail-value">${user.edad || 'No especificada'} años</div>
                        </div>
                    </div>
                </div>
                
                <div class="profile-actions">
                    <button class="action-button primary-action" id="editar-perfil-btn">
                        <i class="fas fa-edit"></i> Editar perfil
                    </button>
                </div>
            </div>
        `;

        // Crear sección de citas
        document.getElementById('mis-citas-container').innerHTML = `
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-calendar-check"></i>
                    </div>
                    <div class="profile-info">
                        <h2 class="profile-name">Mis Citas</h2>
                        <p class="profile-role">Gestión de citas médicas</p>
                    </div>
                </div>
                
                <div class="citas-list">
                    ${citasData.map(cita => `
                        <div class="detail-item cita-item" data-estado="${cita.estado}">
                            <div class="detail-icon">
                                <i class="fas ${getIconoCita(cita.estado)}"></i>
                            </div>
                            <div class="detail-content">
                                <div class="detail-label">${formatearFecha(cita.fecha)} - ${cita.hora}</div>
                                <div class="detail-value">${cita.tipo} con ${cita.especialista}</div>
                                <div class="detail-status status-${cita.estado}">${cita.estado.toUpperCase()}</div>
                            </div>
                            <div class="cita-actions">
                                ${cita.estado === 'pendiente' ? '<button class="action-button small-action"><i class="fas fa-edit"></i></button>' : ''}
                                ${cita.estado === 'confirmada' ? '<button class="action-button small-action danger"><i class="fas fa-times"></i></button>' : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="profile-actions">
                    <button class="action-button primary-action" id="nueva-cita-btn">
                        <i class="fas fa-plus"></i> Nueva cita
                    </button>
                </div>
            </div>
        `;

        // Crear sección de historial
        const historialContainer = document.createElement('div');
        historialContainer.id = 'historial-container';
        historialContainer.className = 'animate__animated animate__fadeIn';
        historialContainer.innerHTML = `
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-clipboard-list"></i>
                    </div>
                    <div class="profile-info">
                        <h2 class="profile-name">Historial Médico</h2>
                        <p class="profile-role">Registro de consultas y tratamientos</p>
                    </div>
                </div>
                
                <div class="historial-list">
                    ${historialData.map(item => `
                        <div class="detail-item historial-item">
                            <div class="detail-icon">
                                <i class="fas fa-file-medical"></i>
                            </div>
                            <div class="detail-content">
                                <div class="detail-label">${formatearFecha(item.fecha)} - ${item.especialista}</div>
                                <div class="detail-value">${item.tratamiento}</div>
                                <div class="detail-extra">
                                    <strong>Diagnóstico:</strong> ${item.diagnostico}<br>
                                    <strong>Notas:</strong> ${item.notas}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="profile-actions">
                    <button class="action-button primary-action" id="descargar-historial-btn">
                        <i class="fas fa-download"></i> Descargar historial
                    </button>
                </div>
            </div>
        `;

        // Crear sección de pagos
        const pagosContainer = document.createElement('div');
        pagosContainer.id = 'pagos-container';
        pagosContainer.className = 'animate__animated animate__fadeIn';
        pagosContainer.innerHTML = `
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-credit-card"></i>
                    </div>
                    <div class="profile-info">
                        <h2 class="profile-name">Pagos y Facturación</h2>
                        <p class="profile-role">Gestión de pagos y facturas</p>
                    </div>
                </div>
                
                <div class="pagos-summary">
                    <div class="summary-item">
                        <span class="summary-label">Total pagado:</span>
                        <span class="summary-value pagado">$${pagosData.filter(p => p.estado === 'pagado').reduce((sum, p) => sum + p.monto, 0).toLocaleString()}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Pendiente:</span>
                        <span class="summary-value pendiente">$${pagosData.filter(p => p.estado === 'pendiente').reduce((sum, p) => sum + p.monto, 0).toLocaleString()}</span>
                    </div>
                </div>
                
                <div class="pagos-list">
                    ${pagosData.map(pago => `
                        <div class="detail-item pago-item" data-estado="${pago.estado}">
                            <div class="detail-icon">
                                <i class="fas ${pago.estado === 'pagado' ? 'fa-check-circle' : 'fa-clock'}"></i>
                            </div>
                            <div class="detail-content">
                                <div class="detail-label">${formatearFecha(pago.fecha)} - ${pago.concepto}</div>
                                <div class="detail-value">$${pago.monto.toLocaleString()}</div>
                                <div class="detail-extra">
                                    <span class="payment-status status-${pago.estado}">${pago.estado.toUpperCase()}</span>
                                    <span class="payment-method">${pago.metodoPago}</span>
                                </div>
                            </div>
                            <div class="pago-actions">
                                ${pago.estado === 'pendiente' ? '<button class="action-button small-action primary"><i class="fas fa-credit-card"></i></button>' : ''}
                                <button class="action-button small-action"><i class="fas fa-download"></i></button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="profile-actions">
                    <button class="action-button primary-action" id="nuevo-pago-btn">
                        <i class="fas fa-plus"></i> Realizar pago
                    </button>
                </div>
            </div>
        `;

        // Añadir las secciones al DOM (inicialmente ocultas)
        document.querySelector('.main-content').appendChild(historialContainer);
        document.querySelector('.main-content').appendChild(pagosContainer);
        
        // Ocultar todas las secciones inicialmente excepto perfil
        historialContainer.style.display = 'none';
        pagosContainer.style.display = 'none';
        document.getElementById('mis-citas-container').style.display = 'none';

        // Funciones auxiliares
        function getIconoCita(estado) {
            switch(estado) {
                case 'confirmada': return 'fa-check-circle';
                case 'pendiente': return 'fa-clock';
                case 'completada': return 'fa-check-double';
                default: return 'fa-calendar';
            }
        }

        function formatearFecha(fecha) {
            const date = new Date(fecha);
            return date.toLocaleDateString('es-ES', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        }

        // Gestión de navegación
        const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
        
        // Función para mostrar una sección específica
        function showSection(sectionId) {
            // Ocultar todas las secciones
            document.getElementById('perfil-container').style.display = 'none';
            document.getElementById('mis-citas-container').style.display = 'none';
            document.getElementById('historial-container').style.display = 'none';
            document.getElementById('pagos-container').style.display = 'none';
            
            // Remover clase activa de todos los enlaces
            sidebarLinks.forEach(link => link.classList.remove('active'));
            
            // Mostrar la sección seleccionada y activar el enlace
            switch(sectionId) {
                case 'perfil':
                    document.getElementById('perfil-container').style.display = 'block';
                    document.getElementById('perfil-link').classList.add('active');
                    break;
                case 'citas':
                    document.getElementById('mis-citas-container').style.display = 'block';
                    document.getElementById('citas-link').classList.add('active');
                    break;
                case 'historial':
                    document.getElementById('historial-container').style.display = 'block';
                    document.getElementById('historial-link').classList.add('active');
                    break;
                case 'pagos':
                    document.getElementById('pagos-container').style.display = 'block';
                    document.getElementById('pagos-link').classList.add('active');
                    break;
            }
        }

        // Asignar eventos a los enlaces de navegación
        document.getElementById('perfil-link').addEventListener('click', (e) => {
            e.preventDefault();
            showSection('perfil');
        });
        
        document.getElementById('citas-link').addEventListener('click', (e) => {
            e.preventDefault();
            showSection('citas');
        });
        
        document.getElementById('historial-link').addEventListener('click', (e) => {
            e.preventDefault();
            showSection('historial');
        });
        
        document.getElementById('pagos-link').addEventListener('click', (e) => {
            e.preventDefault();
            showSection('pagos');
        });

        // Mostrar perfil por defecto
        showSection('perfil');

        // Eventos específicos
        document.getElementById('editar-perfil-btn').addEventListener('click', () => {
            const currentEmail = user.email || '';
            const currentTelefono = user.telefono || '';
            
            const newEmail = prompt('Ingrese su nuevo correo electrónico:', currentEmail);
            const newTelefono = prompt('Ingrese su nuevo número de teléfono:', currentTelefono);
            
            if (newEmail !== null && newTelefono !== null) {
                user.email = newEmail;
                user.telefono = newTelefono;
                
                localStorage.setItem('user', JSON.stringify(user));
                
                const detailItems = document.querySelectorAll('.detail-item');
                detailItems[0].querySelector('.detail-value').textContent = newEmail || 'No especificado';
                detailItems[1].querySelector('.detail-value').textContent = newTelefono || 'No especificado';
                
                alert('Perfil actualizado correctamente');
            }
        });

        // Botón de menú móvil
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (menuToggle) {
            menuToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });
        }
    }

    // Funcionalidad del botón de cerrar sesión
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
                localStorage.removeItem('user');
                window.location.href = 'TheHome.html';
            }
        });
    }
});

// Establecer la fecha mínima como hoy
document.addEventListener('DOMContentLoaded', function() {
      const today = new Date().toISOString().split('T')[0];
      document.getElementById('fecha').min = today;
      
      // Inicializar el datepicker con opciones
      flatpickr("input[type=date]", {
        locale: "es",
        dateFormat: "Y-m-d",
        minDate: "today"
      });
    });