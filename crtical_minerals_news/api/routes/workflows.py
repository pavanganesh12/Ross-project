"""
Workflow API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional

from ..schemas.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    SearchCategory,
)
from ..services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflows"])

# Initialize service
workflow_service = WorkflowService()


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start News Discovery Workflow",
    description="Start a new critical minerals news discovery workflow."
)
async def start_workflow(request: WorkflowRequest):
    """
    Start a new workflow execution.
    
    The workflow searches across news, Twitter, and LinkedIn for critical
    minerals information, aggregates the results, and generates a report.
    
    - **query**: Custom search query (optional)
    - **minerals**: Specific minerals to search for (optional)
    - **categories**: Search categories (news, twitter, linkedin, or all)
    - **preset**: Use a predefined search preset (general, lithium, geopolitics, etc.)
    - **days_back**: Number of days to look back (1-30)
    - **num_results**: Number of results per category
    - **generate_report**: Whether to save a markdown report
    """
    return workflow_service.start_workflow(request)


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
    
    Uses the default query, all categories, 7 days lookback.
    """
    request = WorkflowRequest(
        query=None,
        minerals=None,
        categories=[SearchCategory.ALL],
        preset=None,
        days_back=7,
        num_results=15,
        generate_report=True,
    )
    return workflow_service.start_workflow(request)


@router.post(
    "/preset/{preset_name}",
    response_model=WorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start Workflow with Preset",
    description="Start a workflow using a predefined search preset."
)
async def start_workflow_with_preset(preset_name: str):
    """
    Start a workflow with a predefined search preset.
    
    Available presets: general, lithium, geopolitics, sustainability,
    market, technology, supply_chain, policy
    """
    presets = workflow_service.get_available_presets()
    
    if preset_name not in presets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown preset '{preset_name}'. Available: {list(presets.keys())}"
        )
    
    request = WorkflowRequest(
        preset=preset_name,
        categories=[SearchCategory.ALL],
        days_back=7,
        num_results=15,
        generate_report=True,
    )
    return workflow_service.start_workflow(request)


@router.get(
    "",
    response_model=List[WorkflowStatusResponse],
    summary="List Workflows",
    description="Get a list of all workflow executions."
)
async def list_workflows(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum workflows to return")
):
    """Get all workflow executions, sorted by start time (newest first)."""
    return workflow_service.get_all_workflows(limit=limit)


@router.get(
    "/presets",
    response_model=Dict[str, str],
    summary="Get Available Presets",
    description="Get list of available search query presets."
)
async def get_presets():
    """Get the list of available search presets with their queries."""
    return workflow_service.get_available_presets()


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get Search Categories",
    description="Get list of available search categories."
)
async def get_categories():
    """Get the list of available search categories."""
    return [cat.value for cat in SearchCategory]


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
    
    Note: Only workflows in 'running' status can be cancelled.
    """
    cancelled = workflow_service.cancel_workflow(workflow_id)
    
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow '{workflow_id}' could not be cancelled"
        )
    
    return {"message": f"Workflow '{workflow_id}' has been cancelled"}
