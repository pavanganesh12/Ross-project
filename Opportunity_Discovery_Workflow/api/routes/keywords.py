"""
Keywords API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Optional

from ..schemas.keywords import (
    KeywordDomain,
    KeywordsResponse,
    KeywordsUpdateRequest,
    KeywordAddRequest,
    KeywordDeleteRequest,
    KeywordSearchRequest,
)
from ..services.keyword_service import KeywordService

router = APIRouter(prefix="/keywords", tags=["Keywords"])

# Initialize service
keyword_service = KeywordService()


@router.get(
    "",
    response_model=KeywordsResponse,
    summary="List All Keywords",
    description="Get all keywords organized by domain."
)
async def list_keywords():
    """
    Get all keywords grouped by domain.
    
    Returns domains with their keywords, plus negative keywords for exclusion.
    """
    return keyword_service.get_all_keywords()


@router.get(
    "/search",
    response_model=Dict[str, List[str]],
    summary="Search Keywords",
    description="Search for keywords matching a query."
)
async def search_keywords(
    query: str = Query(..., min_length=2, description="Search query"),
    domain: Optional[str] = Query(default=None, description="Limit search to specific domain"),
):
    """
    Search for keywords containing the query string.
    
    - **query**: The search query (case-insensitive)
    - **domain**: Optional domain to limit the search
    """
    results = keyword_service.search_keywords(query, domain)
    
    if not results:
        return {}
    
    return results


@router.get(
    "/negative",
    response_model=List[str],
    summary="Get Negative Keywords",
    description="Get the list of keywords to exclude from filtering."
)
async def get_negative_keywords():
    """
    Get the list of negative keywords.
    
    These keywords are used to exclude irrelevant opportunities.
    """
    return keyword_service.get_negative_keywords()


@router.put(
    "/negative",
    response_model=List[str],
    summary="Update Negative Keywords",
    description="Update the list of negative keywords."
)
async def update_negative_keywords(
    keywords: List[str],
    append: bool = Query(default=False, description="Append to existing instead of replacing"),
):
    """
    Update the negative keywords list.
    
    - **keywords**: List of keywords
    - **append**: If True, adds to existing list; if False, replaces the list
    """
    return keyword_service.update_negative_keywords(keywords, append)


@router.get(
    "/domains",
    response_model=List[str],
    summary="List Domain Names",
    description="Get just the names of all keyword domains."
)
async def list_domain_names():
    """
    Get a list of all domain names (without keywords).
    """
    response = keyword_service.get_all_keywords()
    return [domain.name for domain in response.domains]


@router.get(
    "/domain/{domain_name}",
    response_model=KeywordDomain,
    summary="Get Domain Keywords",
    description="Get keywords for a specific domain."
)
async def get_domain_keywords(domain_name: str):
    """
    Get keywords for a specific domain.
    
    - **domain_name**: Name of the domain
    """
    domain = keyword_service.get_domain_keywords(domain_name)
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_name}' not found"
        )
    
    return domain


@router.post(
    "/domain",
    response_model=KeywordDomain,
    status_code=status.HTTP_201_CREATED,
    summary="Add New Domain",
    description="Add a new domain with keywords."
)
async def add_domain(request: KeywordAddRequest):
    """
    Add a new keyword domain.
    
    - **domain**: Name for the new domain
    - **keywords**: List of keywords for this domain
    """
    try:
        return keyword_service.add_domain(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put(
    "/domain/{domain_name}",
    response_model=KeywordDomain,
    summary="Update Domain Keywords",
    description="Update keywords for an existing domain."
)
async def update_domain_keywords(
    domain_name: str,
    keywords: List[str],
    append: bool = Query(default=False, description="Append to existing instead of replacing"),
):
    """
    Update keywords for an existing domain.
    
    - **domain_name**: Name of the domain to update
    - **keywords**: New list of keywords
    - **append**: If True, adds to existing keywords; if False, replaces all keywords
    """
    request = KeywordsUpdateRequest(
        domain=domain_name,
        keywords=keywords,
        append=append,
    )
    
    return keyword_service.update_domain_keywords(request)


@router.delete(
    "/domain/{domain_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Domain",
    description="Delete an entire domain and all its keywords."
)
async def delete_domain(domain_name: str):
    """
    Delete a domain and all its keywords.
    
    - **domain_name**: Name of the domain to delete
    
    Warning: This action cannot be undone.
    """
    deleted = keyword_service.delete_domain(domain_name)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_name}' not found"
        )
    
    return None


@router.delete(
    "/domain/{domain_name}/keywords",
    response_model=KeywordDomain,
    summary="Delete Keywords from Domain",
    description="Delete specific keywords from a domain."
)
async def delete_keywords_from_domain(
    domain_name: str,
    keywords: List[str] = Query(..., description="Keywords to delete"),
):
    """
    Delete specific keywords from a domain.
    
    - **domain_name**: Name of the domain
    - **keywords**: List of keywords to remove
    """
    result = keyword_service.delete_keywords_from_domain(domain_name, keywords)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_name}' not found"
        )
    
    return result
