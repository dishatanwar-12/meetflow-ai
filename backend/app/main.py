import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.clients import router as clients_router
from backend.app.api.v1.projects import router as projects_router
from backend.app.api.v1.meetings import router as meetings_router
from backend.app.api.v1.decisions import router as decisions_router
from backend.app.api.v1.tasks import router as tasks_router
from backend.app.api.v1.risks import router as risks_router
from backend.app.api.v1.questions import router as questions_router
from backend.app.api.v1.exports import router as exports_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.system import router as system_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("meetflow")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing MeetFlow AI backend services and database...")
    await init_db()
    yield
    logger.info("Shutting down MeetFlow AI backend...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Enterprise Meeting-to-Action Tracker with NVIDIA NIM inference and strict uncertainty preservation.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all v1 routers with /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(meetings_router, prefix="/api/v1")
app.include_router(decisions_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(risks_router, prefix="/api/v1")
app.include_router(questions_router, prefix="/api/v1")
app.include_router(exports_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "api_v1": "/api/v1",
        "docs": "/docs",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
