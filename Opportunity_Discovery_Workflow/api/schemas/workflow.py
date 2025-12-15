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


class WorkflowPhase(str, Enum):
    """Enum for workflow phases."""
    FETCH = "fetch"
    AGGREGATE = "aggregate"
    FILTER = "filter"
    SCORE = "score"
    REPORT = "report"
    PDF_CONVERT = "pdf_convert"


class DataSource(str, Enum):
    """Enum for data sources."""
    SIMPLER_GRANTS = "simpler_grants"
    GRANTS_GOV = "grants_gov"
    SAM_GOV = "sam_gov"
    ALL = "all"


class WorkflowRequest(BaseModel):
    """Schema for workflow execution request."""
    sources: List[DataSource] = Field(
        default=[DataSource.ALL],
        description="Data sources to fetch from"
    )
    days_back: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days to look back for opportunities"
    )
    domains: Optional[List[str]] = Field(
        default=None,
        description="Specific domains to filter by (uses all if not specified)"
    )
    generate_report: bool = Field(
        default=True,
        description="Whether to generate a markdown report"
    )
    save_to_db: bool = Field(
        default=True,
        description="Whether to save results to database"
    )


class WorkflowPhaseResult(BaseModel):
    """Schema for individual workflow phase result."""
    phase: WorkflowPhase
    status: WorkflowStatus
    count: Optional[int] = Field(None, description="Number of items processed")
    duration_seconds: Optional[float] = Field(None, description="Duration of phase in seconds")
    message: Optional[str] = Field(None, description="Status message or error")


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
    started_at: datetime = Field(..., description="Workflow start time")
    completed_at: Optional[datetime] = Field(None, description="Workflow completion time")
    total_opportunities_found: Optional[int] = Field(None, description="Total opportunities discovered")
    total_opportunities_scored: Optional[int] = Field(None, description="Total opportunities scored")
    report_path: Optional[str] = Field(None, description="Path to generated markdown report")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF report")
    error: Optional[str] = Field(None, description="Error message if failed")


class WorkflowHistoryResponse(BaseModel):
    """Schema for workflow execution history."""
    workflows: List[WorkflowStatusResponse] = Field(..., description="List of workflow executions")
    total_count: int = Field(..., description="Total number of workflow executions")
