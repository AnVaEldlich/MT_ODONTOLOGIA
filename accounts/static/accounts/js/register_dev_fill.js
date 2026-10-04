/**
 * Relleno rápido del registro de paciente (solo desarrollo).
 * No se usa en producción: el template solo lo carga con DEBUG.
 */
(function () {
    "use strict";

    const fillBtn = document.getElementById("devFillRegister");
    if (!fillBtn) {
        return;
    }

    const sample = {
        firstName: "Camila",
        lastName: "Restrepo",
        idType: "cc",
        idNumber: String(Date.now()).slice(-10),
        birthDate: "1994-08-21",
        gender: "femenino",
        email: "camila." + Date.now() + "@test.com",
        phone: "3005556677",
        address: "Calle 45 # 12-34 Apto 502",
        city: "Bogotá",
        department: "bogota",
        emergencyContact: "Andrés Restrepo",
        emergencyPhone: "3104445566",
        eps: "Sura",
        medications: "",
        dentalHistory: "Limpieza anual. Sin tratamientos mayores.",
        password: "testpass123",
        confirmPassword: "testpass123",
    };

    function setValue(id, value) {
        const el = document.getElementById(id);
        if (!el) {
            return;
        }
        el.value = value;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    fillBtn.addEventListener("click", function () {
        setValue("firstName", sample.firstName);
        setValue("lastName", sample.lastName);
        setValue("idType", sample.idType);
        setValue("idNumber", sample.idNumber);
        setValue("birthDate", sample.birthDate);
        setValue("gender", sample.gender);
        setValue("email", sample.email);
        setValue("phone", sample.phone);
        setValue("address", sample.address);
        setValue("city", sample.city);
        setValue("department", sample.department);
        setValue("emergencyContact", sample.emergencyContact);
        setValue("emergencyPhone", sample.emergencyPhone);
        setValue("eps", sample.eps);
        setValue("medications", sample.medications);
        setValue("dentalHistory", sample.dentalHistory);
        setValue("password", sample.password);
        setValue("confirmPassword", sample.confirmPassword);

        const ninguna = document.getElementById("ninguna");
        if (ninguna) {
            ninguna.checked = true;
            ninguna.dispatchEvent(new Event("change", { bubbles: true }));
        }

        const terms = document.getElementById("terms");
        if (terms) {
            terms.checked = true;
        }

        fillBtn.textContent = "Formulario rellenado";
        fillBtn.disabled = true;
    });
})();
