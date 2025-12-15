"""
Instructions module for Critical Minerals News agents.
Contains optimized, markdown-formatted instructions for each agent.
"""

from .news_instructions import NEWS_AGENT_INSTRUCTIONS
from .twitter_instructions import TWITTER_AGENT_INSTRUCTIONS
from .linkedin_instructions import LINKEDIN_AGENT_INSTRUCTIONS
from .csis_instructions import CSIS_AGENT_INSTRUCTIONS
from .aggregation_instructions import AGGREGATION_AGENT_INSTRUCTIONS
from .formatting_instructions import FORMATTING_AGENT_INSTRUCTIONS

__all__ = [
    "NEWS_AGENT_INSTRUCTIONS",
    "TWITTER_AGENT_INSTRUCTIONS",
    "LINKEDIN_AGENT_INSTRUCTIONS",
    "CSIS_AGENT_INSTRUCTIONS",
    "AGGREGATION_AGENT_INSTRUCTIONS",
    "FORMATTING_AGENT_INSTRUCTIONS",
]
