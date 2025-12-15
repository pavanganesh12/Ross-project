"""
Workflow API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from typing import List, Dict, Any, Optional

from ..schemas.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    DataSource,
)
from ..services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflows"])

# Initialize service
workflow_service = WorkflowService()


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start Workflow",
    description="Start a new opportunity discovery workflow."
)
async def start_workflow(request: WorkflowRequest):
    """
    Start a new workflow execution.
    
    The workflow runs asynchronously in the background. Use the returned
    workflow_id to check status via GET /workflows/{workflow_id}.
    
    - **sources**: Data sources to fetch from (default: all)
    - **days_back**: Number of days to look back (1-30)
    - **domains**: Specific domains to filter by (optional)
    - **generate_report**: Whether to generate a markdown report
    - **save_to_db**: Whether to save results to database
    """
    return workflow_service.start_workflow(request)


@router.get(
    "",
    response_model=List[WorkflowStatusResponse],
    summary="List Workflows",
    description="Get a list of all workflow executions."
)
async def list_workflows(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of workflows to return")
):
    """
    Get all workflow executions.
    
    Returns workflows sorted by start time (most recent first).
    """
    return workflow_service.get_all_workflows(limit=limit)


@router.get(
    "/sources",
    response_model=List[str],
    summary="Get Available Sources",
    description="Get list of available data sources."
)
async def get_available_sources():
    """
    Get the list of available data sources for workflows.
    """
    return [source.value for source in DataSource]


@router.get(
    "/reports",
    response_model=List[Dict[str, Any]],
    summary="List Reports",
    description="Get a list of generated reports."
)
async def list_reports(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of reports to return")
):
    """
    Get all generated reports.
    
    Returns reports sorted by creation date (most recent first).
    """
    return workflow_service.get_reports(limit=limit)


@router.get(
    "/reports/{filename}",
    response_class=PlainTextResponse,
    summary="Get Report Content",
    description="Get the content of a specific report."
)
async def get_report_content(filename: str):
    """
    Get the content of a generated report.
    
    - **filename**: The filename of the report (must end with .md)
    """
    if not filename.endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename. Must be a markdown file (.md)"
        )
    
    content = workflow_service.get_report_content(filename)
    
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{filename}' not found"
        )
    
    return content


@router.get(
    "/{workflow_id}",
    response_model=WorkflowStatusResponse,
    summary="Get Workflow Status",
    description="Get the status of a workflow by ID."
)
async def get_workflow_status(workflow_id: str):
    """
    Get detailed status of a workflow execution.
    
    - **workflow_id**: The unique workflow ID returned when starting the workflow
    """
    workflow_status = workflow_service.get_workflow_status(workflow_id)
    
    if not workflow_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID '{workflow_id}' not found"
        )
    
    return workflow_status


@router.post(
    "/{workflow_id}/cancel",
    response_model=Dict[str, str],
    summary="Cancel Workflow",
    description="Cancel a running workflow."
)
async def cancel_workflow(workflow_id: str):
    """
    Cancel a running workflow.
    
    - **workflow_id**: The unique workflow ID to cancel
    
    Note: Only workflows in 'running' status can be cancelled.
    """
    cancelled = workflow_service.cancel_workflow(workflow_id)
    
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow '{workflow_id}' could not be cancelled. It may not exist or is not running."
        )
    
    return {"message": f"Workflow '{workflow_id}' has been cancelled"}


@router.post(
    "/quick",
    response_model=WorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Quick Start Workflow",
    description="Start a workflow with default settings."
)
async def quick_start_workflow():
    """
    Start a workflow with default settings.
    
    Uses all data sources, 7 days lookback, all domains,
    generates report, and saves to database.
    """
    request = WorkflowRequest(
        sources=[DataSource.ALL],
        days_back=7,
        domains=None,
        generate_report=True,
        save_to_db=True,
    )
    
    return workflow_service.start_workflow(request)
