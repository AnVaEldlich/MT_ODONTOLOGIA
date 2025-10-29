document.addEventListener('DOMContentLoaded', function() {
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

// Enhanced interactions
document.querySelectorAll('.treatment-tag').forEach(tag => {
    tag.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.05) rotate(1deg)';
    });
    
    tag.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1) rotate(0deg)';
    });
});

document.querySelectorAll('.benefit-card').forEach(card => {
    card.addEventListener('click', function() {
    this.style.transform = 'scale(0.98)';
    setTimeout(() => {
        this.style.transform = 'translateY(-5px) scale(1)';
    }, 150);
    });
});
});

