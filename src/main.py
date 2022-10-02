import asyncio

from uvicorn import Config, Server

from src.app import App, get_app
from src.settings import Settings, get_settings


async def _run_server() -> None:
    app: App = get_app()
    async with app:
        settings: Settings = get_settings()
        config = Config(
            app,
            log_config="./logging-conf.yaml",
            port=settings.port,
            host=settings.host,
        )

        server = Server(config=config)
        await server.serve()


def run_server() -> None:
    asyncio.run(_run_server())


if __name__ == "__main__":
    run_server()
