"""
Pydantic schemas for Opportunity API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OpportunityBase(BaseModel):
    """Base schema for opportunity data."""
    title: str = Field(..., description="Title of the opportunity")
    description: str = Field(..., description="Brief description of the opportunity")
    source: str = Field(..., description="Source URL or Agency name")
    agency: Optional[str] = Field(None, description="Agency name")
    sector: Optional[str] = Field(None, description="Sector or Domain (e.g., AI/ML, Energy)")
    published_date: Optional[str] = Field(None, description="Date published (YYYY-MM-DD)")
    open_date: Optional[str] = Field(None, description="Open date from source")
    close_date: Optional[str] = Field(None, description="Close date from source")
    url: Optional[str] = Field(None, description="Direct link to the opportunity")


class OpportunityCreate(OpportunityBase):
    """Schema for creating a new opportunity."""
    pass


class OpportunityResponse(OpportunityBase):
    """Schema for opportunity response."""
    id: Optional[int] = Field(None, description="Database ID")
    
    class Config:
        from_attributes = True


class ScoredOpportunityResponse(OpportunityResponse):
    """Schema for scored opportunity response."""
    feasibility_score: float = Field(..., ge=0, le=10, description="Feasibility score (0-10)")
    impact_score: float = Field(..., ge=0, le=10, description="Impact score (0-10)")
    alignment_score: float = Field(..., ge=0, le=10, description="Alignment score (0-10)")
    total_score: float = Field(..., ge=0, le=10, description="Total/average score (0-10)")
    justification: Optional[str] = Field(None, description="Reasoning for the score")


class OpportunityListResponse(BaseModel):
    """Schema for list of opportunities response."""
    count: int = Field(..., description="Total number of opportunities")
    opportunities: List[OpportunityResponse] = Field(..., description="List of opportunities")


class ScoredOpportunityListResponse(BaseModel):
    """Schema for list of scored opportunities response."""
    count: int = Field(..., description="Total number of scored opportunities")
    opportunities: List[ScoredOpportunityResponse] = Field(..., description="List of scored opportunities")
    average_score: Optional[float] = Field(None, description="Average score across all opportunities")
    generated_at: datetime = Field(default_factory=datetime.now, description="Timestamp of generation")


class OpportunityFilterParams(BaseModel):
    """Schema for filtering opportunities."""
    sector: Optional[str] = Field(None, description="Filter by sector/domain")
    source: Optional[str] = Field(None, description="Filter by source")
    min_score: Optional[float] = Field(None, ge=0, le=10, description="Minimum total score")
    days_back: Optional[int] = Field(7, ge=1, le=90, description="Number of days to look back")
    limit: Optional[int] = Field(100, ge=1, le=500, description="Maximum results to return")
