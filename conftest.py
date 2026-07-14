import pytest


@pytest.fixture
def client(db):
    from django.test import Client

    return Client()
