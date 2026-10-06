from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import router
from app.database.session import init_db

frontend_dir = Path(__file__).resolve().parent.parent / 'frontend'


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description='AI-powered resource intelligence and waste prevention platform.',
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(router, prefix='/api')


@app.get('/')
def root():
    return FileResponse(frontend_dir / 'dashboard.html')


@app.get('/dashboard/', include_in_schema=False)
def dashboard():
    return FileResponse(frontend_dir / 'dashboard.html')


@app.get('/health')
def health():
    from app.ml.predictor import is_model_loaded

    return {'status': 'healthy', 'model_loaded': is_model_loaded()}


app.mount('/assets', StaticFiles(directory=frontend_dir), name='assets')