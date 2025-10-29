document.addEventListener('DOMContentLoaded', function() {
    // Doctor data simulation
    // const doctorData = {
    //   name: 'Dra. María González',
    //   speciality: 'Odontología General',
    //   license: 'COL-12345',
    //   email: 'maria.gonzalez@clinica.com',
    //   phone: '+57 300 456 7890',
    //   status: 'available'
    // };

    function loadDoctorProfile() {
        const doctorData = JSON.parse(localStorage.getItem('doctor') || "null");
      
        const nameEl = document.getElementById('doctor-name');
        if (!nameEl) return; // Evita error si falta el elemento
      
        if (doctorData) {
          nameEl.textContent = doctorData.nombre;
          document.getElementById('doctor-speciality').textContent = doctorData.especialidades;
          document.querySelector('.doctor-status').innerHTML = `
            <i class="fas fa-circle ${doctorData.status === 'available' ? 'status-available' : 'status-unavailable'}"></i>
            ${doctorData.status === 'available' ? 'Disponible' : 'No disponible'}
          `;
        } else {
          nameEl.textContent = "Doctor desconocido";
        }
      }
      
    // Sample appointments data
    const appointmentsData = [
      {
        id: 1,
        patient: { name: 'Ana Rodríguez', phone: '300-123-4567', avatar: 'AR' },
        date: '2025-09-06',
        time: '09:00',
        treatment: 'Limpieza Dental',
        status: 'confirmed',
        duration: '45 min'
      },
      {
        id: 2,
        patient: { name: 'Carlos Mendoza', phone: '301-234-5678', avatar: 'CM' },
        date: '2025-09-06',
        time: '10:30',
        treatment: 'Consulta General',
        status: 'pending',
        duration: '30 min'
      },
      {
        id: 3,
        patient: { name: 'Laura Santos', phone: '302-345-6789', avatar: 'LS' },
        date: '2025-09-06',
        time: '11:15',
        treatment: 'Endodoncia',
        status: 'confirmed',
        duration: '90 min'
      },
      {
        id: 4,
        patient: { name: 'Miguel Torres', phone: '303-456-7890', avatar: 'MT' },
        date: '2025-09-06',
        time: '14:00',
        treatment: 'Ortodoncia - Control',
        status: 'confirmed',
        duration: '30 min'
      },
      {
        id: 5,
        patient: { name: 'Sofia Herrera', phone: '304-567-8901', avatar: 'SH' },
        date: '2025-09-06',
        time: '15:30',
        treatment: 'Implante Dental',
        status: 'pending',
        duration: '120 min'
      }
    ];

    // Sample patients data
    const patientsData = [
      {
        id: 1,
        name: 'Ana Rodríguez',
        email: 'ana.rodriguez@email.com',
        phone: '300-123-4567',
        avatar: 'AR',
        visits: 12,
        lastVisit: '2025-08-15',
        nextAppointment: '2025-09-06',
        status: 'active'
      },
      {
        id: 2,
        name: 'Carlos Mendoza',
        email: 'carlos.mendoza@email.com',
        phone: '301-234-5678',
        avatar: 'CM',
        visits: 8,
        lastVisit: '2025-07-22',
        nextAppointment: '2025-09-06',
        status: 'active'
      },
      {
        id: 3,
        name: 'Laura Santos',
        email: 'laura.santos@email.com',
        phone: '302-345-6789',
        avatar: 'LS',
        visits: 15,
        lastVisit: '2025-08-30',
        nextAppointment: '2025-09-06',
        status: 'treatment'
      },
      {
        id: 4,
        name: 'Miguel Torres',
        email: 'miguel.torres@email.com',
        phone: '303-456-7890',
        avatar: 'MT',
        visits: 6,
        lastVisit: '2025-08-10',
        nextAppointment: '2025-09-06',
        status: 'active'
      },
      {
        id: 5,
        name: 'Sofia Herrera',
        email: 'sofia.herrera@email.com',
        phone: '304-567-8901',
        avatar: 'SH',
        visits: 3,
        lastVisit: '2025-08-25',
        nextAppointment: '2025-09-06',
        status: 'new'
      },
      {
        id: 6,
        name: 'Roberto Lima',
        email: 'roberto.lima@email.com',
        phone: '305-678-9012',
        avatar: 'RL',
        visits: 20,
        lastVisit: '2025-08-28',
        nextAppointment: null,
        status: 'inactive'
      }
    ];



    // Initialize dashboard
    function initializeDashboard() {
      loadTodayAppointments();
      updateStats();
      loadPatientsGrid();
      loadAllAppointments();
      
      // Simulate real-time updates
      setInterval(updateStats, 30000);
    }


    
    // Load today's appointments
    function loadTodayAppointments() {
      const tbody = document.getElementById('appointments-tbody');
      const todayAppointments = appointmentsData.filter(apt => apt.date === '2025-09-06');
      
      tbody.innerHTML = todayAppointments.map(appointment => `
        <tr>
          <td>
            <div class="patient-info">
              <div class="patient-avatar">${appointment.patient.avatar}</div>
              <div class="patient-details">
                <h4>${appointment.patient.name}</h4>
                <p>${appointment.patient.phone}</p>
              </div>
            </div>
          </td>
          <td><strong>${appointment.time}</strong></td>
          <td>${appointment.treatment}</td>
          <td>
            <span class="appointment-status status-${appointment.status}">
              ${appointment.status === 'confirmed' ? 'Confirmada' : 
                appointment.status === 'pending' ? 'Pendiente' : 'Cancelada'}
            </span>
          </td>
          <td>
            <div class="appointment-actions">
              <button class="action-btn btn-view" title="Ver detalles">
                <i class="fas fa-eye"></i>
              </button>
              <button class="action-btn btn-edit" title="Editar">
                <i class="fas fa-edit"></i>
              </button>
              <button class="action-btn btn-delete" title="Cancelar">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    // Load all appointments
    function loadAllAppointments() {
      const tbody = document.getElementById('all-appointments-tbody');
      
      tbody.innerHTML = appointmentsData.map(appointment => `
        <tr>
          <td>
            <div class="patient-info">
              <div class="patient-avatar">${appointment.patient.avatar}</div>
              <div class="patient-details">
                <h4>${appointment.patient.name}</h4>
                <p>${appointment.patient.phone}</p>
              </div>
            </div>
          </td>
          <td>
            <div>
              <strong>${formatDate(appointment.date)}</strong><br>
              <span style="color: var(--text-light);">${appointment.time}</span>
            </div>
          </td>
          <td>${appointment.treatment}</td>
          <td>
            <span class="appointment-status status-${appointment.status}">
              ${appointment.status === 'confirmed' ? 'Confirmada' : 
                appointment.status === 'pending' ? 'Pendiente' : 'Cancelada'}
            </span>
          </td>
          <td>${appointment.duration}</td>
          <td>
            <div class="appointment-actions">
              <button class="action-btn btn-view" title="Ver detalles">
                <i class="fas fa-eye"></i>
              </button>
              <button class="action-btn btn-edit" title="Editar">
                <i class="fas fa-edit"></i>
              </button>
              <button class="action-btn btn-delete" title="Cancelar">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    // Load patients grid
    function loadPatientsGrid() {
      const grid = document.getElementById('patients-grid');
      
      grid.innerHTML = patientsData.map(patient => `
        <div class="patient-card">
          <div class="patient-card-header">
            <div class="patient-card-avatar">${patient.avatar}</div>
            <div class="patient-card-info">
              <h4>${patient.name}</h4>
              <p>${patient.email}</p>
            </div>
          </div>
          <div class="patient-stats">
            <div class="patient-stat">
              <div class="patient-stat-value">${patient.visits}</div>
              <div class="patient-stat-label">Visitas</div>
            </div>
            <div class="patient-stat">
              <div class="patient-stat-value">${formatDateShort(patient.lastVisit)}</div>
              <div class="patient-stat-label">Última Visita</div>
            </div>
            <div class="patient-stat">
              <div class="patient-stat-value">
                <span class="appointment-status status-${patient.status}">
                  ${patient.status === 'active' ? 'Activo' : 
                    patient.status === 'treatment' ? 'En Tratamiento' :
                    patient.status === 'new' ? 'Nuevo' : 'Inactivo'}
                </span>
              </div>
              <div class="patient-stat-label">Estado</div>
            </div>
          </div>
          <div class="appointment-actions" style="justify-content: center; padding-top: 1rem;">
            <button class="action-btn btn-view" title="Ver historial">
              <i class="fas fa-file-medical"></i>
            </button>
            <button class="action-btn btn-edit" title="Editar">
              <i class="fas fa-edit"></i>
            </button>
            <button class="quick-action-btn btn-outline" style="padding: 0.5rem 1rem; font-size: 0.8rem;">
              <i class="fas fa-calendar-plus"></i>
              Agendar Cita
            </button>
          </div>
        </div>
      `).join('');
    }



    // Update dashboard stats
    function updateStats() {
      const todayAppointments = appointmentsData.filter(apt => apt.date === '2025-09-06').length;
      document.getElementById('today-appointments').textContent = todayAppointments;
      
      // Simulate some dynamic updates
      const totalPatients = document.getElementById('total-patients');
      if (totalPatients) {
        totalPatients.textContent = patientsData.length;
      }
    }

    // Navigation functionality
    function setupNavigation() {
      const navLinks = document.querySelectorAll('.sidebar-nav a');
      const sections = {
        'dashboard-link': 'dashboard-section',
        'calendar-link': 'calendar-section',
        'appointments-link': 'appointments-section',
        'patients-link': 'patients-section',
        'treatments-link': 'treatments-section',
        'history-link': 'history-section',
        'schedule-link': 'schedule-section',
        'billing-link': 'billing-section',
        'reports-link': 'reports-section',
        'settings-link': 'settings-section'
      };

      navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
          e.preventDefault();
          
          // Update active nav
          navLinks.forEach(l => l.classList.remove('active'));
          this.classList.add('active');
          
          // Hide all sections
          Object.values(sections).forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) section.style.display = 'none';
          });
          
          // Show selected section
          const targetSection = sections[this.id];
          if (targetSection) {
            const section = document.getElementById(targetSection);
            if (section) {
              section.style.display = 'block';
              section.classList.add('fade-in');
              
              // Update header
              updatePageHeader(this.id);
            }
          }
        });
      });
    }

    // Update page header based on section
    function updatePageHeader(linkId) {
      const headerTitle = document.getElementById('page-title');
      const headerSubtitle = document.getElementById('page-subtitle');
      
      const headers = {
        'dashboard-link': {
          title: 'Dashboard Profesional',
          subtitle: 'Resumen de actividad clínica y gestión de pacientes'
        },

        'calendar-link': {
          title: 'Calendario',
          subtitle: 'Gestiona tus citas y eventos'
        },

        'appointments-link': {
          title: 'Gestión de Citas',
          subtitle: 'Administra y organiza todas las citas médicas'
        },
        'patients-link': {
          title: 'Mis Pacientes',
          subtitle: 'Gestiona la información y historial de tus pacientes'
        },
        'treatments-link': {
          title: 'Tratamientos Activos',
          subtitle: 'Seguimiento de todos los tratamientos en curso'
        },
        'history-link': {
          title: 'Historial Clínico',
          subtitle: 'Visualiza el historial médico de tus pacientes'
        },
        'schedule-link': {
          title: 'Horarios de Atención',
          subtitle: 'Gestiona tus horarios de atención semanales'
        },
        'billing-link': {
          title: 'Facturación',
          subtitle: 'Administra facturas y pagos de pacientes'
        },
        'reports-link': {
          title: 'Reportes',
          subtitle: 'Genera reportes y estadísticas de la clínica'
        },
        'settings-link': {
          title: 'Configuración',
          subtitle: 'Ajusta las preferencias de tu cuenta y clínica'
        }
      };
      
      const header = headers[linkId];
      if (header) {
        headerTitle.textContent = header.title;
        headerSubtitle.textContent = header.subtitle;
      }
    }

    // Utility functions
    function formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', { 
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    }

    function formatDateShort(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', { 
        day: 'numeric',
        month: 'short'
      });
    }

    // Mobile menu functionality
    function setupMobileMenu() {
      const menuToggle = document.getElementById('menu-toggle');
      const sidebar = document.querySelector('.sidebar');
      
      if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
          sidebar.classList.toggle('show');
          this.style.transform = sidebar.classList.contains('show') ? 'rotate(90deg)' : 'rotate(0deg)';
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
          if (window.innerWidth <= 768 && 
              !sidebar.contains(e.target) && 
              !menuToggle.contains(e.target)) {
            sidebar.classList.remove('show');
            menuToggle.style.transform = 'rotate(0deg)';
          }
        });
      }
    }

    // Quick actions
    function setupQuickActions() {
      document.getElementById('new-appointment-btn')?.addEventListener('click', function() {
        alert('Funcionalidad: Crear nueva cita\nEsta función abriría un modal para agendar una nueva cita.');
      });

      document.getElementById('new-patient-btn')?.addEventListener('click', function() {
        alert('Funcionalidad: Registrar nuevo paciente\nEsta función abriría un formulario para registrar un nuevo paciente.');
      });
    }

    // Logout functionality
    function setupLogout() {
      const logoutBtn = document.getElementById('logout-btn');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
          e.preventDefault();
          if (confirm('¿Está seguro que desea cerrar sesión?')) {
            alert('Cerrando sesión...');
            setTimeout(() => {
              window.location.href = 'TheHome.html';
            }, 1500);
          }
        });
      }
    }



    
    // Initialize everything
    initializeDashboard();
    setupNavigation();
    setupMobileMenu();
    setupQuickActions();
    setupLogout();
    loadDoctorProfile();

    // Add some interactive feedback
    document.addEventListener('click', function(e) {
      if (e.target.closest('.action-btn')) {
        const btn = e.target.closest('.action-btn');
        btn.style.transform = 'scale(0.95)';
        setTimeout(() => {
          btn.style.transform = 'scale(1)';
        }, 150);
      }
    });

    console.log('✅ Panel profesional del odontólogo inicializado correctamente');
  });