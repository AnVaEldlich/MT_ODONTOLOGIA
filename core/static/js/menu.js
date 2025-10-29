document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');
    const mainContent = document.getElementById('mainContent');
    
    // Toggle sidebar collapse/expand
    
    function toggleSidebar() {
        sidebar.classList.toggle('collapsed');
        // Save state to localStorage
        const isCollapsed = sidebar.classList.contains('collapsed');
    }
    
    
 

    // Add active class to current page link
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref && (linkHref === currentPage || 
            (currentPage === '' && linkHref === 'index.html'))) {
            link.classList.add('active');
        }
        
        // Smooth scroll for anchor links
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    window.scrollTo({
                        top: target.offsetTop - 20,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Handle window resize
    function handleResize() {
        if (window.innerWidth <= 992) {
            sidebar.classList.add('mobile');
            if (!sidebar.classList.contains('collapsed')) {
                sidebar.classList.add('collapsed');
            }
        } else {
            sidebar.classList.remove('mobile');
            
        }
    }
    
    // Initial check
    handleResize();
    
    // Add resize listener
    window.addEventListener('resize', handleResize);
});
