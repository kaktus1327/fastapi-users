from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import health, logs, users
from app.core.config import get_settings
from app.core.errors import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Users service with request log storage",
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(logs.router)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    index = static_dir / "index.html"

    @app.get("/", include_in_schema=False)
    async def demo_page() -> FileResponse:
        return FileResponse(index)

    return app


app = create_app()
