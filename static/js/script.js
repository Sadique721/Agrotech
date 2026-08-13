/* AgroTech - Main JavaScript */

// Document ready
document.addEventListener('DOMContentLoaded', function () {

    // Mobile Navigation Toggle
    function toggleMenu() {
        const navLinks = document.getElementById('nav-links');
        if (navLinks) {
            navLinks.classList.toggle('active');
        }
    }
    window.toggleMenu = toggleMenu;

    // Close mobile menu when a link is clicked
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            const nav = document.getElementById('nav-links');
            if (nav) nav.classList.remove('active');
        });
    });

    // Smooth appear animation for cards on scroll
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card, .feature-item, .team-member, .function-item').forEach(function (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Scroll to Top
    window.scrollToTop = function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };

    // Auto-dismiss messages
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        });
    }, 4000);
});
