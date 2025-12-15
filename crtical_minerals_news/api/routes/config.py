"""
Configuration API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any

from ..schemas.config import (
    ConfigResponse,
    SearchQueryPreset,
    MineralsListResponse,
)
from ..services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["Configuration"])

# Initialize service
config_service = ConfigService()


@router.get(
    "",
    response_model=ConfigResponse,
    summary="Get Configuration",
    description="Get current workflow configuration settings."
)
async def get_config():
    """
    Get all configuration settings.
    
    Returns model settings, search parameters, minerals list, and presets.
    """
    return config_service.get_config()


@router.get(
    "/minerals",
    response_model=MineralsListResponse,
    summary="Get Tracked Minerals",
    description="Get list of minerals being tracked."
)
async def get_minerals():
    """Get the list of critical minerals being tracked."""
    return config_service.get_minerals()


@router.get(
    "/presets",
    response_model=List[SearchQueryPreset],
    summary="Get Search Presets",
    description="Get available search query presets with descriptions."
)
async def get_search_presets():
    """Get detailed information about available search presets."""
    return config_service.get_search_presets()


@router.get(
    "/domains",
    response_model=Dict[str, List[str]],
    summary="Get Trusted Domains",
    description="Get trusted domains by category."
)
async def get_trusted_domains():
    """Get the list of trusted domains for each category."""
    return config_service.get_trusted_domains()


@router.get(
    "/regions",
    response_model=List[str],
    summary="Get Geographic Regions",
    description="Get geographic focus regions."
)
async def get_geographic_regions():
    """Get the list of geographic focus regions."""
    return config_service.get_geographic_regions()


@router.get(
    "/sectors",
    response_model=List[str],
    summary="Get Industry Sectors",
    description="Get industry sectors being monitored."
)
async def get_industry_sectors():
    """Get the list of industry sectors."""
    return config_service.get_industry_sectors()


@router.get(
    "/exa",
    response_model=Dict[str, Any],
    summary="Get Exa Configuration",
    description="Get Exa search tool configuration."
)
async def get_exa_config():
    """Get the Exa search configuration parameters."""
    return config_service.get_exa_config()


@router.post(
    "/query/generate",
    response_model=Dict[str, str],
    summary="Generate Custom Query",
    description="Generate a search query for specific minerals."
)
async def generate_custom_query(
    minerals: List[str] = Query(..., min_length=1, description="List of minerals")
):
    """
    Generate a custom search query for specific minerals.
    
    - **minerals**: List of mineral names to include in the query
    """
    query = config_service.generate_custom_query(minerals)
    
    return {
        "minerals": ", ".join(minerals),
        "query": query,
    }
