from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Opportunity(BaseModel):
    """Detailed information about a discovered opportunity."""
    title: str = Field(description="Title of the opportunity")
    description: str = Field(description="Brief description of the opportunity")
    source: str = Field(description="Source URL or Agency name")
    agency: Optional[str] = Field(description="Agency name")
    sector: str = Field(description="Sector or Domain (e.g., AI/ML, Energy)")
    published_date: Optional[str] = Field(description="Date published (YYYY-MM-DD)")
    openDate: Optional[str] = Field(description="Open date from source")
    closeDate: Optional[str] = Field(description="Close date from source")
    url: Optional[str] = Field(description="Direct link to the opportunity")

class ScoredOpportunity(Opportunity):
    """Opportunity with scoring details."""
    feasibility_score: float = Field(description="Score 1-10")
    impact_score: float = Field(description="Score 1-10")
    alignment_score: float = Field(description="Score 1-10")
    total_score: float = Field(description="Average score")
    justification: str = Field(description="Reasoning for the score")

class OpportunityList(BaseModel):
    """List of discovered opportunities."""
    opportunities: List[Opportunity] = Field(description="List of opportunities")

class ScoredOpportunityList(BaseModel):
    """List of scored opportunities."""
    opportunities: List[ScoredOpportunity] = Field(description="List of scored opportunities")
