"""Pruebas de la configuración: sin DEBUG no hay valores inseguros por defecto."""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured

SETTINGS_PATH = Path(__file__).resolve().parents[2] / "Web_odontologia" / "settings.py"
REAL_IS_FILE = Path.is_file

ENV_KEYS = (
    "DEBUG",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "USE_SQLITE",
    "SECURE_SSL_REDIRECT",
    "SECURE_HSTS_SECONDS",
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    "SECURE_HSTS_PRELOAD",
    "SENTRY_DSN",
    "REDIS_URL",
)

PROD_ENV = {
    "SECRET_KEY": "x" * 50,
    "ALLOWED_HOSTS": "clinica.example.com",
    "CSRF_TRUSTED_ORIGINS": "https://clinica.example.com",
    "USE_SQLITE": "True",
}


def load_settings(monkeypatch, **env):
    """Ejecuta settings.py en un módulo aparte, solo con las variables dadas y sin leer .env."""
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(Path, "is_file", lambda self: False)

    spec = importlib.util.spec_from_file_location("settings_under_test", SETTINGS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_debug_es_false_por_defecto(monkeypatch):
    settings = load_settings(monkeypatch, **PROD_ENV)
    assert settings.DEBUG is False


def test_sin_secret_key_y_sin_debug_falla(monkeypatch):
    env = {k: v for k, v in PROD_ENV.items() if k != "SECRET_KEY"}
    with pytest.raises(ImproperlyConfigured, match="SECRET_KEY"):
        load_settings(monkeypatch, **env)


def test_con_debug_sin_secret_key_usa_clave_de_desarrollo(monkeypatch):
    settings = load_settings(monkeypatch, DEBUG="True", USE_SQLITE="True")
    assert settings.DEBUG is True
    assert settings.SECRET_KEY
    assert settings.ALLOWED_HOSTS == ["127.0.0.1", "localhost"]


@pytest.mark.parametrize("hosts", ["", "*", "clinica.example.com,*"])
def test_allowed_hosts_vacio_o_comodin_sin_debug_falla(monkeypatch, hosts):
    with pytest.raises(ImproperlyConfigured, match="ALLOWED_HOSTS"):
        load_settings(monkeypatch, **{**PROD_ENV, "ALLOWED_HOSTS": hosts})


@pytest.mark.parametrize("origins", ["", "*", "https://*"])
def test_csrf_trusted_origins_vacio_o_comodin_sin_debug_falla(monkeypatch, origins):
    with pytest.raises(ImproperlyConfigured, match="CSRF_TRUSTED_ORIGINS"):
        load_settings(monkeypatch, **{**PROD_ENV, "CSRF_TRUSTED_ORIGINS": origins})


def test_csrf_trusted_origins_acepta_subdominio_comodin(monkeypatch):
    settings = load_settings(monkeypatch, **{**PROD_ENV, "CSRF_TRUSTED_ORIGINS": "https://*.onrender.com"})
    assert settings.CSRF_TRUSTED_ORIGINS == ["https://*.onrender.com"]


def test_sin_debug_activa_seguridad_de_produccion(monkeypatch):
    settings = load_settings(monkeypatch, **PROD_ENV)
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SECURE_HSTS_SECONDS == 31536000
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert settings.SECURE_HSTS_PRELOAD is True
    assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.X_FRAME_OPTIONS == "DENY"


def test_sin_debug_permite_ajustar_ssl_y_hsts(monkeypatch):
    settings = load_settings(
        monkeypatch,
        **PROD_ENV,
        SECURE_SSL_REDIRECT="False",
        SECURE_HSTS_SECONDS="3600",
        SECURE_HSTS_INCLUDE_SUBDOMAINS="False",
    )
    assert settings.SECURE_SSL_REDIRECT is False
    assert settings.SECURE_HSTS_SECONDS == 3600
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is False


def test_hsts_seconds_no_numerico_falla(monkeypatch):
    with pytest.raises(ImproperlyConfigured, match="SECURE_HSTS_SECONDS"):
        load_settings(monkeypatch, **PROD_ENV, SECURE_HSTS_SECONDS="un-anio")


def test_con_debug_no_fuerza_https(monkeypatch):
    settings = load_settings(monkeypatch, DEBUG="True", USE_SQLITE="True")
    assert not hasattr(settings, "SECURE_SSL_REDIRECT")
    assert not hasattr(settings, "SESSION_COOKIE_SECURE")
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.X_FRAME_OPTIONS == "DENY"


def test_use_sqlite_es_false_por_defecto_fuera_de_pytest(monkeypatch):
    # settings.py fuerza SQLite si detecta pytest; aquí se simula un proceso normal.
    monkeypatch.delitem(sys.modules, "pytest")
    settings = load_settings(monkeypatch, **{k: v for k, v in PROD_ENV.items() if k != "USE_SQLITE"})
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"


def test_variable_del_entorno_gana_sobre_dotenv(monkeypatch, tmp_path):
    settings = load_settings(monkeypatch, DEBUG="True", USE_SQLITE="True")
    (tmp_path / ".env").write_text("DEBUG=False\nEXTRA_VAR=desde-dotenv\n", encoding="utf-8")
    monkeypatch.setattr(Path, "is_file", REAL_IS_FILE)
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
    monkeypatch.delenv("EXTRA_VAR", raising=False)

    settings._load_dotenv()

    assert os.environ["DEBUG"] == "True"
    assert os.environ["EXTRA_VAR"] == "desde-dotenv"
