/*

TemplateMo 593 personal shape

https://templatemo.com/tm-593-personal-shape

Landing-page animations and contact form UX.
Navbar / mobile menu live in navbar.js (loaded from base.html).

*/

(function () {
    "use strict";

    const observerOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -80px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("animate");
            }
        });
    }, observerOptions);

    const portfolioObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const items = entry.target.querySelectorAll(".portfolio-item");
                    items.forEach((item, index) => {
                        setTimeout(() => {
                            item.classList.add("animate");
                        }, index * 150);
                    });
                }
            });
        },
        { threshold: 0.1 }
    );

    document.addEventListener("DOMContentLoaded", () => {
        document
            .querySelectorAll(".fade-in, .slide-in-left, .slide-in-right")
            .forEach((el) => observer.observe(el));

        const portfolioSection = document.querySelector(".portfolio-grid");
        if (portfolioSection) {
            portfolioObserver.observe(portfolioSection);
        }
    });

    const contactForm = document.querySelector(".contact-form");
    if (contactForm) {
        contactForm.addEventListener("submit", (event) => {
            event.preventDefault();
            const submitBtn = contactForm.querySelector(".submit-btn");
            if (!submitBtn) {
                return;
            }
            const originalText = submitBtn.textContent;

            submitBtn.textContent = "Sending...";
            submitBtn.disabled = true;
            submitBtn.style.background = "linear-gradient(135deg, #94a3b8, #64748b)";

            setTimeout(() => {
                submitBtn.textContent = "Message Sent! ✓";
                submitBtn.style.background = "linear-gradient(135deg, #10b981, #059669)";
                submitBtn.style.transform = "scale(1.05)";
                setTimeout(() => {
                    submitBtn.style.transform = "scale(1)";
                }, 200);

                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.background = "";
                    contactForm.reset();
                }, 3000);
            }, 2000);
        });
    }

    let ticking = false;

    function updateParallax() {
        const hero = document.querySelector(".hero");
        if (hero) {
            const rate = window.pageYOffset * -0.3;
            hero.style.transform = `translateY(${rate}px)`;
        }
        ticking = false;
    }

    window.addEventListener("scroll", () => {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    });

    document.querySelectorAll(".skill-tag").forEach((tag) => {
        tag.addEventListener("mouseenter", () => {
            tag.style.transform = "translateY(-2px) scale(1.05)";
        });
        tag.addEventListener("mouseleave", () => {
            tag.style.transform = "translateY(0) scale(1)";
        });
    });
})();
