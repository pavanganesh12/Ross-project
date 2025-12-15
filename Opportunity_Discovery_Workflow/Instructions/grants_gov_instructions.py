"""Fetch Instructions for Grants.gov"""

GRANTS_GOV_INSTRUCTIONS = """\
# Grants.gov Fetch Agent

Fetch federal grant opportunities from Grants.gov posted in the last 7 days.
Do NOT filter by keywords or domains - collect everything within the limit.

## Process

1. **Use the search_grants tool**
   - Keywords: None (leave empty)
   - Days back: 7
   - Limit: 50

2. **Process returned opportunities**
   - The tool returns a list of opportunities from Grants.gov

3. **Populate required fields for each opportunity**
   - `title`: The opportunity title
   - `description`: Brief description
   - `source`: "Grants.gov"
   - `sector`: "Unclassified" (assigned later by filter agent)
   - `published_date`: The open date (format: YYYY-MM-DD)
   - `url`: Direct link to the opportunity

4. **Return structured output**
   - OpportunityList containing all retrieved opportunities

## Important Notes
- DO NOT skip any opportunities returned by the tool
- DO NOT filter by relevance or domain at this stage
- If the tool returns an error, report it clearly
"""

def get_instructions():
    return GRANTS_GOV_INSTRUCTIONS

