"""
Report API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from typing import List, Dict, Any, Optional

from ..schemas.report import (
    ReportSummary,
    ReportListResponse,
    ReportResponse,
    ReportDeleteResponse,
    ReportSearchResult,
)
from ..services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])

# Initialize service
report_service = ReportService()


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List Reports",
    description="Get a list of all generated reports."
)
async def list_reports(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum reports to return")
):
    """
    Get all generated reports.
    
    Returns reports sorted by creation date (newest first).
    """
    return report_service.get_all_reports(limit=limit)


@router.get(
    "/latest",
    response_model=ReportResponse,
    summary="Get Latest Report",
    description="Get the most recently generated report."
)
async def get_latest_report():
    """Get the most recent report with full content."""
    report = report_service.get_latest_report()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reports found"
        )
    
    return report


@router.get(
    "/statistics",
    response_model=Dict[str, Any],
    summary="Get Report Statistics",
    description="Get statistics about all reports."
)
async def get_report_statistics():
    """Get statistics about generated reports."""
    return report_service.get_report_statistics()


@router.get(
    "/search",
    response_model=List[ReportSearchResult],
    summary="Search Reports",
    description="Search reports for a keyword."
)
async def search_reports(
    keyword: str = Query(..., min_length=2, description="Keyword to search for"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum reports to search")
):
    """
    Search reports for a keyword.
    
    Returns matching text excerpts from each report.
    """
    results = report_service.search_reports(keyword, limit)
    
    if not results:
        return []
    
    return results


@router.get(
    "/{filename}",
    response_model=ReportResponse,
    summary="Get Report",
    description="Get a specific report by filename."
)
async def get_report(filename: str):
    """
    Get a specific report with full content.
    
    - **filename**: The report filename (with or without .md extension)
    """
    report = report_service.get_report_content(filename)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{filename}' not found"
        )
    
    return report


@router.get(
    "/{filename}/raw",
    response_class=PlainTextResponse,
    summary="Get Raw Report Content",
    description="Get report content as plain markdown text."
)
async def get_report_raw(filename: str):
    """
    Get report content as plain markdown text.
    
    Useful for direct rendering or downloading.
    """
    report = report_service.get_report_content(filename)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{filename}' not found"
        )
    
    return report.content


@router.delete(
    "/{filename}",
    response_model=ReportDeleteResponse,
    summary="Delete Report",
    description="Delete a report by filename."
)
async def delete_report(filename: str):
    """
    Delete a report.
    
    - **filename**: The report filename to delete
    
    Warning: This action cannot be undone.
    """
    deleted = report_service.delete_report(filename)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{filename}' not found"
        )
    
    return ReportDeleteResponse(
        filename=filename,
        message=f"Report '{filename}' deleted successfully"
    )
