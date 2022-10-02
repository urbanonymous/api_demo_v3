import pytest


@pytest.fixture()
def envvars(monkeypatch):
    # Settings
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("HOST", "http://localhost")
