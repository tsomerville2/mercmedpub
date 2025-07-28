# PubMed MCP Server Integration Guide

## Overview

The PubMed MCP (Model Context Protocol) Server provides a standardized interface for AI agents and research tools to interact with PubMed's vast biomedical literature database. This guide covers integration approaches, available implementations, and best practices.

## Available MCP Server Implementations

### 1. cyanheads/pubmed-mcp-server (Recommended)
**Repository**: https://github.com/cyanheads/pubmed-mcp-server

**Key Features**:
- TypeScript-based with robust error handling
- Full integration with NCBI E-utilities API
- Supports both stdio and HTTP transport modes
- Strong type safety and authentication utilities
- Research agent scaffold included

**Main Tools**:
- `search_pubmed_articles` - Advanced search with filtering
- `fetch_pubmed_content` - Retrieve detailed article content
- `get_pubmed_article_connections` - Find article citations and relationships
- `pubmed_research_agent` - Generate research plans
- `generate_pubmed_chart` - Create data visualizations

**Installation**:
```bash
npm install @cyanheads/pubmed-mcp-server
```

### 2. andybrandt/mcp-simple-pubmed
**Repository**: https://github.com/andybrandt/mcp-simple-pubmed

**Key Features**:
- Returns XML-formatted full text (preferred by AI models)
- Simple, lightweight implementation
- Easy integration via Smithery

**Installation via Smithery**:
```bash
npx -y @smithery/cli install mcp-simple-pubmed --client claude
```

### 3. grll/pubmedmcp
**Repository**: https://github.com/grll/pubmedmcp

**Key Features**:
- Python-based implementation
- Uses pubmedclient Python package
- Search and fetch operations

### 4. JackKuo666/PubMed-MCP-Server
**Repository**: https://github.com/JackKuo666/PubMed-MCP-Server

**Key Features**:
- Simple MCP interface
- Keyword search functionality
- Metadata access and analysis

## Integration Approaches

### 1. Direct npm/pip Installation
For TypeScript/JavaScript projects:
```bash
npm install @cyanheads/pubmed-mcp-server
```

For Python projects:
```bash
pip install pubmedmcp
```

### 2. Claude Desktop Configuration
Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pubmed": {
      "command": "node",
      "args": ["path/to/pubmed-mcp-server/dist/index.js"],
      "env": {
        "NCBI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 3. Programmatic Integration
```typescript
import { MCPClient } from '@modelcontextprotocol/sdk';
import { PubMedServer } from '@cyanheads/pubmed-mcp-server';

const server = new PubMedServer({
  apiKey: process.env.NCBI_API_KEY,
  email: process.env.NCBI_EMAIL
});

// Initialize and use the server
await server.start();
```

## Core Capabilities

### 1. Article Search
- Query PubMed using natural language or structured queries
- Filter by date range, publication type, open access status
- Sort by relevance, date, or other criteria
- Respect NCBI rate limits automatically

### 2. Content Retrieval
- Fetch article abstracts and metadata
- Access author information and affiliations
- Retrieve journal details and publication dates
- Get MeSH terms and keywords

### 3. Citation Analysis
- Find articles that cite a given paper
- Discover related articles
- Build citation networks
- Track research trends

### 4. Research Planning
- Generate research plans based on queries
- Identify key papers in a field
- Create literature review outlines
- Suggest related research directions

## Best Practices

### 1. API Key Management
- Always use an NCBI API key for better rate limits (10 req/sec vs 3 req/sec)
- Store API keys securely in environment variables
- Never commit API keys to version control

### 2. Rate Limiting
- Implement exponential backoff for retries
- Monitor request rates to avoid hitting limits
- Use batch operations where possible
- Schedule large jobs during off-peak hours (9 PM - 5 AM EST)

### 3. Error Handling
```typescript
try {
  const results = await server.searchArticles({
    query: "COVID-19 vaccines",
    maxResults: 100
  });
} catch (error) {
  if (error.code === 'RATE_LIMIT_EXCEEDED') {
    // Wait and retry
    await sleep(1000);
  } else if (error.code === 'INVALID_API_KEY') {
    // Handle authentication error
  }
}
```

### 4. Query Optimization
- Use specific search terms for better results
- Combine with date filters to reduce result sets
- Leverage MeSH terms for precise searches
- Use field tags (e.g., [Author], [Title]) for targeted searches

## Integration with Prefect Workflow

For the Medical Research Agent project, integrate the MCP server within Prefect tasks:

```python
from prefect import task, flow
import asyncio
from mcp_client import MCPClient

@task
async def search_pubmed(query: str, filters: dict):
    """Search PubMed using MCP server"""
    client = MCPClient("pubmed")
    results = await client.call_tool(
        "search_pubmed_articles",
        {
            "query": query,
            "filters": filters
        }
    )
    return results

@flow
async def medical_research_flow(query: str):
    """Main research workflow"""
    # Search articles
    articles = await search_pubmed(query, {
        "maxResults": 50,
        "sortOrder": "relevance"
    })
    
    # Process results...
    return articles
```

## Security Considerations

1. **API Key Security**:
   - Use environment variables or secure vaults
   - Rotate keys periodically
   - Monitor usage for anomalies

2. **Data Privacy**:
   - Be aware of data retention policies
   - Don't store sensitive patient information
   - Follow HIPAA guidelines if applicable

3. **Access Control**:
   - Implement authentication for your MCP endpoints
   - Use rate limiting at the application level
   - Log all access for audit purposes

## Troubleshooting

### Common Issues

1. **Rate Limit Errors**:
   - Error: "API rate limit exceeded"
   - Solution: Add API key or reduce request frequency

2. **Connection Failures**:
   - Error: "Failed to connect to MCP server"
   - Solution: Check server is running and accessible

3. **Invalid Queries**:
   - Error: "Invalid search query"
   - Solution: Validate query syntax and special characters

4. **Authentication Errors**:
   - Error: "Invalid API key"
   - Solution: Verify API key is correct and active

## Resources

- [NCBI E-utilities Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [PubMed Search Help](https://pubmed.ncbi.nlm.nih.gov/help/)
- [NCBI API Key Registration](https://www.ncbi.nlm.nih.gov/account/settings/)