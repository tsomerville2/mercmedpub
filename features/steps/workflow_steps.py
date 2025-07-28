from behave import given, when, then
import time
import asyncio
from typing import List, Dict, Any
import os
import sys
import uuid

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from medicalresearchagent.workflow.simple_flow import medical_research_flow_simple
from medicalresearchagent.models.database import db_manager


@given('the Prefect workflow is configured')
def step_configure_prefect_workflow(context):
    """Configure the Prefect workflow with necessary settings."""
    context.prefect_config = {
        'api_url': os.getenv('PREFECT_API_URL', 'http://localhost:4200'),
        'project': 'medical-research-agent',
        'flow_name': 'medical_research_query_flow'
    }
    # Workflow is configured in the module
    context.workflow_configured = True


@given('the MCP PubMed server is accessible')
def step_verify_mcp_accessible(context):
    """Verify MCP PubMed server is accessible."""
    # This is verified when the workflow runs
    context.mcp_accessible = True


@given('an LLM API is configured for analysis')
def step_configure_llm_api(context):
    """Configure LLM API for analysis."""
    context.llm_config = {
        'provider': os.getenv('LLM_PROVIDER', 'openai'),
        'api_key': os.getenv('LLM_API_KEY', ''),
        'model': os.getenv('LLM_MODEL', 'gpt-4')
    }
    # For MVP, we use the mock LLM implementation
    context.llm_configured = True


@given('I have a query "{query}"')
def step_set_query(context, query: str):
    """Set the research query."""
    context.current_query = query
    context.query_timestamp = time.time()


@when('I submit the query to the Prefect workflow')
def step_submit_query_to_workflow(context):
    """Submit query to Prefect workflow."""
    context.query_id = str(uuid.uuid4())
    context.workflow_start_time = time.time()
    
    # Run the workflow
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        context.workflow_result = loop.run_until_complete(
            medical_research_flow_simple(
                query_text=context.current_query,
                query_id=context.query_id,
                api_key=os.getenv('NCBI_API_KEY')
            )
        )
        context.workflow_error = None
    except Exception as e:
        context.workflow_error = str(e)
        context.workflow_result = None


@then('the query should be parsed into PubMed search parameters')
def step_verify_query_parsed(context):
    """Verify query is parsed correctly."""
    assert context.workflow_result is not None, f"Workflow failed: {context.workflow_error}"
    assert "query" in context.workflow_result, "No query in result"
    assert context.workflow_result["query"] == context.current_query


@then('relevant articles should be retrieved from PubMed')
def step_verify_articles_retrieved(context):
    """Verify articles are retrieved."""
    assert context.workflow_result is not None, "No workflow result"
    assert "article_count" in context.workflow_result, "No article count in result"
    assert context.workflow_result["article_count"] > 0, f"No articles retrieved, result: {context.workflow_result}"
    
    # Get articles from database
    articles = db_manager.get_articles(context.query_id)
    assert len(articles) > 0, f"No articles saved to database for query_id: {context.query_id}, but workflow says {context.workflow_result['article_count']} were found"
    context.retrieved_articles = articles


@then('the articles should be analyzed by the LLM')
def step_verify_llm_analysis(context):
    """Verify LLM analysis is performed."""
    assert context.workflow_result is not None, "No workflow result"
    assert "summary" in context.workflow_result, "No summary in result"
    assert context.workflow_result["summary"], "Empty summary"
    assert len(context.workflow_result["summary"]) > 50, "Summary too short"


@then('I should receive a summarized response within {seconds:d} seconds')
def step_verify_response_time(context, seconds: int):
    """Verify response is received within time limit."""
    elapsed_time = time.time() - context.workflow_start_time
    assert elapsed_time < seconds, f"Response took {elapsed_time:.1f}s, expected < {seconds}s"
    
    # Also check the recorded processing time
    assert "processing_time" in context.workflow_result
    assert context.workflow_result["processing_time"] < seconds


@given('I specify filters for open-access articles only')
def step_add_open_access_filter(context):
    """Add open-access filter."""
    if not hasattr(context, 'query_filters'):
        context.query_filters = {}
    context.query_filters['open_access'] = True


@given('I limit results to publications from {year:d} onwards')
def step_add_date_filter(context, year: int):
    """Add publication date filter."""
    if not hasattr(context, 'query_filters'):
        context.query_filters = {}
    context.query_filters['min_year'] = year


@when('I submit the filtered query to the workflow')
def step_submit_filtered_query(context):
    """Submit query with filters."""
    raise NotImplementedError("Filtered query submission not yet implemented")


@then('only open-access articles should be retrieved')
def step_verify_open_access_only(context):
    """Verify only open-access articles."""
    raise NotImplementedError("Open-access filter verification not yet implemented")


@then('all articles should have publication dates from {year:d} or later')
def step_verify_publication_dates(context, year: int):
    """Verify publication date filtering."""
    raise NotImplementedError("Publication date verification not yet implemented")


@then('the filtered results should be analyzed appropriately')
def step_verify_filtered_analysis(context):
    """Verify filtered results are analyzed."""
    raise NotImplementedError("Filtered analysis verification not yet implemented")


@given('I have processed a query about "{topic}"')
def step_process_initial_query(context, topic: str):
    """Process an initial query."""
    context.initial_query = topic
    context.conversation_context = []
    raise NotImplementedError("Initial query processing not yet implemented")


@given('I received an initial analysis response')
def step_receive_initial_response(context):
    """Receive initial analysis response."""
    raise NotImplementedError("Initial response reception not yet implemented")


@when('I ask a follow-up question "{question}"')
def step_ask_followup_question(context, question: str):
    """Ask a follow-up question."""
    context.followup_question = question
    raise NotImplementedError("Follow-up question handling not yet implemented")


@then('the system should maintain context from the previous query')
def step_verify_context_maintained(context):
    """Verify context is maintained."""
    raise NotImplementedError("Context maintenance verification not yet implemented")


@then('the follow-up response should reference the initial results')
def step_verify_followup_references(context):
    """Verify follow-up references initial results."""
    raise NotImplementedError("Follow-up reference verification not yet implemented")


@then('the analysis should be specific to the follow-up question')
def step_verify_followup_specificity(context):
    """Verify follow-up is specific."""
    raise NotImplementedError("Follow-up specificity verification not yet implemented")


@given('I have {count:d} different medical research queries')
def step_create_multiple_queries(context, count: int):
    """Create multiple queries."""
    context.multiple_queries = [
        "Latest Alzheimer's treatment research",
        "mRNA vaccine technology advancements",
        "CRISPR gene therapy clinical trials"
    ][:count]


@when('I submit all queries simultaneously')
def step_submit_queries_simultaneously(context):
    """Submit all queries at once."""
    context.submission_timestamp = time.time()
    raise NotImplementedError("Simultaneous query submission not yet implemented")


@then('each query should be processed in parallel')
def step_verify_parallel_processing(context):
    """Verify parallel processing."""
    raise NotImplementedError("Parallel processing verification not yet implemented")


@then('no query should block the others')
def step_verify_no_blocking(context):
    """Verify queries don't block each other."""
    raise NotImplementedError("Non-blocking verification not yet implemented")


@then('all results should be returned independently')
def step_verify_independent_results(context):
    """Verify results are independent."""
    raise NotImplementedError("Independent results verification not yet implemented")


@then('the total processing time should be less than single sequential processing')
def step_verify_parallel_speedup(context):
    """Verify parallel processing is faster."""
    raise NotImplementedError("Parallel speedup verification not yet implemented")


@given('I have a query that will partially fail')
def step_create_failing_query(context):
    """Create a query that will partially fail."""
    context.failing_query = "Test query for partial failure scenario"
    context.force_llm_failure = True


@when('the PubMed retrieval succeeds but LLM analysis fails')
def step_trigger_partial_failure(context):
    """Trigger partial failure scenario."""
    raise NotImplementedError("Partial failure triggering not yet implemented")


@then('I should receive the raw PubMed results')
def step_verify_raw_results_received(context):
    """Verify raw PubMed results are received."""
    raise NotImplementedError("Raw results verification not yet implemented")


@then('an error message about the analysis failure')
def step_verify_analysis_error_message(context):
    """Verify analysis error message."""
    raise NotImplementedError("Analysis error message verification not yet implemented")


@then('the option to retry the analysis step')
def step_verify_retry_option(context):
    """Verify retry option is available."""
    raise NotImplementedError("Retry option verification not yet implemented")


@then('the failure should not crash the entire workflow')
def step_verify_workflow_stability(context):
    """Verify workflow doesn't crash."""
    raise NotImplementedError("Workflow stability verification not yet implemented")