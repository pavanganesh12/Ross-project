"""
Service layer for Keyword operations.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..schemas.keywords import (
    KeywordDomain,
    KeywordsResponse,
    KeywordsUpdateRequest,
    KeywordAddRequest,
)


class KeywordService:
    """Service class for keyword management operations."""
    
    def __init__(self):
        """Initialize the keyword service."""
        self.keywords_path = r"d:\Agno\keywords.json"
    
    def _load_keywords(self) -> Dict[str, Any]:
        """Load keywords from JSON file."""
        if not os.path.exists(self.keywords_path):
            return {
                "keywords": {},
                "last_updated": None,
                "total_domains": 0,
                "total_keywords": 0
            }
        
        with open(self.keywords_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_keywords(self, data: Dict[str, Any]) -> None:
        """Save keywords to JSON file."""
        # Update metadata
        data["last_updated"] = datetime.now().isoformat()
        data["total_domains"] = len([k for k in data.get("keywords", {}).keys() 
                                     if k != "Negative_Keywords_To_Exclude"])
        data["total_keywords"] = sum(
            len(v) for k, v in data.get("keywords", {}).items()
        )
        
        with open(self.keywords_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def get_all_keywords(self) -> KeywordsResponse:
        """Get all keywords organized by domain."""
        data = self._load_keywords()
        keywords_dict = data.get("keywords", {})
        
        domains = []
        negative_keywords = None
        
        for name, kw_list in keywords_dict.items():
            if name == "Negative_Keywords_To_Exclude":
                negative_keywords = kw_list
            else:
                domains.append(KeywordDomain(
                    name=name,
                    keywords=kw_list,
                    count=len(kw_list)
                ))
        
        # Parse last_updated
        last_updated = None
        if data.get("last_updated"):
            try:
                last_updated = datetime.fromisoformat(data["last_updated"])
            except:
                pass
        
        return KeywordsResponse(
            domains=domains,
            total_domains=len(domains),
            total_keywords=sum(d.count for d in domains),
            last_updated=last_updated,
            negative_keywords=negative_keywords
        )
    
    def get_domain_keywords(self, domain: str) -> Optional[KeywordDomain]:
        """Get keywords for a specific domain."""
        data = self._load_keywords()
        keywords_dict = data.get("keywords", {})
        
        if domain not in keywords_dict:
            return None
        
        return KeywordDomain(
            name=domain,
            keywords=keywords_dict[domain],
            count=len(keywords_dict[domain])
        )
    
    def update_domain_keywords(self, request: KeywordsUpdateRequest) -> KeywordDomain:
        """Update keywords for a domain."""
        data = self._load_keywords()
        
        if "keywords" not in data:
            data["keywords"] = {}
        
        if request.append and request.domain in data["keywords"]:
            # Append new keywords (avoiding duplicates)
            existing = set(data["keywords"][request.domain])
            new_keywords = [kw for kw in request.keywords if kw not in existing]
            data["keywords"][request.domain].extend(new_keywords)
        else:
            # Replace keywords
            data["keywords"][request.domain] = request.keywords
        
        self._save_keywords(data)
        
        return KeywordDomain(
            name=request.domain,
            keywords=data["keywords"][request.domain],
            count=len(data["keywords"][request.domain])
        )
    
    def add_domain(self, request: KeywordAddRequest) -> KeywordDomain:
        """Add a new domain with keywords."""
        data = self._load_keywords()
        
        if "keywords" not in data:
            data["keywords"] = {}
        
        if request.domain in data["keywords"]:
            raise ValueError(f"Domain '{request.domain}' already exists. Use update instead.")
        
        data["keywords"][request.domain] = request.keywords
        self._save_keywords(data)
        
        return KeywordDomain(
            name=request.domain,
            keywords=request.keywords,
            count=len(request.keywords)
        )
    
    def delete_domain(self, domain: str) -> bool:
        """Delete an entire domain."""
        data = self._load_keywords()
        
        if domain not in data.get("keywords", {}):
            return False
        
        del data["keywords"][domain]
        self._save_keywords(data)
        
        return True
    
    def delete_keywords_from_domain(self, domain: str, keywords: List[str]) -> Optional[KeywordDomain]:
        """Delete specific keywords from a domain."""
        data = self._load_keywords()
        
        if domain not in data.get("keywords", {}):
            return None
        
        data["keywords"][domain] = [
            kw for kw in data["keywords"][domain] 
            if kw not in keywords
        ]
        
        self._save_keywords(data)
        
        return KeywordDomain(
            name=domain,
            keywords=data["keywords"][domain],
            count=len(data["keywords"][domain])
        )
    
    def search_keywords(self, query: str, domain: Optional[str] = None) -> Dict[str, List[str]]:
        """Search for keywords matching a query."""
        data = self._load_keywords()
        keywords_dict = data.get("keywords", {})
        
        results = {}
        query_lower = query.lower()
        
        for dom, kw_list in keywords_dict.items():
            if domain and dom != domain:
                continue
            
            matches = [kw for kw in kw_list if query_lower in kw.lower()]
            if matches:
                results[dom] = matches
        
        return results
    
    def get_negative_keywords(self) -> List[str]:
        """Get the list of negative keywords to exclude."""
        data = self._load_keywords()
        return data.get("keywords", {}).get("Negative_Keywords_To_Exclude", [])
    
    def update_negative_keywords(self, keywords: List[str], append: bool = False) -> List[str]:
        """Update negative keywords list."""
        data = self._load_keywords()
        
        if "keywords" not in data:
            data["keywords"] = {}
        
        if append and "Negative_Keywords_To_Exclude" in data["keywords"]:
            existing = set(data["keywords"]["Negative_Keywords_To_Exclude"])
            new_keywords = [kw for kw in keywords if kw not in existing]
            data["keywords"]["Negative_Keywords_To_Exclude"].extend(new_keywords)
        else:
            data["keywords"]["Negative_Keywords_To_Exclude"] = keywords
        
        self._save_keywords(data)
        
        return data["keywords"]["Negative_Keywords_To_Exclude"]
