"""Filter Instructions for Opportunity Discovery Workflow."""

import json

def get_filter_instructions():
    # Load keywords from file to embed in instructions
    keywords_path = r"d:\Agno\keywords.json"
    
    try:
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords_data = json.load(f)
            keywords = keywords_data.get('keywords', {})
    except:
        keywords = {}
    
    keywords_json = json.dumps(keywords, indent=4)
    
    return f"""\
# Filter Agent

Filter opportunities based on relevance to specific domains and keywords.
You will receive a list of opportunities in the prompt.

## Domains
- Critical Minerals & Battery Materials
- Artificial Intelligence & Machine Learning
- AR, VR, and XR Technologies
- Manufacturing
- Energy & Clean Technology

## Keywords
```json
{keywords_json}
```

## Process

1. **Review each opportunity**
   - Check the title and description of each opportunity

2. **Match keywords**
   - Check if ANY keyword from ANY domain (EXCEPT "Negative_Keywords_To_Exclude") appears in title or description
   - If an opportunity matches any keyword in "Negative_Keywords_To_Exclude", DISCARD it immediately
   - Matching is case-insensitive
   - Partial matches are acceptable (e.g., "battery" matches "batteries")

3. **Assign sectors**
   - When an opportunity matches keywords from a domain, assign that domain as the sector
   - If multiple domains match, choose the BEST match based on:
     - Number of keyword matches
     - Strength of relevance
   - Format sector names exactly as shown in domains list

4. **Return filtered list**
   - ONLY return opportunities that match at least one keyword
   - Each opportunity must have: title, description, source, sector, published_date, url

## Important Notes
- Be thorough - don't miss relevant opportunities
- Be precise - only include opportunities that genuinely match the keywords
- If an opportunity doesn't match any keywords, DO NOT include it in the output

## Output
Return a structured OpportunityList containing only the filtered, domain-matched opportunities with assigned sectors.
"""


