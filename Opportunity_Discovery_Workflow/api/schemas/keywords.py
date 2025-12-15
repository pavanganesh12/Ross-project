"""
Pydantic schemas for Keywords API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class KeywordDomain(BaseModel):
    """Schema for a keyword domain."""
    name: str = Field(..., description="Name of the domain")
    keywords: List[str] = Field(..., description="List of keywords in this domain")
    count: int = Field(..., description="Number of keywords in this domain")


class KeywordsResponse(BaseModel):
    """Schema for keywords response."""
    domains: List[KeywordDomain] = Field(..., description="List of keyword domains")
    total_domains: int = Field(..., description="Total number of domains")
    total_keywords: int = Field(..., description="Total number of keywords across all domains")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    negative_keywords: Optional[List[str]] = Field(None, description="Keywords to exclude")


class KeywordsUpdateRequest(BaseModel):
    """Schema for updating keywords."""
    domain: str = Field(..., description="Domain name to update")
    keywords: List[str] = Field(..., description="New list of keywords for the domain")
    append: bool = Field(
        default=False,
        description="If True, append to existing keywords; if False, replace"
    )


class KeywordAddRequest(BaseModel):
    """Schema for adding a new domain with keywords."""
    domain: str = Field(..., description="New domain name")
    keywords: List[str] = Field(..., description="Keywords for the new domain")


class KeywordDeleteRequest(BaseModel):
    """Schema for deleting keywords or domains."""
    domain: str = Field(..., description="Domain name")
    keywords: Optional[List[str]] = Field(
        None,
        description="Specific keywords to delete (deletes entire domain if not specified)"
    )


class KeywordSearchRequest(BaseModel):
    """Schema for searching keywords."""
    query: str = Field(..., min_length=2, description="Search query")
    domain: Optional[str] = Field(None, description="Limit search to specific domain")
