"""
Pydantic schemas for Workflow API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Enum for workflow status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchCategory(str, Enum):
    """Enum for search categories."""
    NEWS = "news"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    ALL = "all"


class WorkflowPhase(str, Enum):
    """Enum for workflow phases."""
    PREPARE = "prepare"
    NEWS_SEARCH = "news_search"
    TWITTER_SEARCH = "twitter_search"
    LINKEDIN_SEARCH = "linkedin_search"
    AGGREGATE = "aggregate"
    FORMAT = "format"
    SAVE = "save"
    PDF_CONVERT = "pdf_convert"


class WorkflowRequest(BaseModel):
    """Schema for workflow execution request."""
    query: Optional[str] = Field(
        default=None,
        description="Custom search query. If not provided, uses default query."
    )
    minerals: Optional[List[str]] = Field(
        default=None,
        description="Specific minerals to search for (e.g., ['lithium', 'cobalt'])"
    )
    categories: List[SearchCategory] = Field(
        default=[SearchCategory.ALL],
        description="Search categories to include (news, twitter, linkedin, or all)"
    )
    preset: Optional[str] = Field(
        default=None,
        description="Use a predefined search query preset (general, lithium, geopolitics, etc.)"
    )
    days_back: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days to look back for content"
    )
    num_results: int = Field(
        default=15,
        ge=5,
        le=50,
        description="Number of results per search category"
    )
    generate_report: bool = Field(
        default=True,
        description="Whether to generate and save a markdown report"
    )


class WorkflowPhaseResult(BaseModel):
    """Schema for individual workflow phase result."""
    phase: WorkflowPhase
    status: WorkflowStatus
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    message: Optional[str] = Field(None, description="Status message")
    results_count: Optional[int] = Field(None, description="Number of results found")


class WorkflowResponse(BaseModel):
    """Schema for workflow execution response."""
    workflow_id: str = Field(..., description="Unique workflow execution ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    message: str = Field(..., description="Status message")
    started_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class WorkflowStatusResponse(BaseModel):
    """Schema for detailed workflow status response."""
    workflow_id: str = Field(..., description="Unique workflow execution ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    current_phase: Optional[WorkflowPhase] = Field(None, description="Current execution phase")
    phases: List[WorkflowPhaseResult] = Field(default=[], description="Results of each phase")
    query_used: Optional[str] = Field(None, description="The search query used")
    categories_searched: List[str] = Field(default=[], description="Categories that were searched")
    started_at: datetime = Field(..., description="Workflow start time")
    completed_at: Optional[datetime] = Field(None, description="Workflow completion time")
    report_filename: Optional[str] = Field(None, description="Generated report filename")
    pdf_filename: Optional[str] = Field(None, description="Generated PDF filename")
    error: Optional[str] = Field(None, description="Error message if failed")


class WorkflowHistoryResponse(BaseModel):
    """Schema for workflow execution history."""
    workflows: List[WorkflowStatusResponse] = Field(..., description="List of workflow executions")
    total_count: int = Field(..., description="Total number of workflow executions")
