"""LLM client for analyzing medical research articles"""

import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def analyze_articles(
    articles: List[Dict[str, Any]], 
    query: str,
    provider: str = "openai"
) -> str:
    """
    Analyze articles using LLM to generate insights.
    
    For MVP, this returns a formatted summary.
    In production, this would use the actual LLM API.
    """
    
    if not articles:
        return "No articles found to analyze."
    
    # MVP implementation - create structured summary
    summary = f"## Medical Research Summary\n\n"
    summary += f"**Query**: {query}\n"
    summary += f"**Articles Found**: {len(articles)}\n\n"
    
    summary += "### Key Findings\n\n"
    
    # Group by publication year
    year_counts = {}
    for article in articles:
        pub_date = article.get('publication_date', '')
        year = pub_date.split()[0] if pub_date else 'Unknown'
        year_counts[year] = year_counts.get(year, 0) + 1
    
    summary += "**Publication Timeline**:\n"
    for year in sorted(year_counts.keys(), reverse=True)[:5]:
        summary += f"- {year}: {year_counts[year]} articles\n"
    
    summary += "\n### Top Research Articles\n\n"
    
    # Detailed summary of top 5 articles
    for i, article in enumerate(articles[:5], 1):
        summary += f"#### {i}. {article['title']}\n"
        
        if article.get('authors'):
            authors = article['authors'][:3]
            summary += f"**Authors**: {', '.join(authors)}"
            if len(article['authors']) > 3:
                summary += f" et al."
            summary += "\n"
        
        summary += f"**Published**: {article.get('publication_date', 'Unknown')}\n"
        summary += f"**Journal**: {article.get('journal', 'Unknown')}\n"
        
        if article.get('abstract'):
            # First 200 characters of abstract
            abstract_preview = article['abstract'][:200]
            if len(article['abstract']) > 200:
                abstract_preview += "..."
            summary += f"**Abstract**: {abstract_preview}\n"
        
        summary += f"**PMID**: {article['pmid']}\n\n"
    
    if len(articles) > 5:
        summary += f"\n*... and {len(articles) - 5} additional articles.*\n"
    
    summary += "\n### Recommendations\n\n"
    summary += "1. Review the full abstracts of top-ranked articles\n"
    summary += "2. Check citation networks for seminal papers\n"
    summary += "3. Consider refining search with more specific terms\n"
    
    return summary