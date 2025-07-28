"""Prefect workflow for medical research queries"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
import prefect.settings
import os

# Disable Prefect API for local execution
os.environ["PREFECT_API_URL"] = ""
prefect.settings.PREFECT_API_ENABLED = False

from ..mcp.pubmed_client import PubMedMCPClient, MCPServerConfig
from ..models.database import db_manager
from ..utils.llm_client import analyze_articles

logger = logging.getLogger(__name__)


@task(name="Parse Query")
def parse_query(query_text: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Parse natural language query into structured search parameters"""
    # For MVP, we'll use the query as-is
    # In production, this would use NLP to extract entities, dates, etc.
    
    parsed = {
        "query": query_text,
        "filters": filters or {}
    }
    
    # Apply default filters if not specified
    if "maxResults" not in parsed["filters"]:
        parsed["filters"]["maxResults"] = 50
    
    logger.info(f"Parsed query: {parsed}")
    return parsed


@task(name="Connect to MCP Server")
async def connect_to_mcp_server(api_key: Optional[str] = None) -> PubMedMCPClient:
    """Initialize and connect to MCP PubMed server"""
    config = MCPServerConfig(
        endpoint="http://localhost:8080",
        api_key=api_key,
        email="research@example.com"
    )
    
    client = PubMedMCPClient(config)
    success = await client.connect()
    
    if not success:
        raise RuntimeError("Failed to connect to MCP server")
    
    logger.info("Connected to MCP PubMed server")
    return client


@task(name="Search PubMed")
async def search_pubmed(
    client: PubMedMCPClient,
    query: str,
    filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Search PubMed for articles using MCP client"""
    try:
        max_results = filters.pop("maxResults", 50)
        articles = await client.search_articles(
            query=query,
            max_results=max_results,
            filters=filters
        )
        
        logger.info(f"Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        logger.error(f"Error searching PubMed: {e}")
        raise


@task(name="Analyze Articles")
async def analyze_articles_task(articles: List[Dict[str, Any]], query: str) -> str:
    """Analyze articles using LLM to generate summary"""
    if not articles:
        return "No articles found for the given query."
    
    # For MVP, create a simple summary
    # In production, this would use the configured LLM
    summary = f"Found {len(articles)} articles related to '{query}'.\n\n"
    
    # Add top 3 article summaries
    for i, article in enumerate(articles[:3], 1):
        summary += f"{i}. {article['title']}\n"
        if article.get('authors'):
            summary += f"   Authors: {', '.join(article['authors'][:3])}"
            if len(article['authors']) > 3:
                summary += f" et al."
            summary += "\n"
        summary += f"   Published: {article.get('publication_date', 'Unknown')}\n\n"
    
    if len(articles) > 3:
        summary += f"... and {len(articles) - 3} more articles.\n"
    
    return summary


@task(name="Save Results")
def save_results(
    query_id: str,
    articles: List[Dict[str, Any]],
    summary: str,
    processing_time: float
) -> Dict[str, Any]:
    """Save query results to database"""
    # Update query status
    db_manager.update_query(
        query_id,
        status="completed",
        completed_at=datetime.utcnow(),
        processing_time=processing_time,
        article_count=len(articles),
        summary=summary
    )
    
    # Save articles
    if articles:
        db_manager.save_articles(query_id, articles)
    
    # Return final result
    query = db_manager.get_query(query_id)
    return query.to_dict() if query else {}


@task(name="Handle Error")
def handle_error(query_id: str, error_message: str):
    """Handle workflow errors"""
    logger.error(f"Workflow error for query {query_id}: {error_message}")
    
    db_manager.update_query(
        query_id,
        status="failed",
        completed_at=datetime.utcnow(),
        error_message=error_message
    )


@flow(
    name="Medical Research Query Flow",
    task_runner=ConcurrentTaskRunner()
)
async def medical_research_flow(
    query_text: str,
    filters: Optional[Dict[str, Any]] = None,
    query_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Main workflow for processing medical research queries"""
    
    start_time = datetime.utcnow()
    
    # Generate query ID if not provided
    if not query_id:
        query_id = str(uuid.uuid4())
    
    # Save initial query to database
    db_manager.save_query({
        "id": query_id,
        "query_text": query_text,
        "filters": filters,
        "status": "processing"
    })
    
    try:
        # Parse the query
        parsed_query = parse_query(query_text, filters)
        
        # Connect to MCP server
        mcp_client = await connect_to_mcp_server(api_key)
        
        # Search PubMed
        articles = await search_pubmed(
            mcp_client,
            parsed_query["query"],
            parsed_query["filters"]
        )
        
        # Analyze results
        summary = await analyze_articles_task(articles, query_text)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Save results
        result = save_results(query_id, articles, summary, processing_time)
        
        # Disconnect from MCP
        await mcp_client.disconnect()
        
        return result
        
    except Exception as e:
        handle_error(query_id, str(e))
        raise


# Convenience function for running the flow
def run_research_query(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Run a research query synchronously"""
    return asyncio.run(
        medical_research_flow(
            query_text=query,
            filters=filters,
            api_key=api_key
        )
    )