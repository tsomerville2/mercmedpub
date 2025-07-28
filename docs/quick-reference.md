# Medical Research Agent Quick Reference

## Key Components

### MCP PubMed Servers
- **Primary**: `cyanheads/pubmed-mcp-server` (TypeScript, full-featured)
- **Alternative**: `andybrandt/mcp-simple-pubmed` (XML-focused)
- **Python**: `grll/pubmedmcp` (Python implementation)

### API Endpoints
```
POST /api/query                 # Submit research query
GET  /api/query/status/{id}     # Check query status
POST /api/query/batch           # Submit multiple queries
GET  /docs                      # API documentation
```

### NCBI E-utilities Rate Limits
- **No API Key**: 3 requests/second
- **With API Key**: 10 requests/second
- **Get Key**: https://www.ncbi.nlm.nih.gov/account/settings/

## Environment Variables

```bash
# Required
NCBI_API_KEY=your_key_here
NCBI_EMAIL=your_email@example.com

# Optional
MCP_PUBMED_ENDPOINT=http://localhost:8080
API_BASE_URL=http://localhost:8000
PREFECT_API_URL=http://localhost:4200
LLM_PROVIDER=openai
LLM_API_KEY=your_llm_key
```

## Quick Commands

### BDD Testing
```bash
# Run all tests
behave

# Run specific feature
behave features/mcp_pubmed_integration.feature

# Run by tag
behave --tags @critical

# Generate report
behave --format json.pretty --outfile reports/results.json
```

### MCP Server Setup
```bash
# Install MCP server
npm install @cyanheads/pubmed-mcp-server

# Configure in claude_desktop_config.json
{
  "mcpServers": {
    "pubmed": {
      "command": "node",
      "args": ["node_modules/@cyanheads/pubmed-mcp-server/dist/index.js"]
    }
  }
}
```

## PubMed Search Syntax

### Basic Operators
- `AND` - Both terms required
- `OR` - Either term
- `NOT` - Exclude term
- `"phrase"` - Exact phrase

### Field Tags
- `[Author]` - Author name
- `[Title]` - Article title
- `[MeSH]` - MeSH terms
- `[Journal]` - Journal name
- `[pdat]` - Publication date

### Examples
```
"machine learning"[Title] AND cancer[MeSH] AND 2020:2023[pdat]
"COVID-19"[Title] AND "open access"[filter]
Smith J[Author] AND Harvard[Affiliation]
```

## Common MCP Tools

### search_pubmed_articles
```json
{
  "query": "string",
  "maxResults": 100,
  "filters": {
    "publicationDateStart": "2023-01-01",
    "openAccess": true
  }
}
```

### fetch_pubmed_content
```json
{
  "pmids": ["12345678", "87654321"],
  "includeFullText": true
}
```

### get_pubmed_article_connections
```json
{
  "pmid": "12345678",
  "connectionType": "citations"
}
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 429 | Rate limit exceeded | Add API key or slow down |
| 401 | Unauthorized | Check API credentials |
| 422 | Invalid request | Verify query syntax |
| 500 | Server error | Retry with backoff |

## Prefect Workflow Tasks

1. **QueryParser** - Convert natural language to PubMed syntax
2. **DataRetriever** - Fetch articles via MCP
3. **FilterTask** - Apply user filters
4. **LLMAnalyzer** - AI analysis of results
5. **ResponseHandler** - Format final output

## Performance Tips

1. **Use API Keys**: 3x higher rate limit
2. **Batch Requests**: Process multiple queries together
3. **Cache Results**: Avoid duplicate API calls
4. **Off-Peak Hours**: Run large jobs 9 PM - 5 AM EST
5. **Specific Queries**: Use field tags for precision

## Monitoring

### Prefect Dashboard
- View workflow runs
- Monitor task performance
- Check error logs

### Custom Metrics
- Request rate
- Response times
- Error rates
- Cache hit ratio

## Troubleshooting

### MCP Connection Issues
1. Check server is running
2. Verify endpoint URL
3. Test with curl/postman
4. Check firewall rules

### Rate Limiting
1. Add NCBI API key
2. Implement retry logic
3. Use exponential backoff
4. Monitor request rate

### Empty Results
1. Verify query syntax
2. Check date ranges
3. Remove filters gradually
4. Test in PubMed directly

## Useful Links

- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
- [PubMed Help](https://pubmed.ncbi.nlm.nih.gov/help/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Prefect Docs](https://docs.prefect.io/)
- [Get NCBI API Key](https://www.ncbi.nlm.nih.gov/account/settings/)