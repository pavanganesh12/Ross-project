import requests
from datetime import datetime, timedelta
import json
from typing import Optional
from agno.tools import Toolkit

class GrantsGovTools(Toolkit):
    
    def __init__(self):
        super().__init__(name="grants_gov_tools")
        self.register(self.search_grants)

    def search_grants(self, keywords: Optional[str] = None, days_back: int = 7, limit: int = 100):

        url = "https://api.grants.gov/v1/api/search2"
        
        payload = {
            "keyword": keywords if keywords else None,
            "cfda": None,
            "agencies": None,
            "sortBy": "openDate|desc",
            "rows": limit,
            "eligibilities": None,
            "fundingCategories": None,
            "fundingInstruments": None,
            "dateRange": str(days_back),
            "oppStatuses": "posted"
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Agno-Agent"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            opportunities = []
            hits = data.get("oppHits")
            if not hits and "data" in data:
                hits = data["data"].get("oppHits")
                
            if hits:
                for item in hits:
                    opp = {
                        "title": item.get("title"),
                        "opportunityNumber": item.get("number"),
                        "agency": item.get("agency"),
                        "description": item.get("description"),
                        "link": f"https://www.grants.gov/search-results-detail/{item.get('id')}",
                        "openDate": item.get("openDate"),
                        "closeDate": item.get("closeDate"),
                        "source": "Grants.gov"
                    }
                    opportunities.append(opp)
            
            return opportunities

        except requests.exceptions.RequestException as e:
            return f"Error searching Grants.gov: {e}"
