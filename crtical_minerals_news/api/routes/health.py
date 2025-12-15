"""
Health check and system status endpoints.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
import os
import sys

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: datetime
    version: str
    service: str


class SystemInfoResponse(BaseModel):
    """System information response schema."""
    python_version: str
    platform: str
    working_directory: str
    outputs_directory_exists: bool
    config_loaded: bool
    agents_available: bool


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy."
)
async def health_check():
    """Perform a basic health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        service="Critical Minerals News API"
    )


@router.get(
    "/ready",
    response_model=Dict[str, Any],
    summary="Readiness Check",
    description="Check if the API is ready to serve requests."
)
async def readiness_check():
    """Verify all required resources are available."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check outputs directory
    outputs_exists = os.path.exists(os.path.join(base_path, "outputs"))
    
    # Check config
    config_ok = False
    try:
        sys.path.insert(0, base_path)
        from config import WorkflowConfig
        config_ok = True
    except:
        pass
    
    # Check agents
    agents_ok = False
    try:
        from agents import news_search_agent
        agents_ok = True
    except:
        pass
    
    checks = {
        "outputs_directory": outputs_exists,
        "config_loaded": config_ok,
        "agents_available": agents_ok,
    }
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
    }


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="System Information",
    description="Get system and environment information."
)
async def system_info():
    """Get system information."""
    import platform
    
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check config
    config_ok = False
    try:
        sys.path.insert(0, base_path)
        from config import WorkflowConfig
        config_ok = True
    except:
        pass
    
    # Check agents
    agents_ok = False
    try:
        from agents import news_search_agent
        agents_ok = True
    except:
        pass
    
    return SystemInfoResponse(
        python_version=sys.version,
        platform=platform.platform(),
        working_directory=os.getcwd(),
        outputs_directory_exists=os.path.exists(os.path.join(base_path, "outputs")),
        config_loaded=config_ok,
        agents_available=agents_ok,
    )
