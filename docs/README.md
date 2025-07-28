# Medical Research Agent Documentation

This directory contains comprehensive documentation for the Medical Research Agent project, which uses the Model Context Protocol (MCP) to integrate with PubMed's biomedical literature database.

## Documentation Structure

### Architecture Documentation
- **[Technology Overview](architecture/technology-overview.md)** - High-level system architecture, core technologies, and implementation details

### MCP Documentation
- **[General MCP Usage Guide](mcp/general-mcp-usage-guide.md)** - Comprehensive guide to understanding and using MCP servers
- **[Claude Code MCP Guide](mcp/claude-code-mcp-guide.md)** - MCP usage specifically within Claude Code environment
- **[PubMed MCP Integration Guide](mcp/pubmed-mcp-integration-guide.md)** - Complete guide for integrating MCP servers with the project
- **[MCP Protocol Details](mcp/mcp-protocol-details.md)** - Technical details about the Model Context Protocol implementation

### API Documentation
- **[NCBI E-utilities API Guide](api/ncbi-eutils-api-guide.md)** - Comprehensive guide to using NCBI's E-utilities API with rate limits and best practices

### Quick References
- **[Quick Reference Guide](quick-reference.md)** - Essential commands, configurations, and troubleshooting tips

## Key Technologies

1. **Model Context Protocol (MCP)** - Standardized protocol for LLM-service integration
2. **NCBI E-utilities** - PubMed's API for biomedical literature access
3. **Prefect** - Workflow orchestration framework
4. **FastAPI** - Modern web API framework

## Getting Started

1. Review the [Technology Overview](architecture/technology-overview.md) for system understanding
2. Follow the [PubMed MCP Integration Guide](mcp/pubmed-mcp-integration-guide.md) for setup
3. Reference the [NCBI API Guide](api/ncbi-eutils-api-guide.md) for rate limits and usage
4. Keep the [Quick Reference](quick-reference.md) handy during development

## External Resources

- [MCPmed GitHub](https://github.com/MCPmed) - MCPmed organization repositories
- [MCPmed Paper](https://arxiv.org/html/2507.08055v1) - Academic paper on MCP for bioinformatics
- [NCBI Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25497/) - Official E-utilities documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

## Contributing

When adding new documentation:
1. Follow the existing structure and formatting
2. Include practical examples and code snippets
3. Keep technical accuracy while maintaining readability
4. Update this README with new document links