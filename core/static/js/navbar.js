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

    const root = document.getElementById("dd1");
    if (!root) {
        return;
    }

    const btn = root.querySelector(".dd-toggle");
    const menu = root.querySelector(".menu");
    const items = Array.from(root.querySelectorAll(".menu-item"));
    if (!btn || !menu) {
        return;
    }

    const close = () => {
        menu.classList.remove("show");
        btn.setAttribute("aria-expanded", "false");
        document.removeEventListener("click", outsideClick);
        document.removeEventListener("keydown", onKeyDown);
    };

    const open = () => {
        menu.classList.add("show");
        btn.setAttribute("aria-expanded", "true");
        document.addEventListener("click", outsideClick);
        document.addEventListener("keydown", onKeyDown);
    };

    const toggle = () => {
        if (menu.classList.contains("show")) {
            close();
        } else {
            open();
        }
    };

    function outsideClick(event) {
        if (!root.contains(event.target)) {
            close();
        }
    }

    function onKeyDown(event) {
        if (event.key === "Escape") {
            close();
            btn.focus();
        }
        if (event.key === "ArrowDown") {
            event.preventDefault();
            if (!menu.classList.contains("show")) {
                open();
            }
            if (items[0]) {
                items[0].focus();
            }
        }
    }

    btn.addEventListener("click", (event) => {
        event.stopPropagation();
        toggle();
    });

    btn.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            open();
            if (items[0]) {
                items[0].focus();
            }
        }
    });

    items.forEach((item) => {
        item.setAttribute("tabindex", "0");
        item.addEventListener("keydown", (event) => {
            const idx = items.indexOf(event.currentTarget);
            if (event.key === "ArrowDown") {
                event.preventDefault();
                (items[idx + 1] || items[0]).focus();
            }
            if (event.key === "ArrowUp") {
                event.preventDefault();
                (items[idx - 1] || items[items.length - 1]).focus();
            }
            if (event.key === "Enter" || event.key === " ") {
                event.currentTarget.click();
            }
        });
    });
})();
