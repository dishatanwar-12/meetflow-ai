from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.services.nvidia_llm import NvidiaLLMService

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "database_connected": db_ok
    }

@router.get("/providers")
async def provider_status() -> Dict[str, Any]:
    """
    Returns AI provider configuration state without exposing secrets or credentials.
    """
    service = NvidiaLLMService()
    configured = service.is_configured()
    return {
        "provider": "nvidia_nim",
        "base_url": settings.NVIDIA_BASE_URL,
        "model": settings.NVIDIA_MODEL,
        "is_configured": configured,
        "status": "configured" if configured else "missing_api_key",
        "instructions": "Set NVIDIA_API_KEY from build.nvidia.com in environment variables." if not configured else "Ready for inference."
    }

