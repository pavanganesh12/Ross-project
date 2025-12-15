"""
Pydantic schemas for Configuration API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class SearchQueryPreset(BaseModel):
    """Schema for search query preset."""
    name: str = Field(..., description="Preset name")
    query: str = Field(..., description="Search query text")
    description: Optional[str] = Field(None, description="Preset description")


class ConfigResponse(BaseModel):
    """Schema for configuration response."""
    model_id: str = Field(..., description="OpenAI model being used")
    exa_num_results: int = Field(..., description="Number of results per search")
    exa_text_length_limit: int = Field(..., description="Text length limit per result")
    exa_category: str = Field(..., description="Default search category")
    critical_minerals: List[str] = Field(..., description="List of tracked minerals")
    default_query: str = Field(..., description="Default search query")
    output_directory: str = Field(..., description="Output directory path")
    report_sections: List[str] = Field(..., description="Report sections")
    geographic_regions: List[str] = Field(..., description="Geographic focus regions")
    industry_sectors: List[str] = Field(..., description="Industry sectors")
    search_presets: Dict[str, str] = Field(..., description="Available search presets")
    trusted_domains: Dict[str, List[str]] = Field(..., description="Trusted domains by category")


class ConfigUpdateRequest(BaseModel):
    """Schema for updating configuration."""
    critical_minerals: Optional[List[str]] = Field(
        None, 
        description="Update the list of tracked minerals"
    )
    exa_num_results: Optional[int] = Field(
        None, 
        ge=5, 
        le=50, 
        description="Number of results per search"
    )
    default_query: Optional[str] = Field(
        None, 
        min_length=10, 
        description="Update the default search query"
    )


class MineralInfo(BaseModel):
    """Schema for mineral information."""
    name: str = Field(..., description="Mineral name")
    common_uses: List[str] = Field(..., description="Common uses/applications")
    key_producers: List[str] = Field(..., description="Major producing countries")


class MineralsListResponse(BaseModel):
    """Schema for list of minerals."""
    minerals: List[str] = Field(..., description="List of tracked minerals")
    count: int = Field(..., description="Number of minerals")
