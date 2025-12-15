"""
Configuration file for Critical Minerals News Workflow

Modify these settings to customize the workflow behavior.
"""

from typing import List


class WorkflowConfig:
    """Configuration for the critical minerals news workflow."""
    
    # OpenAI Model Configuration
    MODEL_ID: str = "gpt-4o-mini"  # Options: "gpt-4o-mini", "gpt-4o", "gpt-4-turbo"
    
    # Exa Search Configuration
    EXA_NUM_RESULTS: int = 15  # Number of results per search
    EXA_TEXT_LENGTH_LIMIT: int = 1000  # Character limit for each result
    EXA_CATEGORY: str = "news"  # Options: "news", "twitter", "linkedin"
    EXA_SHOW_RESULTS: bool = True  # Show results in console
    
    # Search Topics - Customize what to search for
    CRITICAL_MINERALS: List[str] = [
        "lithium",
        "cobalt", 
        "nickel",
        "rare earth elements",
        "copper",
        "graphite",
        "manganese",
    ]
    
    # Default search query
    DEFAULT_QUERY: str = (
        "Latest developments in critical minerals including "
        "lithium, cobalt, nickel, rare earth elements, and mining industry"
    )
    
    # Report Configuration
    OUTPUT_DIRECTORY: str = "outputs"
    REPORT_PREFIX: str = "critical_minerals_news"
    INCLUDE_TIMESTAMP: bool = True
    
    # Agent Instructions Customization
    WEB_SEARCH_FOCUS_AREAS: List[str] = [
        "Mining developments and new discoveries",
        "Supply chain issues and geopolitics",
        "Market trends and pricing",
        "Sustainability and environmental concerns",
        "Technology and innovation in mining",
        "Policy and regulatory changes",
    ]
    
    # Report Sections - Customize what appears in reports
    REPORT_SECTIONS: List[str] = [
        "Executive Summary",
        "Latest News",
        "Social Media Insights",
        "Market Analysis",
        "Emerging Trends",
        "Sources",
    ]
    
    # Advanced Settings
    MARKDOWN_OUTPUT: bool = True
    STREAM_RESPONSES: bool = False  # Set to True to stream responses
    DEBUG_MODE: bool = False  # Set to True for verbose logging
    
    # Geographic Focus (optional)
    GEOGRAPHIC_REGIONS: List[str] = [
        "Global",
        "North America",
        "Europe", 
        "Asia-Pacific",
        "Australia",
        "Africa",
        "South America",
    ]
    
    # Industry Focus (optional)
    INDUSTRY_SECTORS: List[str] = [
        "Mining and Extraction",
        "Battery Technology",
        "Electric Vehicles",
        "Renewable Energy",
        "Electronics Manufacturing",
        "Defense and Aerospace",
    ]
    
    @classmethod
    def get_search_query(cls, custom_minerals: List[str] = None) -> str:
        """
        Generate a search query based on configured or custom minerals.
        
        Args:
            custom_minerals: Optional list of specific minerals to search for
            
        Returns:
            Formatted search query string
        """
        minerals = custom_minerals or cls.CRITICAL_MINERALS
        minerals_str = ", ".join(minerals)
        return f"Latest developments in critical minerals including {minerals_str}"
    
    @classmethod
    def get_exa_config(cls) -> dict:
        """
        Get ExaTools configuration as a dictionary.
        
        Returns:
            Dictionary of ExaTools parameters
        """
        return {
            "category": cls.EXA_CATEGORY,
            "num_results": cls.EXA_NUM_RESULTS,
            "text_length_limit": cls.EXA_TEXT_LENGTH_LIMIT,
            "show_results": cls.EXA_SHOW_RESULTS,
        }
    
    @classmethod
    def get_output_path(cls) -> str:
        """
        Get the full output directory path.
        
        Returns:
            Output directory path string
        """
        from pathlib import Path
        return str(Path(__file__).parent / cls.OUTPUT_DIRECTORY)


# Predefined search queries for common use cases
SEARCH_QUERIES = {
    "general": (
        "Latest developments in critical minerals including "
        "lithium, cobalt, nickel, rare earth elements, and mining industry"
    ),
    "lithium": (
        "Latest news about lithium mining, lithium prices, "
        "lithium battery technology, and lithium supply chain"
    ),
    "geopolitics": (
        "Critical minerals geopolitics, supply chain security, trade policies, "
        "China rare earths, mining policy, and international competition"
    ),
    "sustainability": (
        "Sustainable mining practices, environmental impact of critical minerals, "
        "recycling technologies, and green mining innovations"
    ),
    "market": (
        "Critical minerals market prices, supply and demand trends, "
        "investment opportunities, and commodity trading"
    ),
    "technology": (
        "New mining technologies, critical minerals processing innovations, "
        "extraction techniques, and battery technology"
    ),
    "supply_chain": (
        "Critical minerals supply chain disruptions, logistics, "
        "transportation, and distribution networks"
    ),
    "policy": (
        "Government policies on critical minerals, regulations, "
        "strategic reserves, and international agreements"
    ),
}


# ExaTools domain filtering (optional)
# Uncomment and customize as needed
TRUSTED_DOMAINS = {
    "news": [
        "reuters.com",
        "bloomberg.com",
        "ft.com",
        "wsj.com",
        "mining.com",
        "mining-technology.com",
    ],
    "industry": [
        "mining.com",
        "mining-journal.com",
        "resourceworld.com",
        "mining-technology.com",
    ],
    "financial": [
        "bloomberg.com",
        "reuters.com",
        "ft.com",
        "marketwatch.com",
    ],
}


# Excluded terms (optional)
# Add terms you want to exclude from searches
EXCLUDED_TERMS: List[str] = [
    # Add any terms you want to exclude
]


def get_config() -> WorkflowConfig:
    """
    Get the workflow configuration instance.
    
    Returns:
        WorkflowConfig instance
    """
    return WorkflowConfig()


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    
    print("=== Workflow Configuration ===")
    print(f"Model: {config.MODEL_ID}")
    print(f"Number of results: {config.EXA_NUM_RESULTS}")
    print(f"Search category: {config.EXA_CATEGORY}")
    print(f"\nCritical Minerals: {', '.join(config.CRITICAL_MINERALS)}")
    print(f"\nDefault Query: {config.DEFAULT_QUERY}")
    print(f"\nOutput Directory: {config.get_output_path()}")
    print(f"\nExa Config: {config.get_exa_config()}")
    print("\nAvailable Search Queries:")
    for key, query in SEARCH_QUERIES.items():
        print(f"  - {key}: {query[:60]}...")
