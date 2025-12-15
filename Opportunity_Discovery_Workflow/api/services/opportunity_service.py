"""
Service layer for Opportunity operations.
"""
import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..schemas.opportunity import (
    OpportunityResponse,
    ScoredOpportunityResponse,
    OpportunityListResponse,
    ScoredOpportunityListResponse,
    OpportunityFilterParams,
)


class OpportunityService:
    """Service class for opportunity database operations."""
    
    def __init__(self):
        """Initialize the service with database path."""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_path, "opportunity_discovery.db")
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database and table exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                source TEXT,
                agency TEXT,
                sector TEXT,
                published_date TEXT,
                open_date TEXT,
                close_date TEXT,
                url TEXT UNIQUE,
                feasibility_score REAL,
                impact_score REAL,
                alignment_score REAL,
                total_score REAL,
                justification TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _row_to_dict(self, row: tuple, columns: List[str]) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        return dict(zip(columns, row))
    
    def get_all_opportunities(
        self,
        limit: int = 100,
        offset: int = 0,
        sector: Optional[str] = None,
        source: Optional[str] = None,
        min_score: Optional[float] = None,
    ) -> ScoredOpportunityListResponse:
        """
        Get all opportunities with optional filters.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            sector: Filter by sector
            source: Filter by source
            min_score: Minimum total score filter
            
        Returns:
            List of scored opportunities
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT * FROM opportunities WHERE 1=1"
        params = []
        
        if sector:
            query += " AND sector LIKE ?"
            params.append(f"%{sector}%")
        
        if source:
            query += " AND source LIKE ?"
            params.append(f"%{source}%")
        
        if min_score is not None:
            query += " AND total_score >= ?"
            params.append(min_score)
        
        # Order by score descending, then by published date
        query += " ORDER BY total_score DESC, published_date DESC"
        query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM opportunities WHERE 1=1"
        count_params = []
        if sector:
            count_query += " AND sector LIKE ?"
            count_params.append(f"%{sector}%")
        if source:
            count_query += " AND source LIKE ?"
            count_params.append(f"%{source}%")
        if min_score is not None:
            count_query += " AND total_score >= ?"
            count_params.append(min_score)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Convert rows to response objects
        opportunities = []
        total_scores = []
        
        for row in rows:
            opp = ScoredOpportunityResponse(
                id=row["id"],
                title=row["title"] or "",
                description=row["description"] or "",
                source=row["source"] or "",
                agency=row["agency"],
                sector=row["sector"],
                published_date=row["published_date"],
                open_date=row["open_date"],
                close_date=row["close_date"],
                url=row["url"],
                feasibility_score=row["feasibility_score"] or 0.0,
                impact_score=row["impact_score"] or 0.0,
                alignment_score=row["alignment_score"] or 0.0,
                total_score=row["total_score"] or 0.0,
                justification=row["justification"],
            )
            opportunities.append(opp)
            if row["total_score"]:
                total_scores.append(row["total_score"])
        
        avg_score = sum(total_scores) / len(total_scores) if total_scores else None
        
        return ScoredOpportunityListResponse(
            count=total_count,
            opportunities=opportunities,
            average_score=avg_score,
            generated_at=datetime.now(),
        )
    
    def get_opportunity_by_id(self, opportunity_id: int) -> Optional[ScoredOpportunityResponse]:
        """Get a single opportunity by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opportunity_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ScoredOpportunityResponse(
            id=row["id"],
            title=row["title"] or "",
            description=row["description"] or "",
            source=row["source"] or "",
            agency=row["agency"],
            sector=row["sector"],
            published_date=row["published_date"],
            open_date=row["open_date"],
            close_date=row["close_date"],
            url=row["url"],
            feasibility_score=row["feasibility_score"] or 0.0,
            impact_score=row["impact_score"] or 0.0,
            alignment_score=row["alignment_score"] or 0.0,
            total_score=row["total_score"] or 0.0,
            justification=row["justification"],
        )
    
    def get_opportunities_by_sector(self, sector: str) -> ScoredOpportunityListResponse:
        """Get opportunities filtered by sector."""
        return self.get_all_opportunities(sector=sector, limit=500)
    
    def get_top_opportunities(self, limit: int = 10, min_score: float = 7.0) -> ScoredOpportunityListResponse:
        """Get top-scoring opportunities."""
        return self.get_all_opportunities(limit=limit, min_score=min_score)
    
    def delete_opportunity(self, opportunity_id: int) -> bool:
        """Delete an opportunity by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM opportunities WHERE id = ?", (opportunity_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_sectors_summary(self) -> Dict[str, int]:
        """Get a summary of opportunities by sector."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sector, COUNT(*) as count 
            FROM opportunities 
            WHERE sector IS NOT NULL 
            GROUP BY sector 
            ORDER BY count DESC
        """)
        
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return results
    
    def get_sources_summary(self) -> Dict[str, int]:
        """Get a summary of opportunities by source."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM opportunities 
            WHERE source IS NOT NULL 
            GROUP BY source 
            ORDER BY count DESC
        """)
        
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about opportunities."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        total_count = cursor.fetchone()[0]
        
        # Score statistics
        cursor.execute("""
            SELECT 
                AVG(total_score) as avg_score,
                MAX(total_score) as max_score,
                MIN(total_score) as min_score
            FROM opportunities 
            WHERE total_score IS NOT NULL
        """)
        score_stats = cursor.fetchone()
        
        # Sector distribution
        cursor.execute("""
            SELECT sector, COUNT(*) as count 
            FROM opportunities 
            WHERE sector IS NOT NULL 
            GROUP BY sector
        """)
        sector_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Source distribution
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM opportunities 
            GROUP BY source
        """)
        source_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_opportunities": total_count,
            "score_statistics": {
                "average": round(score_stats[0], 2) if score_stats[0] else None,
                "max": round(score_stats[1], 2) if score_stats[1] else None,
                "min": round(score_stats[2], 2) if score_stats[2] else None,
            },
            "by_sector": sector_dist,
            "by_source": source_dist,
        }
