"""
Service layer for Workflow operations.
"""
import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import threading

from ..schemas.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatus,
    WorkflowPhase,
    WorkflowStatusResponse,
    WorkflowPhaseResult,
    DataSource,
)


class WorkflowService:
    """Service class for workflow execution and management."""
    
    # In-memory storage for workflow status (in production, use Redis or database)
    _workflows: Dict[str, WorkflowStatusResponse] = {}
    _lock = threading.Lock()
    _executor = ThreadPoolExecutor(max_workers=3)
    
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
        
        # Initialize workflow status
        workflow_status = WorkflowStatusResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            current_phase=None,
            phases=[],
            started_at=datetime.now(),
            completed_at=None,
            total_opportunities_found=None,
            total_opportunities_scored=None,
            report_path=None,
            error=None,
        )
        
        with self._lock:
            self._workflows[workflow_id] = workflow_status
        
        # Submit workflow execution to background thread
        self._executor.submit(self._execute_workflow, workflow_id, request)
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            message="Workflow started successfully. Use GET /workflows/{workflow_id} to check status.",
            started_at=workflow_status.started_at,
        )
    
    def _execute_workflow(self, workflow_id: str, request: WorkflowRequest):
        """Execute the workflow in a background thread."""
        import time
        
        try:
            self._update_workflow_status(workflow_id, status=WorkflowStatus.RUNNING)
            
            # Import workflow components
            from Opportunity_Discovery_Workflow.Agents.simpler_grants_gov_agent import get_agent as get_fetch_agent_simpler
            from Opportunity_Discovery_Workflow.Agents.grants_gov_agent import get_agent as get_fetch_agent_grants_gov
            from Opportunity_Discovery_Workflow.Agents.sam_gov_agent import get_agent as get_fetch_agent_sam_gov
            from Opportunity_Discovery_Workflow.Agents.aggregation_agent import get_agent as get_aggregation_agent
            from Opportunity_Discovery_Workflow.Agents.filter_agent import get_agent as get_filter_agent
            from Opportunity_Discovery_Workflow.Agents.scoring_agent import get_agent as get_scoring_agent
            from Opportunity_Discovery_Workflow.Agents.report_agent import get_agent as get_report_agent
            from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList, ScoredOpportunityList
            
            all_opportunities = []
            
            # PHASE 1: FETCH
            self._update_workflow_status(workflow_id, current_phase=WorkflowPhase.FETCH)
            phase_start = time.time()
            
            sources_to_fetch = request.sources
            if DataSource.ALL in sources_to_fetch:
                sources_to_fetch = [DataSource.SIMPLER_GRANTS, DataSource.GRANTS_GOV, DataSource.SAM_GOV]
            
            # Fetch from each source
            for source in sources_to_fetch:
                try:
                    if source == DataSource.SIMPLER_GRANTS:
                        agent = get_fetch_agent_simpler()
                    elif source == DataSource.GRANTS_GOV:
                        agent = get_fetch_agent_grants_gov()
                    elif source == DataSource.SAM_GOV:
                        agent = get_fetch_agent_sam_gov()
                    else:
                        continue
                    
                    response = agent.run(
                        f"Fetch opportunities posted in the last {request.days_back} days.",
                        response_model=OpportunityList
                    )
                    
                    if response.content and not isinstance(response.content, str):
                        all_opportunities.extend(response.content.opportunities)
                        
                except Exception as e:
                    print(f"Error fetching from {source}: {e}")
            
            fetch_duration = time.time() - phase_start
            self._update_workflow_status(
                workflow_id,
                phase_result=WorkflowPhaseResult(
                    phase=WorkflowPhase.FETCH,
                    status=WorkflowStatus.COMPLETED,
                    count=len(all_opportunities),
                    duration_seconds=round(fetch_duration, 2),
                    message=f"Fetched {len(all_opportunities)} opportunities"
                ),
                total_opportunities_found=len(all_opportunities)
            )
            
            if not all_opportunities:
                self._update_workflow_status(
                    workflow_id,
                    status=WorkflowStatus.COMPLETED,
                    completed_at=datetime.now(),
                    error="No opportunities found from any source"
                )
                return
            
            # PHASE 2: AGGREGATE
            self._update_workflow_status(workflow_id, current_phase=WorkflowPhase.AGGREGATE)
            phase_start = time.time()
            
            try:
                aggregation_agent = get_aggregation_agent()
                opps_json = json.dumps([opp.model_dump() for opp in all_opportunities], indent=2)
                
                response = aggregation_agent.run(
                    f"Here is the list of opportunities:\n{opps_json}\n\nMerge duplicates and enrich.",
                    response_model=OpportunityList
                )
                
                if response.content and not isinstance(response.content, str):
                    aggregated_opportunities = response.content.opportunities
                else:
                    # Fallback: basic deduplication
                    unique = {opp.url or opp.title: opp for opp in all_opportunities}
                    aggregated_opportunities = list(unique.values())
                    
            except Exception as e:
                print(f"Aggregation error: {e}")
                aggregated_opportunities = all_opportunities
            
            agg_duration = time.time() - phase_start
            self._update_workflow_status(
                workflow_id,
                phase_result=WorkflowPhaseResult(
                    phase=WorkflowPhase.AGGREGATE,
                    status=WorkflowStatus.COMPLETED,
                    count=len(aggregated_opportunities),
                    duration_seconds=round(agg_duration, 2),
                    message=f"Aggregated to {len(aggregated_opportunities)} unique opportunities"
                )
            )
            
            # PHASE 3: FILTER
            self._update_workflow_status(workflow_id, current_phase=WorkflowPhase.FILTER)
            phase_start = time.time()
            
            try:
                filter_agent = get_filter_agent()
                filtered_opportunities = []
                batch_size = 10
                
                for i in range(0, len(aggregated_opportunities), batch_size):
                    batch = aggregated_opportunities[i:i + batch_size]
                    opps_json = json.dumps([opp.model_dump() for opp in batch], indent=2)
                    
                    response = filter_agent.run(
                        f"Filter these opportunities:\n{opps_json}",
                        response_model=OpportunityList
                    )
                    
                    if response.content and not isinstance(response.content, str):
                        filtered_opportunities.extend(response.content.opportunities)
                        
            except Exception as e:
                print(f"Filter error: {e}")
                filtered_opportunities = aggregated_opportunities
            
            filter_duration = time.time() - phase_start
            self._update_workflow_status(
                workflow_id,
                phase_result=WorkflowPhaseResult(
                    phase=WorkflowPhase.FILTER,
                    status=WorkflowStatus.COMPLETED,
                    count=len(filtered_opportunities),
                    duration_seconds=round(filter_duration, 2),
                    message=f"Filtered to {len(filtered_opportunities)} relevant opportunities"
                )
            )
            
            if not filtered_opportunities:
                self._update_workflow_status(
                    workflow_id,
                    status=WorkflowStatus.COMPLETED,
                    completed_at=datetime.now(),
                    error="No opportunities matched domain keywords"
                )
                return
            
            # PHASE 4: SCORE
            self._update_workflow_status(workflow_id, current_phase=WorkflowPhase.SCORE)
            phase_start = time.time()
            
            try:
                scoring_agent = get_scoring_agent()
                opps_json = json.dumps([opp.model_dump() for opp in filtered_opportunities], indent=2)
                
                response = scoring_agent.run(
                    f"Score these opportunities:\n{opps_json}",
                    response_model=ScoredOpportunityList
                )
                
                if response.content and not isinstance(response.content, str):
                    scored_opportunities = response.content.opportunities
                else:
                    scored_opportunities = []
                    
            except Exception as e:
                print(f"Scoring error: {e}")
                scored_opportunities = []
            
            score_duration = time.time() - phase_start
            self._update_workflow_status(
                workflow_id,
                phase_result=WorkflowPhaseResult(
                    phase=WorkflowPhase.SCORE,
                    status=WorkflowStatus.COMPLETED,
                    count=len(scored_opportunities),
                    duration_seconds=round(score_duration, 2),
                    message=f"Scored {len(scored_opportunities)} opportunities"
                ),
                total_opportunities_scored=len(scored_opportunities)
            )
            
            # Save scored opportunities
            if request.save_to_db and scored_opportunities:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                scored_filename = f"simple_grants_scored_{timestamp}.json"
                scored_filepath = os.path.join(self.output_dir, scored_filename)
                
                with open(scored_filepath, "w", encoding="utf-8") as f:
                    json.dump([opp.model_dump() for opp in scored_opportunities], f, indent=2)
            
            # PHASE 5: REPORT
            report_path = None
            pdf_path = None
            if request.generate_report and scored_opportunities:
                self._update_workflow_status(workflow_id, current_phase=WorkflowPhase.REPORT)
                phase_start = time.time()
                
                try:
                    report_agent = get_report_agent()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Save data for report
                    data_filename = f"api_workflow_data_{timestamp}.json"
                    data_filepath = os.path.join(self.output_dir, data_filename)
                    
                    with open(data_filepath, "w", encoding="utf-8") as f:
                        json.dump([opp.model_dump() for opp in scored_opportunities], f, indent=2)
                    
                    report_filename = f"API_Workflow_Report_{timestamp}.md"
                    
                    report_agent.run(
                        f"Read '{data_filename}' and generate a report. Save as '{report_filename}'."
                    )
                    
                    report_path = report_filename
                    
                    # Cleanup data file
                    if os.path.exists(data_filepath):
                        os.remove(data_filepath)
                        
                except Exception as e:
                    print(f"Report error: {e}")
                
                report_duration = time.time() - phase_start
                self._update_workflow_status(
                    workflow_id,
                    phase_result=WorkflowPhaseResult(
                        phase=WorkflowPhase.REPORT,
                        status=WorkflowStatus.COMPLETED,
                        count=1 if report_path else 0,
                        duration_seconds=round(report_duration, 2),
                        message=f"Generated report: {report_path}" if report_path else "Report generation failed"
                    ),
                    report_path=report_path
                )
                
                # PHASE 6: PDF CONVERSION
                if report_path:
                    self._update_workflow_status(workflow_id, current_phase=WorkflowPhase.PDF_CONVERT)
                    phase_start = time.time()
                    
                    try:
                        from Opportunity_Discovery_Workflow.utils.pdf_converter import convert_md_to_pdf
                        
                        md_filepath = os.path.join(self.output_dir, report_path)
                        pdf_result = convert_md_to_pdf(md_filepath)
                        
                        if pdf_result:
                            pdf_path = os.path.basename(pdf_result)
                            
                    except Exception as e:
                        print(f"PDF conversion error: {e}")
                    
                    pdf_duration = time.time() - phase_start
                    self._update_workflow_status(
                        workflow_id,
                        phase_result=WorkflowPhaseResult(
                            phase=WorkflowPhase.PDF_CONVERT,
                            status=WorkflowStatus.COMPLETED if pdf_path else WorkflowStatus.FAILED,
                            count=1 if pdf_path else 0,
                            duration_seconds=round(pdf_duration, 2),
                            message=f"Generated PDF: {pdf_path}" if pdf_path else "PDF conversion failed"
                        ),
                        pdf_path=pdf_path
                    )
            
            # Mark workflow as completed
            self._update_workflow_status(
                workflow_id,
                status=WorkflowStatus.COMPLETED,
                current_phase=None,
                completed_at=datetime.now()
            )
            
        except Exception as e:
            self._update_workflow_status(
                workflow_id,
                status=WorkflowStatus.FAILED,
                error=str(e),
                completed_at=datetime.now()
            )
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatusResponse]:
        """Get the status of a workflow by ID."""
        with self._lock:
            return self._workflows.get(workflow_id)
    
    def get_all_workflows(self, limit: int = 50) -> List[WorkflowStatusResponse]:
        """Get all workflow statuses."""
        with self._lock:
            workflows = list(self._workflows.values())
            # Sort by started_at descending
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
    
    def get_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of generated reports (both MD and PDF)."""
        reports = []
        
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith(".md") or filename.endswith(".pdf"):
                    filepath = os.path.join(self.output_dir, filename)
                    stat = os.stat(filepath)
                    reports.append({
                        "filename": filename,
                        "path": filepath,
                        "type": "pdf" if filename.endswith(".pdf") else "markdown",
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
        
        # Sort by creation date descending
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        return reports[:limit]
    
    def get_report_content(self, filename: str) -> Optional[str]:
        """Get the content of a specific report."""
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        # Security check: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
