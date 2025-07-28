"""
Helper functions for BDD tests
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def wait_for_condition(condition_func, timeout: int = 30, interval: float = 1.0) -> bool:
    """
    Wait for a condition to become true within a timeout period.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
    
    Returns:
        True if condition was met, False if timeout occurred
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False


def parse_pubmed_date(date_str: str) -> datetime:
    """
    Parse PubMed date string to datetime object.
    
    Args:
        date_str: Date string from PubMed (various formats)
    
    Returns:
        datetime object
    """
    # Common PubMed date formats
    formats = [
        "%Y %b %d",
        "%Y %b",
        "%Y",
        "%Y-%m-%d",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def validate_article_structure(article: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that an article contains all required fields.
    
    Args:
        article: Article dictionary to validate
        required_fields: List of required field names
    
    Returns:
        True if all required fields are present
    """
    return all(field in article and article[field] for field in required_fields)


def calculate_request_delay(rate_limit: float) -> float:
    """
    Calculate delay between requests based on rate limit.
    
    Args:
        rate_limit: Maximum requests per second
    
    Returns:
        Delay in seconds
    """
    return 1.0 / rate_limit


def format_query_for_pubmed(query: str, filters: Dict[str, Any]) -> str:
    """
    Format a natural language query for PubMed search.
    
    Args:
        query: Natural language query
        filters: Dictionary of filters to apply
    
    Returns:
        Formatted PubMed query string
    """
    formatted_query = query
    
    # Add date filter
    if 'publication_date_start' in filters:
        date_filter = f'("{filters["publication_date_start"]}"[Date - Publication] : "3000"[Date - Publication])'
        formatted_query = f'({formatted_query}) AND {date_filter}'
    
    # Add open access filter
    if filters.get('open_access'):
        formatted_query = f'({formatted_query}) AND "open access"[filter]'
    
    # Add clinical trials filter
    if filters.get('clinical_trials'):
        formatted_query = f'({formatted_query}) AND "clinical trial"[Publication Type]'
    
    return formatted_query


def mock_llm_analysis(articles: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """
    Mock LLM analysis for testing purposes.
    
    Args:
        articles: List of articles to analyze
        query: Original query
    
    Returns:
        Mock analysis result
    """
    return {
        "summary": f"Analysis of {len(articles)} articles related to '{query}'",
        "key_findings": [
            f"Finding from article: {article.get('title', 'Unknown')[:50]}..."
            for article in articles[:3]
        ],
        "recommendations": [
            "Further research recommended",
            "Consider clinical implications"
        ],
        "confidence_score": 0.85
    }


def generate_mock_api_response(query: str, query_id: str = None) -> Dict[str, Any]:
    """
    Generate a mock API response for testing.
    
    Args:
        query: The query string
        query_id: Optional query ID
    
    Returns:
        Mock API response
    """
    import uuid
    
    return {
        "query_id": query_id or str(uuid.uuid4()),
        "status": "completed",
        "results": {
            "articles": [
                {
                    "pmid": "12345678",
                    "title": f"Mock article about {query}",
                    "abstract": f"This is a mock abstract discussing {query}...",
                    "authors": ["Smith J", "Doe J"],
                    "publication_date": "2023-01-15",
                    "journal": "Mock Medical Journal"
                }
            ],
            "summary": f"Mock analysis of articles about {query}",
            "total_count": 1
        },
        "metadata": {
            "processing_time": 2.5,
            "filters_applied": {}
        }
    }


def verify_rate_limiting(timestamps: List[float], max_rate: float) -> bool:
    """
    Verify that a series of request timestamps respects rate limiting.
    
    Args:
        timestamps: List of request timestamps
        max_rate: Maximum requests per second
    
    Returns:
        True if rate limiting is respected
    """
    if len(timestamps) < 2:
        return True
    
    min_interval = 1.0 / max_rate
    
    for i in range(1, len(timestamps)):
        interval = timestamps[i] - timestamps[i-1]
        if interval < min_interval * 0.9:  # Allow 10% tolerance
            return False
    
    return True