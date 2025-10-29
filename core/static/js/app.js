// Import utilities
import { utils } from './utils.js';

// App Configuration
const config = {
    apiBaseUrl: '/api',
    animationDuration: 300,
    debounceDelay: 300
};

// App State Management
const state = {
    currentUser: null,
    isAuthenticated: false,
    notifications: [],
    theme: 'light'
};

// Event Bus for component communication
class EventBus {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }

    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }
}

const eventBus = new EventBus();

// UI Components
const UI = {
    // Toast notification system
    toast: {
        show(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type} fade-in`;
            toast.textContent = message;
            
            document.body.appendChild(toast);
            
            setTimeout(() => {
                utils.animation.fadeOut(toast);
                setTimeout(() => toast.remove(), config.animationDuration);
            }, 3000);
        }
    },

    // Modal system
    modal: {
        show(content) {
            const modal = utils.dom.qs('.modal');
            const modalContent = utils.dom.qs('.modal-content');
            
            modalContent.innerHTML = content;
            utils.animation.fadeIn(modal);
        },
        
        hide() {
            const modal = utils.dom.qs('.modal');
            utils.animation.fadeOut(modal);
        }
    },

    // Form handling
    forms: {
        validate(form) {
            const inputs = form.querySelectorAll('input, select, textarea');
            let isValid = true;
            
            inputs.forEach(input => {
                const { type, value, required } = input;
                
                if (required && utils.validation.isEmpty(value)) {
                    this.showError(input, 'Este campo es requerido');
                    isValid = false;
                } else if (type === 'email' && !utils.validation.isEmail(value)) {
                    this.showError(input, 'Email inválido');
                    isValid = false;
                }
            });
            
            return isValid;
        },
        
        showError(input, message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = message;
            
            input.parentNode.appendChild(errorDiv);
            utils.addClass(input, 'input-error');
            
            input.addEventListener('input', () => {
                errorDiv.remove();
                utils.removeClass(input, 'input-error');
            }, { once: true });
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    const savedTheme = utils.storage.get('theme') || 'light';
    document.body.dataset.theme = savedTheme;
    state.theme = savedTheme;

    // Setup event listeners
    setupEventListeners();
    
    // Check authentication status
    checkAuth();
});

// Event listeners setup
function setupEventListeners() {
    // Theme toggle
    const themeToggle = utils.dom.qs('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const newTheme = state.theme === 'light' ? 'dark' : 'light';
            document.body.dataset.theme = newTheme;
            state.theme = newTheme;
            utils.storage.set('theme', newTheme);
        });
    }

    // Form submissions
    utils.dom.qsa('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (UI.forms.validate(form)) {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                try {
                    const response = await utils.api.fetch(form.action, {
                        method: 'POST',
                        body: JSON.stringify(data)
                    });
                    
                    UI.toast.show('¡Operación exitosa!', 'success');
                    eventBus.emit('formSubmitted', response);
                } catch (error) {
                    UI.toast.show('Error al procesar la solicitud', 'error');
                }
            }
        });
    });
}

// Authentication check
async function checkAuth() {
    try {
        const user = await utils.api.fetch(`${config.apiBaseUrl}/auth/status`);
        if (user) {
            state.currentUser = user;
            state.isAuthenticated = true;
            eventBus.emit('auth:changed', { user });
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}
