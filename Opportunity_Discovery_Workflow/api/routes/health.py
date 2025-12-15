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
    environment: str


class SystemInfoResponse(BaseModel):
    """System information response schema."""
    python_version: str
    platform: str
    working_directory: str
    database_exists: bool
    keywords_file_exists: bool
    outputs_directory_exists: bool


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy."
)
async def health_check():
    """
    Perform a basic health check.
    
    Returns the current status, timestamp, and version information.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@router.get(
    "/ready",
    response_model=Dict[str, Any],
    summary="Readiness Check",
    description="Check if the API is ready to serve requests."
)
async def readiness_check():
    """
    Perform a readiness check.
    
    Verifies that all required resources are available.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    checks = {
        "database": os.path.exists(os.path.join(base_path, "opportunity_discovery.db")),
        "keywords_file": os.path.exists(r"d:\Agno\keywords.json"),
        "outputs_directory": os.path.exists(os.path.join(base_path, "outputs")),
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
    """
    Get system information.
    
    Returns Python version, platform, and resource availability.
    """
    import platform
    
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return SystemInfoResponse(
        python_version=sys.version,
        platform=platform.platform(),
        working_directory=os.getcwd(),
        database_exists=os.path.exists(os.path.join(base_path, "opportunity_discovery.db")),
        keywords_file_exists=os.path.exists(r"d:\Agno\keywords.json"),
        outputs_directory_exists=os.path.exists(os.path.join(base_path, "outputs")),
    )
