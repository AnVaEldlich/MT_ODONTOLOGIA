import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_pytest_desactiva_recarga_del_navegador():
    assert settings.USE_BROWSER_RELOAD is False
    assert settings.USE_LIVERELOAD is False
    assert "django_browser_reload" not in settings.INSTALLED_APPS
    assert "livereload" not in settings.INSTALLED_APPS


@pytest.mark.django_db
def test_home_sigue_respondiendo_sin_recarga(client):
    respuesta = client.get(reverse("home"))
    assert respuesta.status_code == 200
    html = respuesta.content.decode()
    assert "django-browser-reload" not in html
    assert "livereload.js" not in html
