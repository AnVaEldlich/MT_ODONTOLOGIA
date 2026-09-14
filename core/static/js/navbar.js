(function () {
    "use strict";

    const mobileMenuToggle = document.getElementById("mobileMenuToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    const navbar = document.getElementById("navbar");

    if (mobileMenuToggle && mobileMenu) {
        const closeMobileMenu = () => {
            mobileMenuToggle.classList.remove("active");
            mobileMenu.classList.remove("active");
            document.body.style.overflow = "auto";
        };

        const toggleMobileMenu = () => {
            mobileMenuToggle.classList.toggle("active");
            mobileMenu.classList.toggle("active");
            document.body.style.overflow = mobileMenu.classList.contains("active")
                ? "hidden"
                : "auto";
        };

        mobileMenuToggle.addEventListener("click", (event) => {
            event.stopPropagation();
            toggleMobileMenu();
        });

        document.querySelectorAll(".mobile-nav-links a").forEach((link) => {
            link.addEventListener("click", closeMobileMenu);
        });

        document.addEventListener("click", (event) => {
            if (
                !mobileMenuToggle.contains(event.target) &&
                !mobileMenu.contains(event.target)
            ) {
                closeMobileMenu();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && mobileMenu.classList.contains("active")) {
                closeMobileMenu();
            }
        });
    }

    if (navbar) {
        const updateNavbarScroll = () => {
            if (window.scrollY > 50) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        };

        window.addEventListener("scroll", updateNavbarScroll, { passive: true });
        updateNavbarScroll();
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (event) {
            const href = this.getAttribute("href");
            if (!href || href === "#") {
                return;
            }
            const target = document.querySelector(href);
            if (!target) {
                return;
            }
            event.preventDefault();
            const offsetTop = target.offsetTop - 80;
            window.scrollTo({ top: offsetTop, behavior: "smooth" });
        });
    });
})();
