import requests
from datetime import datetime, timedelta
import os
from typing import Optional
from agno.tools import Toolkit

class SamGovTools(Toolkit):
    
    def __init__(self, api_key: str = None):
        super().__init__(name="sam_gov_tools")
        self.api_key = api_key or os.getenv("SAM_GOV_API_KEY")
        
        if not self.api_key:
            print("Warning: SAM_GOV_API_KEY not found. SAM.gov tool will not function correctly.")

        self.register(self.search_opportunities)

    def search_opportunities(self, keywords: Optional[str] = None, days_back: int = 7, limit: int = 300):

        if not self.api_key:
            return "Error: SAM_GOV_API_KEY is missing."

        base_url = "https://api.sam.gov/opportunities/v2/search"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates as MM/DD/YYYY for SAM.gov API
        posted_from = start_date.strftime("%m/%d/%Y")
        posted_to = end_date.strftime("%m/%d/%Y")

        params = {
            "api_key": self.api_key,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": limit,
            "offset": 0,
            "active": "true"
        }
        
        headers = {
            "User-Agent": "Agno-Agent/1.0"
        }
        
        if keywords:
            params["keywords"] = keywords

        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            opportunities = []
            if "opportunitiesData" in data:
                for item in data["opportunitiesData"]:
                    opp = {
                        "title": item.get("title"),
                        "solicitationNumber": item.get("solicitationNumber"),
                        "description": item.get("description"),
                        "link": item.get("uiLink"),
                        "postedDate": item.get("postedDate"),
                        "responseDeadLine": item.get("responseDeadLine"),
                        "source": "SAM.gov"
                    }
                    opportunities.append(opp)
            
            return opportunities

        except requests.exceptions.RequestException as e:
            error_msg = f"Error searching SAM.gov: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse: {e.response.text}"
            return error_msg
