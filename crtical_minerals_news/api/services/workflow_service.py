"""
Service layer for Workflow operations.
"""
import os
import sys
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..schemas.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatus,
    WorkflowPhase,
    WorkflowStatusResponse,
    WorkflowPhaseResult,
    SearchCategory,
)


class WorkflowService:
    """Service class for workflow execution and management."""
    
    # In-memory storage for workflow status
    _workflows: Dict[str, WorkflowStatusResponse] = {}
    _lock = threading.Lock()
    _executor = ThreadPoolExecutor(max_workers=2)
    
    def __init__(self):
        """Initialize the workflow service."""
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = os.path.join(self.base_path, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _update_workflow_status(
        self,
        workflow_id: str,
        status: Optional[WorkflowStatus] = None,
        current_phase: Optional[WorkflowPhase] = None,
        phase_result: Optional[WorkflowPhaseResult] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """Update workflow status in thread-safe manner."""
        with self._lock:
            if workflow_id not in self._workflows:
                return
            
            workflow = self._workflows[workflow_id]
            
            if status:
                workflow.status = status
            if current_phase:
                workflow.current_phase = current_phase
            if phase_result:
                workflow.phases.append(phase_result)
            if error:
                workflow.error = error
            
            for key, value in kwargs.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
    
    def start_workflow(self, request: WorkflowRequest) -> WorkflowResponse:
        """
        Start a new workflow execution.
        
        Args:
            request: Workflow configuration request
            
        Returns:
            WorkflowResponse with workflow ID and initial status
        """
        workflow_id = str(uuid.uuid4())[:8]
        
        # Determine query to use
        query_used = self._determine_query(request)
        
        # Determine categories to search
        categories = self._determine_categories(request)
        
        # Initialize workflow status
        workflow_status = WorkflowStatusResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            current_phase=None,
            phases=[],
            query_used=query_used,
            categories_searched=categories,
            started_at=datetime.now(),
            completed_at=None,
            report_filename=None,
            error=None,
        )
        
        with self._lock:
            self._workflows[workflow_id] = workflow_status
        
        # Submit workflow execution to background thread
        self._executor.submit(self._execute_workflow, workflow_id, request, query_used, categories)
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            message="Workflow started. Use GET /workflows/{workflow_id} to check status.",
            started_at=workflow_status.started_at,
        )
    
    def _determine_query(self, request: WorkflowRequest) -> str:
        """Determine the search query to use."""
        from config import SEARCH_QUERIES, WorkflowConfig
        
        if request.query:
            return request.query
        
        if request.preset and request.preset in SEARCH_QUERIES:
            return SEARCH_QUERIES[request.preset]
        
        if request.minerals:
            return WorkflowConfig.get_search_query(request.minerals)
        
        return WorkflowConfig.DEFAULT_QUERY
    
    def _determine_categories(self, request: WorkflowRequest) -> List[str]:
        """Determine which categories to search."""
        if SearchCategory.ALL in request.categories:
            return ["news", "twitter", "linkedin"]
        return [cat.value for cat in request.categories]
    
    def _execute_workflow(
        self, 
        workflow_id: str, 
        request: WorkflowRequest, 
        query: str,
        categories: List[str]
    ):
        """Execute the workflow in a background thread."""
        import time
        
        try:
            self._update_workflow_status(workflow_id, status=WorkflowStatus.RUNNING)
            
            # Import workflow components
            from workflows import enhanced_workflow
            
            # Update phase: PREPARE
            self._update_workflow_status(
                workflow_id, 
                current_phase=WorkflowPhase.PREPARE,
                phase_result=WorkflowPhaseResult(
                    phase=WorkflowPhase.PREPARE,
                    status=WorkflowStatus.RUNNING,
                    message="Preparing search queries"
                )
            )
            
            phase_start = time.time()
            
            # Run the workflow
            try:
                response = enhanced_workflow.run(
                    input=query,
                    additional_data={
                        "original_query": query,
                        "categories": categories,
                        "days_back": request.days_back,
                    }
                )
                
                # Update completion
                self._update_workflow_status(
                    workflow_id,
                    phase_result=WorkflowPhaseResult(
                        phase=WorkflowPhase.SAVE,
                        status=WorkflowStatus.COMPLETED,
                        duration_seconds=round(time.time() - phase_start, 2),
                        message="Report saved successfully"
                    )
                )
                
                # Find the generated report files
                report_filename = self._find_latest_report('.md')
                pdf_filename = self._find_latest_report('.pdf')
                
                self._update_workflow_status(
                    workflow_id,
                    status=WorkflowStatus.COMPLETED,
                    current_phase=None,
                    completed_at=datetime.now(),
                    report_filename=report_filename,
                    pdf_filename=pdf_filename
                )
                
            except Exception as e:
                self._update_workflow_status(
                    workflow_id,
                    status=WorkflowStatus.FAILED,
                    error=str(e),
                    completed_at=datetime.now()
                )
                
        except Exception as e:
            self._update_workflow_status(
                workflow_id,
                status=WorkflowStatus.FAILED,
                error=str(e),
                completed_at=datetime.now()
            )
    
    def _find_latest_report(self, extension: str = '.md') -> Optional[str]:
        """Find the most recently created report with the given extension."""
        if not os.path.exists(self.output_dir):
            return None
        
        reports = [f for f in os.listdir(self.output_dir) if f.endswith(extension)]
        if not reports:
            return None
        
        # Sort by modification time, newest first
        reports.sort(
            key=lambda f: os.path.getmtime(os.path.join(self.output_dir, f)),
            reverse=True
        )
        
        return reports[0] if reports else None
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatusResponse]:
        """Get the status of a workflow by ID."""
        with self._lock:
            return self._workflows.get(workflow_id)
    
    def get_all_workflows(self, limit: int = 50) -> List[WorkflowStatusResponse]:
        """Get all workflow statuses."""
        with self._lock:
            workflows = list(self._workflows.values())
            workflows.sort(key=lambda x: x.started_at, reverse=True)
            return workflows[:limit]
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        with self._lock:
            if workflow_id not in self._workflows:
                return False
            
            workflow = self._workflows[workflow_id]
            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.CANCELLED
                workflow.completed_at = datetime.now()
                return True
            
            return False
    
    def get_available_presets(self) -> Dict[str, str]:
        """Get available search query presets."""
        from config import SEARCH_QUERIES
        return SEARCH_QUERIES
