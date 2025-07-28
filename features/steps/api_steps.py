from behave import given, when, then
import json
import time
import asyncio
from typing import Dict, Any
import os
import sys
import httpx
import uvicorn
import threading
import socket

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from medicalresearchagent.api.app import app


def find_free_port():
    """Find a free port to use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@given('the FastAPI server is running')
def step_ensure_fastapi_running(context):
    """Ensure FastAPI server is running."""
    # Check if server is already running
    try:
        response = httpx.get("http://localhost:8000/health")
        if response.status_code == 200:
            context.api_base_url = "http://localhost:8000"
            return
    except:
        pass
    
    # Find a free port
    port = find_free_port()
    context.api_base_url = f"http://localhost:{port}"
    
    # Start server in background thread if not already running
    if not hasattr(context, 'api_server_thread'):
        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
        
        context.api_server_thread = threading.Thread(target=run_server, daemon=True)
        context.api_server_thread.start()
        time.sleep(2)  # Give server time to start
    
    # Verify server is accessible
    try:
        response = httpx.get(f"{context.api_base_url}/health")
        assert response.status_code == 200
    except Exception as e:
        raise RuntimeError(f"FastAPI server is not accessible: {e}")


@given('authentication is configured')
def step_configure_authentication(context):
    """Configure API authentication."""
    context.auth_enabled = True
    context.test_api_key = os.getenv('TEST_API_KEY', 'test-api-key-for-development')


@given('the medical research workflow is available')
def step_ensure_workflow_available(context):
    """Ensure the medical research workflow is available."""
    # Workflow is built into the API
    context.workflow_available = True


@given('I have a valid API key')
def step_set_valid_api_key(context):
    """Set a valid API key for authentication."""
    context.api_key = os.getenv('TEST_API_KEY', 'test-valid-api-key')
    context.headers = {'Authorization': f'Bearer {context.api_key}'}


@when('I POST to "{endpoint}" with JSON payload')
def step_post_json_payload(context, endpoint: str):
    """Make POST request with JSON payload from docstring."""
    context.request_payload = json.loads(context.text)
    context.request_endpoint = endpoint
    context.request_timestamp = time.time()
    
    # Make the request
    response = httpx.post(
        f"{context.api_base_url}{endpoint}",
        json=context.request_payload,
        headers=context.headers if hasattr(context, 'headers') else {}
    )
    
    context.response = response
    context.response_time = time.time() - context.request_timestamp
    
    # Parse response if JSON
    try:
        context.response_json = response.json()
    except:
        context.response_json = None


@then('I should receive a {status_code:d} {status_text} response')
def step_verify_response_status(context, status_code: int, status_text: str):
    """Verify response status code and text."""
    assert hasattr(context, 'response'), "No response received"
    assert context.response.status_code == status_code, \
        f"Expected status {status_code}, got {context.response.status_code}"


@then('the response should contain a query_id')
def step_verify_query_id_in_response(context):
    """Verify response contains query_id."""
    assert context.response_json is not None, "Response is not JSON"
    assert "query_id" in context.response_json, "No query_id in response"
    assert context.response_json["query_id"], "Empty query_id"
    context.query_id = context.response_json["query_id"]


@then('the response should contain analyzed results')
def step_verify_analyzed_results(context):
    """Verify response contains analyzed results."""
    assert context.response_json is not None, "Response is not JSON"
    assert "status" in context.response_json, "No status in response"
    assert context.response_json["status"] == "completed", \
        f"Query not completed: {context.response_json.get('status')}"
    assert "summary" in context.response_json, "No summary in response"
    assert context.response_json["summary"], "Empty summary"


@then('the response time should be under {seconds:d} seconds')
def step_verify_response_time(context, seconds: int):
    """Verify response time is within limit."""
    assert hasattr(context, 'response_time'), "Response time not recorded"
    assert context.response_time < seconds, \
        f"Response took {context.response_time:.1f}s, expected < {seconds}s"


@given('I have an invalid API key')
def step_set_invalid_api_key(context):
    """Set an invalid API key."""
    context.api_key = 'invalid-api-key'
    context.headers = {'Authorization': f'Bearer {context.api_key}'}


@when('I POST to "{endpoint}" with a research query')
def step_post_research_query(context, endpoint: str):
    """Make POST request with a research query."""
    context.request_payload = {
        "query": "Test medical research query",
        "filters": {}
    }
    context.request_endpoint = endpoint
    
    raise NotImplementedError("POST request with query not yet implemented")


@then('the response should contain an authentication error message')
def step_verify_auth_error_message(context):
    """Verify authentication error message."""
    raise NotImplementedError("Auth error message verification not yet implemented")


@when('I POST to "{endpoint}" with invalid JSON')
def step_post_invalid_json(context, endpoint: str):
    """Make POST request with invalid JSON."""
    context.request_payload = json.loads(context.text)
    context.request_endpoint = endpoint
    
    raise NotImplementedError("POST request with invalid JSON not yet implemented")


@then('the response should detail the validation errors')
def step_verify_validation_errors(context):
    """Verify validation error details."""
    raise NotImplementedError("Validation error verification not yet implemented")


@when('I POST to "{endpoint}" with a complex research query')
def step_post_complex_query(context, endpoint: str):
    """Make POST request with complex query for async processing."""
    context.request_payload = {
        "query": "Comprehensive analysis of CRISPR-Cas9 applications in hereditary diseases with focus on recent clinical trials and safety profiles",
        "filters": {
            "publication_date_start": "2020-01-01",
            "open_access": True,
            "clinical_trials": True
        }
    }
    context.request_endpoint = endpoint
    
    raise NotImplementedError("Async POST request not yet implemented")


@then('the response should contain a task_id')
def step_verify_task_id_in_response(context):
    """Verify response contains task_id."""
    raise NotImplementedError("Task ID verification not yet implemented")


@when('I GET "{endpoint}"')
def step_get_endpoint(context, endpoint: str):
    """Make GET request to endpoint."""
    # Handle parameter substitution for {task_id}
    if '{task_id}' in endpoint and hasattr(context, 'task_id'):
        endpoint = endpoint.replace('{task_id}', context.task_id)
    
    context.request_endpoint = endpoint
    raise NotImplementedError("GET request execution not yet implemented")


@then('I should see the query processing status')
def step_verify_processing_status(context):
    """Verify query processing status."""
    raise NotImplementedError("Processing status verification not yet implemented")


@then('eventually the status should be "{expected_status}"')
def step_verify_eventual_status(context, expected_status: str):
    """Verify status eventually reaches expected value."""
    raise NotImplementedError("Eventual status verification not yet implemented")


@when('I POST to "{endpoint}" with multiple queries')
def step_post_batch_queries(context, endpoint: str):
    """Make POST request with batch queries."""
    context.request_payload = json.loads(context.text)
    context.request_endpoint = endpoint
    
    raise NotImplementedError("Batch POST request not yet implemented")


@then('the response should contain results for all queries')
def step_verify_batch_results(context):
    """Verify all batch queries have results."""
    raise NotImplementedError("Batch results verification not yet implemented")


@then('each result should have its own query_id')
def step_verify_individual_query_ids(context):
    """Verify each result has unique query_id."""
    raise NotImplementedError("Individual query ID verification not yet implemented")


@then('I should receive the OpenAPI documentation')
def step_verify_openapi_docs(context):
    """Verify OpenAPI documentation is received."""
    raise NotImplementedError("OpenAPI documentation verification not yet implemented")


@then('it should describe all available endpoints')
def step_verify_endpoint_descriptions(context):
    """Verify all endpoints are described."""
    raise NotImplementedError("Endpoint description verification not yet implemented")


@then('it should include request/response schemas')
def step_verify_schemas(context):
    """Verify request/response schemas are included."""
    raise NotImplementedError("Schema verification not yet implemented")