"""
Pydantic schemas for Report API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ReportSummary(BaseModel):
    """Schema for report summary."""
    filename: str = Field(..., description="Report filename")
    created_at: datetime = Field(..., description="Report creation timestamp")
    size_bytes: int = Field(..., description="File size in bytes")
    size_readable: str = Field(..., description="Human-readable file size")
    

class ReportListResponse(BaseModel):
    """Schema for list of reports response."""
    reports: List[ReportSummary] = Field(..., description="List of reports")
    total_count: int = Field(..., description="Total number of reports")
    output_directory: str = Field(..., description="Reports output directory")


class ReportResponse(BaseModel):
    """Schema for report content response."""
    filename: str = Field(..., description="Report filename")
    content: str = Field(..., description="Report content in markdown")
    created_at: datetime = Field(..., description="Report creation timestamp")
    size_bytes: int = Field(..., description="File size in bytes")
    word_count: int = Field(..., description="Approximate word count")
    

class ReportDeleteResponse(BaseModel):
    """Schema for report deletion response."""
    filename: str = Field(..., description="Deleted report filename")
    message: str = Field(..., description="Deletion status message")


class ReportSearchRequest(BaseModel):
    """Schema for searching reports."""
    keyword: str = Field(..., min_length=2, description="Keyword to search for")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum reports to search")


class ReportSearchResult(BaseModel):
    """Schema for report search result."""
    filename: str = Field(..., description="Report filename")
    matches: List[str] = Field(..., description="Matching text excerpts")
    match_count: int = Field(..., description="Number of matches found")
