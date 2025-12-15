"""
Service layer for Report operations.
"""
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..schemas.report import (
    ReportSummary,
    ReportListResponse,
    ReportResponse,
    ReportSearchResult,
)


class ReportService:
    """Service class for report management operations."""
    
    def __init__(self):
        """Initialize the report service."""
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = os.path.join(self.base_path, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def get_all_reports(self, limit: int = 50) -> ReportListResponse:
        """Get all reports with metadata."""
        reports = []
        
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(self.output_dir, filename)
                    stat = os.stat(filepath)
                    
                    reports.append(ReportSummary(
                        filename=filename,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        size_bytes=stat.st_size,
                        size_readable=self._format_size(stat.st_size),
                    ))
        
        # Sort by creation date, newest first
        reports.sort(key=lambda x: x.created_at, reverse=True)
        
        return ReportListResponse(
            reports=reports[:limit],
            total_count=len(reports),
            output_directory=self.output_dir,
        )
    
    def get_report_content(self, filename: str) -> Optional[ReportResponse]:
        """Get the content of a specific report."""
        # Security check
        if ".." in filename or "/" in filename or "\\" in filename:
            return None
        
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        stat = os.stat(filepath)
        word_count = len(content.split())
        
        return ReportResponse(
            filename=filename,
            content=content,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            size_bytes=stat.st_size,
            word_count=word_count,
        )
    
    def get_latest_report(self) -> Optional[ReportResponse]:
        """Get the most recent report."""
        reports = self.get_all_reports(limit=1)
        
        if not reports.reports:
            return None
        
        return self.get_report_content(reports.reports[0].filename)
    
    def delete_report(self, filename: str) -> bool:
        """Delete a report by filename."""
        # Security check
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            return False
        
        os.remove(filepath)
        return True
    
    def search_reports(self, keyword: str, limit: int = 10) -> List[ReportSearchResult]:
        """Search reports for a keyword."""
        results = []
        keyword_lower = keyword.lower()
        
        if not os.path.exists(self.output_dir):
            return results
        
        reports = [f for f in os.listdir(self.output_dir) if f.endswith(".md")]
        reports.sort(
            key=lambda f: os.path.getmtime(os.path.join(self.output_dir, f)),
            reverse=True
        )
        
        for filename in reports[:limit]:
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find matching lines
            matches = []
            lines = content.split("\n")
            
            for i, line in enumerate(lines):
                if keyword_lower in line.lower():
                    # Get context: line before, matching line, line after
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    context = " ".join(lines[start:end]).strip()
                    
                    # Truncate if too long
                    if len(context) > 300:
                        context = context[:300] + "..."
                    
                    matches.append(context)
            
            if matches:
                results.append(ReportSearchResult(
                    filename=filename,
                    matches=matches[:5],  # Limit matches per report
                    match_count=len(matches),
                ))
        
        return results
    
    def get_report_statistics(self) -> Dict[str, Any]:
        """Get statistics about all reports."""
        reports = self.get_all_reports(limit=1000)
        
        if not reports.reports:
            return {
                "total_reports": 0,
                "total_size_bytes": 0,
                "total_size_readable": "0 B",
                "oldest_report": None,
                "newest_report": None,
                "average_size_bytes": 0,
            }
        
        total_size = sum(r.size_bytes for r in reports.reports)
        oldest = min(reports.reports, key=lambda x: x.created_at)
        newest = max(reports.reports, key=lambda x: x.created_at)
        
        return {
            "total_reports": reports.total_count,
            "total_size_bytes": total_size,
            "total_size_readable": self._format_size(total_size),
            "oldest_report": oldest.filename,
            "oldest_date": oldest.created_at.isoformat(),
            "newest_report": newest.filename,
            "newest_date": newest.created_at.isoformat(),
            "average_size_bytes": total_size // reports.total_count if reports.total_count else 0,
            "average_size_readable": self._format_size(total_size // reports.total_count) if reports.total_count else "0 B",
        }
