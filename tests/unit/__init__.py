from src.settings import Settings, get_settings


def test_get_settings():
    settings = get_settings()
    assert isinstance(settings, Settings)
