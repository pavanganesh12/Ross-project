import sqlite3
import os
from typing import List
from Opportunity_Discovery_Workflow.Models.data_models import Opportunity, ScoredOpportunity

class DBManager:
    def __init__(self, db_path="opportunity_discovery.db"):
        # Ensure the path is absolute or relative to the workflow directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_path, db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                source TEXT,
                sector TEXT,
                published_date TEXT,
                url TEXT UNIQUE,
                feasibility_score REAL,
                impact_score REAL,
                alignment_score REAL,
                total_score REAL,
                justification TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_opportunities(self, opportunities: List[Opportunity]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for opp in opportunities:
            cursor.execute('''
                INSERT OR IGNORE INTO opportunities (title, description, source, sector, published_date, url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (opp.title, opp.description, opp.source, opp.sector, opp.published_date, opp.url))
            
        conn.commit()
        conn.close()

    def save_scored_opportunities(self, scored_opportunities: List[ScoredOpportunity]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # For simplicity, we'll just insert them as new rows or update if we had IDs.
        # Since we don't track IDs from discovery to scoring perfectly in this simple flow,
        # we will clear the table or just append. Let's append for now, but in a real app we'd update.
        # Actually, let's just insert them.
        
        for opp in scored_opportunities:
             cursor.execute('''
                INSERT OR REPLACE INTO opportunities (id, title, description, source, sector, published_date, url, 
                                           feasibility_score, impact_score, alignment_score, total_score, justification)
                VALUES (
                    (SELECT id FROM opportunities WHERE url = ?),
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (opp.url, opp.title, opp.description, opp.source, opp.sector, opp.published_date, opp.url,
                  opp.feasibility_score, opp.impact_score, opp.alignment_score, opp.total_score, opp.justification))

        conn.commit()
        conn.close()

    def get_all_opportunities(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM opportunities')
        rows = cursor.fetchall()
        conn.close()
        return rows
