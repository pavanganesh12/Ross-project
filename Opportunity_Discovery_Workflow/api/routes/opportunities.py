"""
Opportunity API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, Dict, Any

from ..schemas.opportunity import (
    ScoredOpportunityResponse,
    ScoredOpportunityListResponse,
)
from ..services.opportunity_service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

# Initialize service
opportunity_service = OpportunityService()


@router.get(
    "",
    response_model=ScoredOpportunityListResponse,
    summary="List Opportunities",
    description="Get a list of all opportunities with optional filters."
)
async def list_opportunities(
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    sector: Optional[str] = Query(default=None, description="Filter by sector/domain"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    min_score: Optional[float] = Query(default=None, ge=0, le=10, description="Minimum total score"),
):
    """
    List all opportunities with pagination and optional filters.
    
    - **limit**: Maximum number of results to return (1-500)
    - **offset**: Number of results to skip for pagination
    - **sector**: Filter by sector/domain name
    - **source**: Filter by data source
    - **min_score**: Only return opportunities with score >= this value
    """
    return opportunity_service.get_all_opportunities(
        limit=limit,
        offset=offset,
        sector=sector,
        source=source,
        min_score=min_score,
    )


@router.get(
    "/top",
    response_model=ScoredOpportunityListResponse,
    summary="Get Top Opportunities",
    description="Get the highest-scoring opportunities."
)
async def get_top_opportunities(
    limit: int = Query(default=10, ge=1, le=50, description="Number of top opportunities"),
    min_score: float = Query(default=7.0, ge=0, le=10, description="Minimum score threshold"),
):
    """
    Get the top-scoring opportunities.
    
    Returns opportunities sorted by total score descending.
    """
    return opportunity_service.get_top_opportunities(limit=limit, min_score=min_score)


@router.get(
    "/statistics",
    response_model=Dict[str, Any],
    summary="Get Statistics",
    description="Get statistics about stored opportunities."
)
async def get_statistics():
    """
    Get overall statistics about opportunities.
    
    Returns counts, score statistics, and distributions by sector and source.
    """
    return opportunity_service.get_statistics()


@router.get(
    "/sectors",
    response_model=Dict[str, int],
    summary="Get Sectors Summary",
    description="Get opportunity counts by sector."
)
async def get_sectors_summary():
    """
    Get a summary of opportunities grouped by sector.
    
    Returns a dictionary with sector names as keys and counts as values.
    """
    return opportunity_service.get_sectors_summary()


@router.get(
    "/sources",
    response_model=Dict[str, int],
    summary="Get Sources Summary",
    description="Get opportunity counts by source."
)
async def get_sources_summary():
    """
    Get a summary of opportunities grouped by source.
    
    Returns a dictionary with source names as keys and counts as values.
    """
    return opportunity_service.get_sources_summary()


@router.get(
    "/sector/{sector}",
    response_model=ScoredOpportunityListResponse,
    summary="Get Opportunities by Sector",
    description="Get all opportunities for a specific sector."
)
async def get_opportunities_by_sector(sector: str):
    """
    Get opportunities filtered by a specific sector.
    
    - **sector**: The sector/domain to filter by
    """
    return opportunity_service.get_opportunities_by_sector(sector)


@router.get(
    "/{opportunity_id}",
    response_model=ScoredOpportunityResponse,
    summary="Get Opportunity",
    description="Get a single opportunity by ID."
)
async def get_opportunity(opportunity_id: int):
    """
    Get a single opportunity by its database ID.
    
    - **opportunity_id**: The unique ID of the opportunity
    """
    opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity with ID {opportunity_id} not found"
        )
    
    return opportunity


@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Opportunity",
    description="Delete an opportunity by ID."
)
async def delete_opportunity(opportunity_id: int):
    """
    Delete an opportunity from the database.
    
    - **opportunity_id**: The unique ID of the opportunity to delete
    """
    deleted = opportunity_service.delete_opportunity(opportunity_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity with ID {opportunity_id} not found"
        )
    
    return None
