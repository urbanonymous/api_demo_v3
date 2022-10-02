from src.settings import Settings, get_settings


def test_get_settings(envvars):
    settings = get_settings()
    assert isinstance(settings, Settings)
