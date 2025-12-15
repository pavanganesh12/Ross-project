"""
Service layer for Configuration operations.
"""
import os
import sys
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..schemas.config import (
    ConfigResponse,
    ConfigUpdateRequest,
    SearchQueryPreset,
    MineralsListResponse,
)


class ConfigService:
    """Service class for configuration management."""
    
    def __init__(self):
        """Initialize the config service."""
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    def get_config(self) -> ConfigResponse:
        """Get current workflow configuration."""
        from config import WorkflowConfig, SEARCH_QUERIES, TRUSTED_DOMAINS
        
        return ConfigResponse(
            model_id=WorkflowConfig.MODEL_ID,
            exa_num_results=WorkflowConfig.EXA_NUM_RESULTS,
            exa_text_length_limit=WorkflowConfig.EXA_TEXT_LENGTH_LIMIT,
            exa_category=WorkflowConfig.EXA_CATEGORY,
            critical_minerals=WorkflowConfig.CRITICAL_MINERALS,
            default_query=WorkflowConfig.DEFAULT_QUERY,
            output_directory=WorkflowConfig.get_output_path(),
            report_sections=WorkflowConfig.REPORT_SECTIONS,
            geographic_regions=WorkflowConfig.GEOGRAPHIC_REGIONS,
            industry_sectors=WorkflowConfig.INDUSTRY_SECTORS,
            search_presets=SEARCH_QUERIES,
            trusted_domains=TRUSTED_DOMAINS,
        )
    
    def get_minerals(self) -> MineralsListResponse:
        """Get list of tracked minerals."""
        from config import WorkflowConfig
        
        return MineralsListResponse(
            minerals=WorkflowConfig.CRITICAL_MINERALS,
            count=len(WorkflowConfig.CRITICAL_MINERALS),
        )
    
    def get_search_presets(self) -> List[SearchQueryPreset]:
        """Get available search presets."""
        from config import SEARCH_QUERIES
        
        descriptions = {
            "general": "General critical minerals news and developments",
            "lithium": "Focused on lithium mining, prices, and battery tech",
            "geopolitics": "Supply chain security and international competition",
            "sustainability": "Environmental impact and green mining",
            "market": "Prices, supply/demand, and investment",
            "technology": "Mining tech and processing innovations",
            "supply_chain": "Logistics and distribution",
            "policy": "Government regulations and policies",
        }
        
        return [
            SearchQueryPreset(
                name=name,
                query=query,
                description=descriptions.get(name, ""),
            )
            for name, query in SEARCH_QUERIES.items()
        ]
    
    def get_trusted_domains(self) -> Dict[str, List[str]]:
        """Get trusted domains by category."""
        from config import TRUSTED_DOMAINS
        return TRUSTED_DOMAINS
    
    def get_geographic_regions(self) -> List[str]:
        """Get geographic focus regions."""
        from config import WorkflowConfig
        return WorkflowConfig.GEOGRAPHIC_REGIONS
    
    def get_industry_sectors(self) -> List[str]:
        """Get industry sectors."""
        from config import WorkflowConfig
        return WorkflowConfig.INDUSTRY_SECTORS
    
    def generate_custom_query(self, minerals: List[str]) -> str:
        """Generate a custom search query for specific minerals."""
        from config import WorkflowConfig
        return WorkflowConfig.get_search_query(minerals)
    
    def get_exa_config(self) -> Dict[str, Any]:
        """Get Exa search configuration."""
        from config import WorkflowConfig
        return WorkflowConfig.get_exa_config()
