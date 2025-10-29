// Establecer la fecha mínima como hoy
document.addEventListener('DOMContentLoaded', function() {
const today = new Date().toISOString().split('T')[0];
if (document.getElementById('fecha')) {
    document.getElementById('fecha').min = today;
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
    if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
    }
    });
}, observerOptions);

// Observe fade-in elements
document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
});

// Observe scale-in elements
document.querySelectorAll('.scale-in').forEach(el => {
    observer.observe(el);
});

// Enhanced interactions for clinic cards
document.querySelectorAll('.clinica').forEach(card => {
    card.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-8px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0) scale(1)';
    });
});

// Info cards hover effects
document.querySelectorAll('.info-card').forEach(card => {
    card.addEventListener('click', function() {
    this.style.transform = 'scale(0.98)';
    setTimeout(() => {
        this.style.transform = 'translateY(-5px) scale(1)';
    }, 150);
    });
});

// Feature tags interaction
document.querySelectorAll('.feature-tag').forEach(tag => {
    tag.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.1)';
    this.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
    this.style.color = 'white';
    });
    
    tag.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1)';
    this.style.background = 'linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))';
    this.style.color = '#667eea';
    });
});

// Stats animation on scroll
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
    if (entry.isIntersecting) {
        const statNumbers = entry.target.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
        const finalValue = stat.textContent;
        const isNumber = !isNaN(finalValue.replace(/[+k]/g, ''));
        
        if (isNumber) {
            let currentValue = 0;
            const increment = Math.ceil(parseInt(finalValue.replace(/[+k]/g, '')) / 50);
            const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= parseInt(finalValue.replace(/[+k]/g, ''))) {
                stat.textContent = finalValue;
                clearInterval(timer);
            } else {
                stat.textContent = currentValue + (finalValue.includes('k') ? 'k' : '') + (finalValue.includes('+') ? '+' : '');
            }
            }, 30);
        }
        });
    }
    });
}, { threshold: 0.5 });

// Observe stats section
const statsSection = document.querySelector('.clinicas-stats');
if (statsSection) {
    statsObserver.observe(statsSection);
}
});

