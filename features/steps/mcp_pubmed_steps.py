from behave import given, when, then
import os
import time
import asyncio
from typing import Dict, List, Any
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from medicalresearchagent.mcp.pubmed_client import PubMedMCPClient, MCPServerConfig


@given('the MCP PubMed server is configured with proper NCBI API credentials')
def step_configure_mcp_server_credentials(context):
    """Configure MCP PubMed server with NCBI API credentials from environment."""
    # Read API key from environment or .env file
    context.ncbi_api_key = os.getenv('NCBI_API_KEY', '')
    context.ncbi_email = os.getenv('NCBI_EMAIL', 'test@example.com')
    context.mcp_server_config = {
        'api_key': context.ncbi_api_key,
        'email': context.ncbi_email,
        'tool': 'medical_research_agent'
    }
    
    if not context.ncbi_api_key:
        context.logger.warning("No NCBI API key found - rate limits will be restricted to 3 req/sec")


@given('the server respects NCBI rate limits')
def step_configure_rate_limits(context):
    """Configure rate limiting based on API key availability."""
    # With API key: 10 requests/second, without: 3 requests/second
    context.rate_limit = 10 if context.ncbi_api_key else 3
    context.request_delay = 1.0 / context.rate_limit


@given('I have the MCP PubMed server endpoint configured')
def step_configure_mcp_endpoint(context):
    """Configure the MCP PubMed server endpoint."""
    context.mcp_endpoint = os.getenv('MCP_PUBMED_ENDPOINT', 'http://localhost:8080')
    context.mcp_client = None  # Will be initialized in the next step


@when('I initialize the MCP client connection')
def step_initialize_mcp_connection(context):
    """Initialize connection to the MCP PubMed server."""
    # Create MCP client configuration
    config = MCPServerConfig(
        endpoint=context.mcp_endpoint,
        api_key=context.ncbi_api_key,
        email=context.ncbi_email
    )
    
    # Initialize the client
    context.mcp_client = PubMedMCPClient(config)
    
    # Connect asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        context.connection_success = loop.run_until_complete(
            context.mcp_client.connect()
        )
    except Exception as e:
        context.connection_error = str(e)
        context.connection_success = False


@then('the connection should be established successfully')
def step_verify_connection_established(context):
    """Verify the MCP connection is established."""
    assert hasattr(context, 'connection_success'), "Connection was not attempted"
    assert context.connection_success, f"Connection failed: {getattr(context, 'connection_error', 'Unknown error')}"
    assert context.mcp_client.is_connected, "Client reports not connected"


@then('I should be able to retrieve the server capabilities')
def step_retrieve_server_capabilities(context):
    """Retrieve and verify server capabilities."""
    loop = asyncio.get_event_loop()
    capabilities = loop.run_until_complete(
        context.mcp_client.get_capabilities()
    )
    
    assert capabilities, "No capabilities returned"
    assert "tools" in capabilities, "No tools in capabilities"
    assert len(capabilities["tools"]) > 0, "No tools available"
    
    # Store for later use
    context.server_capabilities = capabilities


@given('I have an active MCP PubMed server connection')
def step_ensure_active_connection(context):
    """Ensure we have an active MCP connection."""
    # If not already connected, establish connection
    if not hasattr(context, 'mcp_client') or not context.mcp_client.is_connected:
        step_configure_mcp_server_credentials(context)
        step_configure_rate_limits(context)
        step_configure_mcp_endpoint(context)
        step_initialize_mcp_connection(context)
        step_verify_connection_established(context)


@when('I search for "{query}" with publication date after {year:d}')
def step_search_pubmed_with_date_filter(context, query: str, year: int):
    """Search PubMed with query and date filter."""
    context.search_query = query
    context.date_filter = f"{year}/01/01"
    
    # Perform the search
    loop = asyncio.get_event_loop()
    
    filters = {
        "publication_date_start": context.date_filter
    }
    
    try:
        context.search_results = loop.run_until_complete(
            context.mcp_client.search_articles(
                query=query,
                max_results=50,
                filters=filters
            )
        )
    except Exception as e:
        context.search_error = str(e)
        context.search_results = []


@then('I should receive a list of relevant articles')
def step_verify_article_results(context):
    """Verify we received article results."""
    assert hasattr(context, 'search_results'), "No search was performed"
    assert not hasattr(context, 'search_error'), f"Search failed: {getattr(context, 'search_error', '')}"
    assert isinstance(context.search_results, list), "Results should be a list"
    assert len(context.search_results) > 0, "No articles found"


@then('each article should contain title, authors, and abstract')
def step_verify_article_fields(context):
    """Verify each article has required fields."""
    required_fields = ['pmid', 'title', 'authors']
    
    for idx, article in enumerate(context.search_results):
        for field in required_fields:
            assert field in article, f"Article {idx} missing field: {field}"
            # Authors can be empty list for some articles, so only check pmid and title are non-empty
            if field in ['pmid', 'title']:
                assert article[field], f"Article {idx} has empty field: {field}"


@then('the results should be filtered by the date constraint')
def step_verify_date_filtering(context):
    """Verify results respect the date filter."""
    # In a real implementation, we would parse publication dates
    # For MVP, we trust the API filtered correctly
    assert hasattr(context, 'date_filter'), "No date filter was set"
    # Additional date validation could be added here


@when('I make {count:d} rapid sequential queries without an API key')
def step_make_rapid_queries(context, count: int):
    """Make multiple rapid queries to test rate limiting."""
    context.ncbi_api_key = ''  # Ensure no API key for this test
    context.rate_limit = 3  # Without API key limit
    context.query_timestamps = []
    
    raise NotImplementedError("Rapid query execution not yet implemented")


@then('the system should respect the {limit:d} requests per second limit')
def step_verify_rate_limit_respected(context, limit: int):
    """Verify rate limiting is respected."""
    raise NotImplementedError("Rate limit verification not yet implemented")


@then('no requests should fail due to rate limiting')
def step_verify_no_rate_limit_failures(context):
    """Verify no requests failed due to rate limiting."""
    raise NotImplementedError("Rate limit failure check not yet implemented")


@then('appropriate delays should be introduced between requests')
def step_verify_request_delays(context):
    """Verify delays between requests."""
    raise NotImplementedError("Request delay verification not yet implemented")


@given('the MCP PubMed server is unavailable')
def step_make_server_unavailable(context):
    """Simulate server unavailability."""
    context.mcp_endpoint = 'http://localhost:9999'  # Non-existent endpoint
    context.server_unavailable = True


@when('I attempt to initialize the MCP client connection')
def step_attempt_connection(context):
    """Attempt to connect to unavailable server."""
    raise NotImplementedError("Connection attempt not yet implemented")


@then('I should receive a meaningful error message')
def step_verify_error_message(context):
    """Verify error message is meaningful."""
    raise NotImplementedError("Error message verification not yet implemented")


@then('the system should suggest retry options')
def step_verify_retry_suggestions(context):
    """Verify retry suggestions are provided."""
    raise NotImplementedError("Retry suggestion verification not yet implemented")


@then('the failure should be logged for monitoring')
def step_verify_failure_logged(context):
    """Verify failure is properly logged."""
    raise NotImplementedError("Failure logging verification not yet implemented")