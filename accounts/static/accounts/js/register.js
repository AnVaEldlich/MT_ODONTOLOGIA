(function () {
    "use strict";

    let currentSection = 1;
    const form = document.getElementById("registrationForm");
    if (!form) {
        return;
    }

    form.setAttribute("novalidate", "novalidate");

    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirmPassword");
    const mismatch = document.getElementById("passwordMismatch");

    function passwordsMatch() {
        if (!passwordInput || !confirmInput || !mismatch) {
            return true;
        }
        const password = passwordInput.value;
        const confirmPassword = confirmInput.value;
        const show = confirmPassword.length > 0 && password !== confirmPassword;
        mismatch.hidden = !show;
        confirmInput.setAttribute("aria-invalid", show ? "true" : "false");
        return !show;
    }

    if (passwordInput && confirmInput) {
        passwordInput.addEventListener("input", passwordsMatch);
        confirmInput.addEventListener("input", passwordsMatch);
    }

    function updateSteps() {
        document.querySelectorAll(".step").forEach((step, index) => {
            step.classList.toggle("active", index + 1 <= currentSection);
        });

        document.querySelectorAll(".form-section").forEach((section, index) => {
            section.classList.toggle("active", index + 1 === currentSection);
        });

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function validateSection(sectionNum) {
        const section = document.getElementById("section" + sectionNum);
        if (!section) {
            return false;
        }
        const inputs = section.querySelectorAll("input[required], select[required]");
        for (const input of inputs) {
            if (input.type === "checkbox") {
                if (!input.checked) {
                    input.focus();
                    alert("Por favor completa todos los campos obligatorios");
                    return false;
                }
                continue;
            }
            if (!String(input.value || "").trim()) {
                input.focus();
                alert("Por favor completa todos los campos obligatorios");
                return false;
            }
        }
        return true;
    }

    function nextSection() {
        if (!validateSection(currentSection)) {
            return;
        }
        if (currentSection < 3) {
            currentSection += 1;
            updateSteps();
        }
    }

    function prevSection() {
        if (currentSection > 1) {
            currentSection -= 1;
            updateSteps();
        }
    }

    window.nextSection = nextSection;
    window.prevSection = prevSection;

    const openSection = Number(form.dataset.openSection || 0);
    if (openSection > 1) {
        currentSection = openSection;
        updateSteps();
    }

    form.addEventListener("submit", function (event) {
        if (currentSection !== 3) {
            event.preventDefault();
            return;
        }
        if (!validateSection(3)) {
            event.preventDefault();
            return;
        }

        const terms = document.getElementById("terms");

        if (!passwordsMatch()) {
            event.preventDefault();
            confirmInput.focus();
            return;
        }
        const password = passwordInput.value;
        if (password.length < 8) {
            event.preventDefault();
            alert("La contraseña debe tener al menos 8 caracteres");
            return;
        }
        if (terms && !terms.checked) {
            event.preventDefault();
            alert("Debes aceptar los términos y condiciones");
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = "Creando cuenta...";
        }
    });

    const ninguna = document.getElementById("ninguna");
    if (ninguna) {
        ninguna.addEventListener("change", function () {
            if (!this.checked) {
                return;
            }
            document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach((cb) => {
                if (cb.id !== "ninguna") {
                    cb.checked = false;
                }
            });
        });
    }
})();
