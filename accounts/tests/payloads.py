"""Payloads reutilizables para pruebas de accounts.

No contienen secretos reales. Git debe versionarlos: son fixtures de prueba, no datos de producción.
"""


def patient_register_payload(**overrides):
    """Datos del formulario de registro (las 3 secciones de la interfaz)."""
    data = {
        "first_name": "Camila",
        "last_name": "Restrepo",
        "id_type": "cc",
        "id_number": "1020304050",
        "birth_date": "1994-08-21",
        "gender": "femenino",
        "email": "camila.restrepo@test.com",
        "phone": "3005556677",
        "address": "Calle 45 # 12-34 Apto 502",
        "city": "Bogotá",
        "department": "bogota",
        "emergency_contact": "Andrés Restrepo",
        "emergency_phone": "3104445566",
        "eps": "Sura",
        "conditions": ["ninguna"],
        "medications": "",
        "dental_history": "Limpieza anual. Sin tratamientos mayores.",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "terms": "on",
    }
    data.update(overrides)
    return data
