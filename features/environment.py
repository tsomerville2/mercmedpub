"""
BDD Environment Setup for Medical Research Agent

This module sets up the test environment, fixtures, and hooks for BDD testing.
"""

import os
import logging
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv


def before_all(context):
    """Set up test environment before all tests."""
    # Load environment variables from .env file if exists
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    context.logger = logging.getLogger('medical_research_agent_bdd')
    
    # Set up configuration
    context.config = {
        'mcp_pubmed_endpoint': os.getenv('MCP_PUBMED_ENDPOINT', 'http://localhost:8080'),
        'api_base_url': os.getenv('API_BASE_URL', 'http://localhost:8000'),
        'prefect_api_url': os.getenv('PREFECT_API_URL', 'http://localhost:4200'),
        'ncbi_api_key': os.getenv('NCBI_API_KEY', ''),
        'ncbi_email': os.getenv('NCBI_EMAIL', 'test@example.com'),
        'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
        'llm_api_key': os.getenv('LLM_API_KEY', ''),
        'test_api_key': os.getenv('TEST_API_KEY', 'test-api-key'),
        'test_timeout': int(os.getenv('TEST_TIMEOUT', '30'))
    }
    
    # Initialize shared resources
    context.shared_resources = {}
    context.test_data = {}
    
    context.logger.info("BDD test environment initialized")


def before_feature(context, feature):
    """Set up before each feature."""
    context.logger.info(f"Starting feature: {feature.name}")
    context.feature_data = {}
    
    # Feature-specific setup based on tags
    if 'mcp' in feature.tags:
        setup_mcp_environment(context)
    
    if 'api' in feature.tags:
        setup_api_environment(context)
    
    if 'workflow' in feature.tags:
        setup_workflow_environment(context)


def before_scenario(context, scenario):
    """Set up before each scenario."""
    context.logger.info(f"Starting scenario: {scenario.name}")
    context.scenario_data = {}
    
    # Scenario-specific setup based on tags
    if 'rate-limit' in scenario.tags:
        context.enforce_rate_limits = True
    
    if 'parallel' in scenario.tags:
        context.parallel_execution = True
    
    if 'error-handling' in scenario.tags:
        context.test_error_scenarios = True


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    context.logger.info(f"Completed scenario: {scenario.name} - Status: {scenario.status}")
    
    # Clean up scenario-specific resources
    if hasattr(context, 'api_session') and context.api_session:
        context.api_session.close()
    
    if hasattr(context, 'mcp_client') and context.mcp_client:
        # Close MCP client connection
        pass
    
    # Clear scenario data
    context.scenario_data = {}


def after_feature(context, feature):
    """Clean up after each feature."""
    context.logger.info(f"Completed feature: {feature.name}")
    
    # Clean up feature-specific resources
    context.feature_data = {}


def after_all(context):
    """Clean up after all tests."""
    context.logger.info("BDD test suite completed")
    
    # Clean up any remaining resources
    if hasattr(context, 'shared_resources'):
        for resource_name, resource in context.shared_resources.items():
            context.logger.info(f"Cleaning up resource: {resource_name}")
            # Implement resource-specific cleanup
    
    # API server thread will be terminated as daemon thread


# Helper functions for environment setup

def setup_mcp_environment(context):
    """Set up MCP-specific test environment."""
    context.logger.info("Setting up MCP test environment")
    
    # Initialize MCP test data
    context.mcp_test_data = {
        'test_queries': [
            "COVID-19 vaccine efficacy",
            "CRISPR gene therapy",
            "Alzheimer's treatment"
        ],
        'expected_fields': ['title', 'authors', 'abstract', 'pmid', 'publication_date']
    }
    
    # Set rate limit configuration
    if context.config['ncbi_api_key']:
        context.rate_limit = 10  # With API key
    else:
        context.rate_limit = 3   # Without API key
        context.logger.warning("No NCBI API key found - rate limited to 3 req/sec")


def setup_api_environment(context):
    """Set up API-specific test environment."""
    context.logger.info("Setting up API test environment")
    
    # Initialize API test data
    context.api_test_data = {
        'valid_payload': {
            "query": "Test medical research query",
            "filters": {
                "publication_date_start": "2020-01-01",
                "open_access": True
            }
        },
        'invalid_payload': {
            "query": "",  # Empty query
            "filters": {
                "invalid_field": "value"
            }
        }
    }
    
    # Set default headers
    context.default_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


def setup_workflow_environment(context):
    """Set up workflow-specific test environment."""
    context.logger.info("Setting up workflow test environment")
    
    # Initialize workflow test data
    context.workflow_test_data = {
        'test_queries': [
            "Latest Alzheimer's treatment research",
            "mRNA vaccine technology advancements",
            "CRISPR gene therapy clinical trials"
        ],
        'expected_workflow_states': [
            'pending',
            'running',
            'completed',
            'failed'
        ]
    }
    
    # Set workflow timeouts
    context.workflow_timeouts = {
        'query_processing': 10,  # seconds
        'parallel_processing': 15,  # seconds
        'async_polling_interval': 1  # seconds
    }