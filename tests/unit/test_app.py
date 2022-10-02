from unittest.mock import patch

import pytest

from src.app import VERSION, get_app

BASE_PATH = "src.app"


@pytest.mark.asyncio
async def test_startup():
    app = get_app()
    await app.startup()


@pytest.mark.asyncio
@patch(f"{BASE_PATH}.App.shutdown")
@patch(f"{BASE_PATH}.App.startup")
async def test_context_manager(startup_mock, shutdown_mock):
    app = get_app()
    async with app:
        pass

    startup_mock.assert_awaited_once()
    shutdown_mock.assert_awaited_once()


@patch(f"{BASE_PATH}.App")
def test_get_app(mock_App_cls):
    get_app.cache_clear()

    app = get_app()

    mock_App_cls.assert_called_once_with(title="API Demo v3", version=VERSION)
    assert app == mock_App_cls.return_value


def test_get_app_caches_result():
    assert get_app() is get_app()
