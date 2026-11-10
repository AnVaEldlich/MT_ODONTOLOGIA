(function () {
    "use strict";

    const mobileMenuToggle = document.getElementById("mobileMenuToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    const mobileBackdrop = document.getElementById("mobileMenuBackdrop");
    const navbar = document.getElementById("navbar");
    const raiz = document.documentElement;

    if (mobileMenuToggle && mobileMenu) {
        let cierreTimer = 0;
        let onCierreEnd = null;

        const menuAbierto = () => mobileMenu.classList.contains("active");

        const syncMenuTop = () => {
            if (!navbar) {
                return;
            }
            const bottom = Math.round(navbar.getBoundingClientRect().bottom);
            raiz.style.setProperty("--mobile-menu-top", `${bottom}px`);
        };

        const cancelarCierrePendiente = () => {
            if (cierreTimer) {
                window.clearTimeout(cierreTimer);
                cierreTimer = 0;
            }
            if (onCierreEnd) {
                mobileMenu.removeEventListener("transitionend", onCierreEnd);
                onCierreEnd = null;
            }
        };

        const closeMobileMenu = () => {
            if (!menuAbierto()) {
                return;
            }
            cancelarCierrePendiente();
            mobileMenuToggle.classList.remove("active");
            mobileMenu.classList.remove("active");
            if (mobileBackdrop) {
                mobileBackdrop.classList.remove("active");
            }
            document.body.classList.remove("menu-abierto");
            mobileMenuToggle.setAttribute("aria-expanded", "false");
            mobileMenuToggle.setAttribute("aria-label", "Abrir menú");

            let finalizado = false;
            const finalizar = () => {
                if (finalizado) {
                    return;
                }
                finalizado = true;
                cancelarCierrePendiente();
                mobileMenu.hidden = true;
                if (mobileBackdrop) {
                    mobileBackdrop.hidden = true;
                }
            };

            onCierreEnd = (event) => {
                if (event.target !== mobileMenu || event.propertyName !== "opacity") {
                    return;
                }
                finalizar();
            };

            mobileMenu.addEventListener("transitionend", onCierreEnd);
            cierreTimer = window.setTimeout(finalizar, 400);
        };

        const openMobileMenu = () => {
            cancelarCierrePendiente();
            syncMenuTop();
            mobileMenu.hidden = false;
            if (mobileBackdrop) {
                mobileBackdrop.hidden = false;
            }
            void mobileMenu.offsetWidth;
            mobileMenuToggle.classList.add("active");
            mobileMenu.classList.add("active");
            if (mobileBackdrop) {
                mobileBackdrop.classList.add("active");
            }
            document.body.classList.add("menu-abierto");
            mobileMenuToggle.setAttribute("aria-expanded", "true");
            mobileMenuToggle.setAttribute("aria-label", "Cerrar menú");
        };

        const toggleMobileMenu = () => {
            if (menuAbierto()) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        };

        mobileMenuToggle.addEventListener("click", (event) => {
            event.stopPropagation();
            toggleMobileMenu();
        });

        if (mobileBackdrop) {
            mobileBackdrop.addEventListener("click", closeMobileMenu);
        }

        document.querySelectorAll(".mobile-nav-links a").forEach((link) => {
            link.addEventListener("click", closeMobileMenu);
        });

        document.addEventListener("click", (event) => {
            if (!menuAbierto()) {
                return;
            }
            if (
                !mobileMenuToggle.contains(event.target) &&
                !mobileMenu.contains(event.target)
            ) {
                closeMobileMenu();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && menuAbierto()) {
                closeMobileMenu();
            }
        });

        window.addEventListener(
            "resize",
            () => {
                if (menuAbierto()) {
                    syncMenuTop();
                }
                if (window.matchMedia("(min-width: 800px)").matches && menuAbierto()) {
                    closeMobileMenu();
                }
            },
            { passive: true }
        );

        window.addEventListener(
            "scroll",
            () => {
                if (menuAbierto()) {
                    syncMenuTop();
                }
            },
            { passive: true }
        );
    }

    const CLAVE_TEMA = "mt-tema";

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

    const avisos = document.querySelector(".site-messages");
    if (avisos) {
        const quitar = (aviso) => {
            if (aviso.classList.contains("is-leaving")) {
                return;
            }
            aviso.classList.add("is-leaving");
            window.setTimeout(() => {
                aviso.remove();
                if (!avisos.querySelector(".alert")) {
                    avisos.remove();
                }
            }, 450);
        };
        avisos.querySelectorAll(".alert-cerrar").forEach((boton) => {
            boton.addEventListener("click", () => quitar(boton.closest(".alert")));
        });
        avisos.querySelectorAll(".alert[data-auto-cerrar]").forEach((aviso) => {
            window.setTimeout(() => quitar(aviso), 2000);
        });
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
