"""Generate and store keywords in database."""

import asyncio
from agno.db.sqlite import SqliteDb
from aegis.agents.keyword_agent import create_keyword_agent
from aegis.keyword_db import KeywordDatabase
from aegis.config import DB_FILE


async def generate_and_store_keywords():
    print("\n" + "="*70)
    print("KEYWORD GENERATION AND STORAGE")
    print("="*70 + "\n")
    
    keyword_db = KeywordDatabase(db_path="keywords.json")
    db = SqliteDb(db_file=DB_FILE)
    keyword_agent = create_keyword_agent(db)
    
    org_profile = """
    ORGANIZATION PROFILE FOR KEYWORD GENERATION:
    
    Technical Capabilities:
    - Critical minerals extraction (lithium, REEs, battery materials)
    - Lithium hydroxide via Direct Lithium Extraction (DLE)
    - Rare earth element separation and refining
    - AR/VR training systems for defense and industrial applications
    - AI/ML for predictive maintenance and computer vision
    - Autonomous systems and robotics
    - Advanced manufacturing and Industry 4.0
    
    Target Domains:
    1. Critical Minerals & Battery Materials
    2. Artificial Intelligence & Machine Learning  
    3. Defense & National Security
    4. AR/VR/XR Technologies
    5. Advanced Manufacturing
    6. Energy & Clean Technology
    
    Target Federal Programs: SBIR/STTR, BAAs, OTAs, FOAs, Grants
    Target Agencies: DOE, DoD, DARPA, NIST, USGS
    
    Generate comprehensive keywords for federal procurement opportunities.
    """
    
    print("🔄 Generating keywords...\n")
    
    try:
        response = await keyword_agent.arun(org_profile)
        
        if response and hasattr(response, 'content'):
            keyword_data = response.content
            print("\n✓ Keywords generated!\n")
            
            if hasattr(keyword_data, 'keyword_sets'):
                for keyword_set in keyword_data.keyword_sets:
                    domain = keyword_set.domain
                    
                    domain_mapping = {
                        'critical minerals': 'Critical_Minerals',
                        'battery materials': 'Critical_Minerals',
                        'artificial intelligence': 'AI_ML',
                        'machine learning': 'AI_ML',
                        'defense': 'Defense',
                        'ar/vr': 'AR_VR_XR',
                        'manufacturing': 'Manufacturing',
                        'energy': 'Energy',
                    }
                    
                    normalized_domain = domain_mapping.get(domain.lower(), domain.replace(' ', '_'))
                    
                    all_keywords = []
                    all_keywords.extend(keyword_set.primary_keywords)
                    all_keywords.extend(keyword_set.expanded_keywords)
                    
                    clean_keywords = []
                    for kw in all_keywords:
                        if any(op in kw for op in [' OR ', ' AND ', '(', ')', '"', ' / ']):
                            continue
                        if len(kw) > 60:
                            continue
                        clean_keywords.append(kw)
                    
                    keyword_db.set_domain_keywords(normalized_domain, clean_keywords)
                    print(f"  ✓ Stored {len(clean_keywords)} keywords: {normalized_domain}")
            
            print("\n" + "="*70)
            keyword_db.stats()
            print("✅ Complete! Keywords saved to: keywords.json\n")
            
        else:
            print("❌ Failed - no response from agent")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(generate_and_store_keywords())
