import os
import requests
from typing import Optional
from agno.tools import Toolkit
from datetime import datetime, timedelta

class SimplerGrantsGovTools(Toolkit):

    def __init__(self, api_key: str = None):
        super().__init__(name="simpler_grants_gov_tools")

        self.api_key = api_key or os.getenv("SIMPLER_GRANTS_GOV_API_KEY")

        if not self.api_key:
            print("Warning: SIMPLER_GRANTS_GOV_API_KEY not found. Simpler.Grants.gov tool will not function correctly.")

        self.register(self.search_opportunities)

    def search_opportunities(self, keywords: Optional[str] = None, days_back: int = 7, limit: int = 50):

        if not self.api_key:
            return "Error: SIMPLER_GRANTS_GOV_API_KEY is missing."

        base_url = "https://api.simpler.grants.gov/v1/opportunities/search"
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        opportunities = []
        page_offset = 1
        page_size = 50
        more_pages = True
        
        while more_pages and len(opportunities) < limit:
            search_payload = {
                                "filters": {
                                    "opportunity_status": {
                                        "one_of": [
                                            "posted",
                                            "forecasted"
                                        ]
                                    }
                                },
                                "pagination": {
                                    "page_offset": page_offset,
                                    "page_size": page_size,
                                    "sort_order": [
                                        {
                                            "order_by": "post_date",
                                            "sort_direction": "descending"
                                        }
                                    ]
                                }
                            }
            
            if keywords:
                search_payload["query"] = keywords

            try:
                response = requests.post(base_url, json=search_payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if "data" not in data or not data["data"]:
                    break
                
                current_batch = data["data"]
                
                for item in current_batch:
                    # Extract summary dictionary
                    summary = item.get("summary", {})
                    
                    post_date_str = summary.get("post_date")
                    
                    if post_date_str:
                        try:
                            # Try parsing YYYY-MM-DD
                            post_date = datetime.strptime(post_date_str, "%Y-%m-%d")
                            if post_date < cutoff_date:
                                more_pages = False
                                break
                        except ValueError:
                            pass
                    
                    opp = {
                        "title": item.get("opportunity_title") or item.get("title"),
                        "opportunityNumber": item.get("opportunity_number") or item.get("opportunityNumber"),
                        "description": (summary.get("summary_description") or "")[:200],
                        "agency": item.get("agency_name") or item.get("agency", {}).get("name"),
                        "postedDate": post_date_str,
                        "closeDate": summary.get("close_date"),
                        "link": f"https://simpler.grants.gov/opportunity/{item.get('opportunity_id') or item.get('id')}",
                        "source": "Simpler.Grants.gov"
                    }

                    opportunities.append(opp)
                    
                    if len(opportunities) >= limit:
                        more_pages = False
                        break
                
                page_offset += 1
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Error searching Simpler.Grants.gov: {e}"
                if hasattr(e, 'response') and e.response is not None:
                    error_msg += f"\nResponse: {e.response.text}"
                return error_msg
                
        return opportunities
