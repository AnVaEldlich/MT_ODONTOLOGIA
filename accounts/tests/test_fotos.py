import io

import pytest
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from accounts.imagenes import MAX_BYTES
from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group


def _jpeg(ancho=80, alto=40, exif=False):
    imagen = Image.new("RGB", (ancho, alto), (11, 116, 144))
    buffer = io.BytesIO()
    opciones = {"format": "JPEG", "quality": 90}
    if exif:
        datos = imagen.getexif()
        datos[274] = 6
        datos[305] = "secreto-exif"
        opciones["exif"] = datos
    imagen.save(buffer, **opciones)
    return SimpleUploadedFile("retrato-original.jpg", buffer.getvalue(), content_type="image/jpeg")


def _png():
    imagen = Image.new("RGB", (90, 90), (15, 122, 69))
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return SimpleUploadedFile("bloque.png", buffer.getvalue(), content_type="image/png")


def _paciente(django_user_model, email, documento):
    user = django_user_model.objects.create_user(
        username=email,
        email=email,
        password="pass12345",
        first_name="Sofía",
        last_name="Núñez",
    )
    assign_paciente_group(user)
    paciente = Paciente.objects.create(
        user=user,
        first_name="Sofía",
        last_name="Núñez",
        id_type="cc",
        id_number=documento,
        birth_date="1991-03-03",
        gender="femenino",
        phone="3001112233",
        address="Calle 10",
        city="Bogotá",
        department="Cundinamarca",
    )
    return user, paciente


def _profesional(django_user_model, email):
    user = django_user_model.objects.create_user(
        username=email,
        email=email,
        password="pass12345",
        first_name="Ana",
        last_name="Torres",
    )
    assign_profesional_group(user)
    profesional = Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=email,
        especialidad="ortodoncia",
        ubicacion="Chapinero",
        telefono="3110000000",
    )
    return user, profesional


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


@pytest.mark.django_db
def test_paciente_guarda_reemplaza_y_quita(client, django_user_model, media):
    user, paciente = _paciente(django_user_model, "foto.pac@test.com", "9101")
    client.force_login(user)
    respuesta = client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": _jpeg(exif=True)})
    assert respuesta.status_code == 302
    paciente.refresh_from_db()
    assert paciente.foto.name.endswith(".jpg")
    assert "retrato-original" not in paciente.foto.name
    guardada = Image.open(paciente.foto.path)
    assert guardada.size == (512, 512)
    assert guardada.format == "JPEG"
    assert 305 not in guardada.getexif()
    anterior = paciente.foto.name
    assert default_storage.exists(anterior)

    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": _png()})
    paciente.refresh_from_db()
    assert paciente.foto.name != anterior
    assert not default_storage.exists(anterior)
    assert Image.open(paciente.foto.path).size == (512, 512)

    client.post(reverse("foto_paciente"), {"campo": "portada", "imagen": _jpeg(ancho=300, alto=80)})
    paciente.refresh_from_db()
    assert Image.open(paciente.portada.path).size == (1500, 500)

    client.post(reverse("foto_paciente"), {"campo": "foto", "accion": "eliminar"})
    paciente.refresh_from_db()
    assert not paciente.foto
    assert not default_storage.exists(anterior)
    assert paciente.portada


@pytest.mark.django_db
def test_profesional_guarda_su_foto(client, django_user_model, media):
    user, profesional = _profesional(django_user_model, "foto.pro@test.com")
    client.force_login(user)
    respuesta = client.post(
        reverse("foto_profesional"),
        {"campo": "portada", "imagen": _jpeg()},
        HTTP_X_REQUESTED_WITH="fetch",
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["ok"] is True
    profesional.refresh_from_db()
    assert profesional.portada
    assert Image.open(profesional.portada.path).size == (1500, 500)


@pytest.mark.django_db
def test_otro_no_cambia_la_foto_ajena(client, django_user_model, media):
    dueno, paciente = _paciente(django_user_model, "dueno.foto@test.com", "9102")
    client.force_login(dueno)
    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": _jpeg()})
    paciente.refresh_from_db()
    nombre = paciente.foto.name

    intruso, _otro = _paciente(django_user_model, "intruso.foto@test.com", "9103")
    client.force_login(intruso)
    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": _png()})
    paciente.refresh_from_db()
    assert paciente.foto.name == nombre
    intruso.paciente.refresh_from_db()
    assert intruso.paciente.foto
    assert intruso.paciente.foto.name != nombre

    pro_user, profesional = _profesional(django_user_model, "pro.foto.ajeno@test.com")
    client.force_login(pro_user)
    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": _jpeg(), "accion": "eliminar"})
    paciente.refresh_from_db()
    assert paciente.foto.name == nombre
    profesional.refresh_from_db()
    assert not profesional.foto

    client.force_login(dueno)
    client.post(reverse("foto_profesional"), {"campo": "foto", "imagen": _jpeg()})
    profesional.refresh_from_db()
    assert not profesional.foto


@pytest.mark.django_db
def test_anonimo_no_sube(client, media):
    respuesta = client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": _jpeg()})
    assert respuesta.status_code == 302
    assert reverse("login") in respuesta.url


@pytest.mark.django_db
def test_rechaza_archivo_falso_extension_y_tamano(client, django_user_model, media):
    user, paciente = _paciente(django_user_model, "malo.foto@test.com", "9104")
    client.force_login(user)
    falso = SimpleUploadedFile("foto.jpg", b"esto no es una imagen", content_type="image/jpeg")
    respuesta = client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": falso}, follow=True)
    assert respuesta.status_code == 200
    assert "no es una imagen" in respuesta.content.decode()
    paciente.refresh_from_db()
    assert not paciente.foto

    gif = io.BytesIO()
    Image.new("RGB", (8, 8), (0, 0, 0)).save(gif, format="GIF")
    disfraz = SimpleUploadedFile("foto.jpg", gif.getvalue(), content_type="image/jpeg")
    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": disfraz})
    paciente.refresh_from_db()
    assert not paciente.foto

    enorme = SimpleUploadedFile("grande.jpg", b"x" * (MAX_BYTES + 1), content_type="image/jpeg")
    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": enorme}, follow=True)
    paciente.refresh_from_db()
    assert not paciente.foto

    svg = SimpleUploadedFile("foto.svg", b"<svg xmlns='http://www.w3.org/2000/svg'/>", content_type="image/svg+xml")
    client.post(reverse("foto_paciente"), {"campo": "foto", "imagen": svg})
    paciente.refresh_from_db()
    assert not paciente.foto
