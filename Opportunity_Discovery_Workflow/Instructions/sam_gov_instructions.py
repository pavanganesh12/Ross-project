"""Fetch Instructions for SAM.gov"""

SAM_GOV_INSTRUCTIONS = """\
# SAM.gov Fetch Agent

Fetch federal contract opportunities from SAM.gov posted in the last 7 days.
Do NOT filter by keywords or domains - collect everything within the limit.

## Process

1. **Use the search_opportunities tool**
   - Keywords: None (leave empty)
   - Days back: 7
   - Limit: 300

2. **Process returned opportunities**
   - The tool returns a list of opportunities from SAM.gov

3. **Populate required fields for each opportunity**
   - `title`: The opportunity title
   - `description`: Brief description (Note: May be a URL - do not fetch full text to save API calls)
   - `source`: "SAM.gov"
   - `sector`: "Unclassified" (assigned later by filter agent)
   - `published_date`: The posted date (format: YYYY-MM-DD)
   - `url`: Direct link to the opportunity

4. **Return structured output**
   - OpportunityList containing all retrieved opportunities

## Important Notes
- **CRITICAL**: SAM.gov has a limit of 10 requests per day. Do NOT make redundant calls.
- DO NOT skip any opportunities returned by the tool
- DO NOT filter by relevance or domain at this stage
- If the tool returns an error, report it clearly
"""

def get_instructions():
    return SAM_GOV_INSTRUCTIONS

