"""Simple workflow implementation for MVP without Prefect decorators"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from ..mcp.pubmed_client import PubMedMCPClient, MCPServerConfig
from ..models.database import db_manager
from ..utils.llm_client import analyze_articles

logger = logging.getLogger(__name__)


async def medical_research_flow_simple(
    query_text: str,
    filters: Optional[Dict[str, Any]] = None,
    query_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Simple workflow for processing medical research queries"""
    
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
        # Parse the query (simple implementation)
        parsed_filters = filters or {}
        if "maxResults" not in parsed_filters:
            parsed_filters["maxResults"] = 50
        max_results = parsed_filters.pop("maxResults", 50)
        
        logger.info(f"Processing query: {query_text}")
        
        # Connect to MCP server
        config = MCPServerConfig(
            endpoint="http://localhost:8080",
            api_key=api_key,
            email="research@example.com"
        )
        
        mcp_client = PubMedMCPClient(config)
        success = await mcp_client.connect()
        
        if not success:
            raise RuntimeError("Failed to connect to MCP server")
        
        logger.info("Connected to MCP PubMed server")
        
        # Search PubMed
        articles = await mcp_client.search_articles(
            query=query_text,
            max_results=max_results,
            filters=parsed_filters
        )
        
        logger.info(f"Found {len(articles)} articles")
        
        # Analyze results
        summary = await analyze_articles(articles, query_text)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update query in database
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
            logger.info(f"Saving {len(articles)} articles to database")
            saved_count = db_manager.save_articles(query_id, articles)
            logger.info(f"Saved {saved_count} articles to database")
        
        # Disconnect from MCP
        await mcp_client.disconnect()
        
        # Return final result
        query = db_manager.get_query(query_id)
        return query.to_dict() if query else {}
        
    except Exception as e:
        logger.error(f"Workflow error for query {query_id}: {str(e)}")
        
        db_manager.update_query(
            query_id,
            status="failed",
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        
        raise


def run_research_query_simple(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Run a research query synchronously (simple version)"""
    return asyncio.run(
        medical_research_flow_simple(
            query_text=query,
            filters=filters,
            api_key=api_key
        )
    )