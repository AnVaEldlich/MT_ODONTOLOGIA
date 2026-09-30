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
            mobileMenuToggle.setAttribute(
                "aria-expanded",
                mobileMenu.classList.contains("active") ? "true" : "false"
            );
            mobileMenuToggle.setAttribute(
                "aria-label",
                mobileMenu.classList.contains("active") ? "Cerrar menú" : "Abrir menú"
            );
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

    const CLAVE_TEMA = "mt-tema";
    const raiz = document.documentElement;

    const temaActual = () => {
        const fijado = raiz.getAttribute("data-theme");
        if (fijado) {
            return fijado;
        }
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    };

    const aplicarTema = (tema) => {
        raiz.setAttribute("data-theme", tema);
        try {
            localStorage.setItem(CLAVE_TEMA, tema);
        } catch (error) {
            /* Sin almacenamiento disponible: el tema dura la sesión. */
        }
    };

    document.querySelectorAll("[data-tema-toggle]").forEach((boton) => {
        boton.addEventListener("click", () => {
            aplicarTema(temaActual() === "dark" ? "light" : "dark");
        });
    });

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
