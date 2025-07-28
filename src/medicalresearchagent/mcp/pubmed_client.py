"""PubMed MCP Client implementation"""

import os
import json
import subprocess
import asyncio
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection"""
    endpoint: str
    api_key: Optional[str] = None
    email: Optional[str] = None
    rate_limit: int = 3  # requests per second
    

class PubMedMCPClient:
    """Client for connecting to PubMed MCP server"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.server_process = None
        self.capabilities = None
        self.is_connected = False
        self.client = httpx.AsyncClient()
        
        # Set rate limit based on API key
        if config.api_key:
            self.config.rate_limit = 10
        
    async def connect(self) -> bool:
        """Initialize connection to MCP server"""
        try:
            # For now, we'll simulate a connection to an MCP server
            # In production, this would start the actual MCP server process
            # or connect to an existing one
            
            # Check if we can reach the endpoint
            response = await self.client.get(
                f"{self.config.endpoint}/health",
                timeout=5.0
            )
            
            if response.status_code == 200:
                self.is_connected = True
                logger.info(f"Connected to MCP server at {self.config.endpoint}")
                return True
            
        except httpx.RequestError as e:
            # If the server isn't running, we'll start a local instance
            logger.info(f"MCP server not reachable at {self.config.endpoint}, starting local instance")
            return await self._start_local_server()
        
        return False
    
    async def _start_local_server(self) -> bool:
        """Start a local MCP server instance"""
        try:
            # For MVP, we'll use a simple HTTP endpoint simulation
            # In production, this would start the actual MCP server
            self.is_connected = True
            self.capabilities = {
                "tools": [
                    {
                        "name": "search_pubmed_articles",
                        "description": "Search PubMed for biomedical literature",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "maxResults": {"type": "number", "default": 50},
                                "filters": {"type": "object"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "fetch_article_content",
                        "description": "Fetch detailed content for specific articles",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pmids": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["pmids"]
                        }
                    }
                ],
                "resources": ["pubmed://articles"],
                "prompts": []
            }
            return True
            
        except Exception as e:
            logger.error(f"Failed to start local MCP server: {e}")
            return False
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Retrieve server capabilities"""
        if not self.is_connected:
            raise RuntimeError("Not connected to MCP server")
        
        return self.capabilities or {}
    
    async def search_articles(self, query: str, max_results: int = 50, 
                            filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search PubMed for articles"""
        if not self.is_connected:
            raise RuntimeError("Not connected to MCP server")
        
        # For MVP, we'll directly use NCBI E-utilities
        # In production, this would go through the MCP server
        return await self._direct_pubmed_search(query, max_results, filters)
    
    async def _direct_pubmed_search(self, query: str, max_results: int,
                                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Direct PubMed search using E-utilities"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
        # Build search query
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        if self.config.api_key:
            search_params["api_key"] = self.config.api_key
        
        # Apply filters
        if filters:
            if "publication_date_start" in filters:
                date_filter = f' AND ("{filters["publication_date_start"]}"[Date - Publication] : "3000"[Date - Publication])'
                search_params["term"] += date_filter
            
            if filters.get("open_access"):
                search_params["term"] += ' AND "open access"[filter]'
        
        try:
            # Search for PMIDs
            search_response = await self.client.get(
                f"{base_url}/esearch.fcgi",
                params=search_params
            )
            search_data = search_response.json()
            
            if "esearchresult" not in search_data:
                return []
            
            pmids = search_data["esearchresult"].get("idlist", [])
            
            if not pmids:
                return []
            
            # Fetch summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json"
            }
            
            if self.config.api_key:
                summary_params["api_key"] = self.config.api_key
            
            summary_response = await self.client.get(
                f"{base_url}/esummary.fcgi",
                params=summary_params
            )
            summary_data = summary_response.json()
            
            # Format results
            articles = []
            if "result" in summary_data:
                for pmid in pmids:
                    if pmid in summary_data["result"]:
                        article_data = summary_data["result"][pmid]
                        articles.append({
                            "pmid": pmid,
                            "title": article_data.get("title", ""),
                            "authors": [author.get("name", "") for author in article_data.get("authors", [])],
                            "abstract": article_data.get("abstract", ""),
                            "publication_date": article_data.get("pubdate", ""),
                            "journal": article_data.get("source", "")
                        })
            
            return articles
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.server_process:
            self.server_process.terminate()
            await asyncio.sleep(0.5)
            if self.server_process.poll() is None:
                self.server_process.kill()
        
        await self.client.aclose()
        self.is_connected = False
        logger.info("Disconnected from MCP server")