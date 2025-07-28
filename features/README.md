# BDD Tests for Medical Research Agent

This directory contains Behavior-Driven Development (BDD) tests for the Medical Research Agent project using the Behave framework.

## Structure

```
features/
├── steps/              # Step definitions
│   ├── mcp_pubmed_steps.py
│   ├── workflow_steps.py
│   └── api_steps.py
├── support/            # Test helpers and data
│   ├── test_data.py
│   └── helpers.py
├── environment.py      # Test environment setup
├── mcp_pubmed_integration.feature
├── query_processing_workflow.feature
└── api_interface.feature
```

## Running Tests

### Run all tests
```bash
behave
```

### Run with detailed output
```bash
behave --format pretty --no-capture
```

### Run specific features
```bash
# MCP integration tests only
behave features/mcp_pubmed_integration.feature

# API tests only
behave features/api_interface.feature

# Workflow tests only
behave features/query_processing_workflow.feature
```

### Run tests by tags
```bash
# Critical tests only
behave --tags @critical

# MCP-related tests
behave --tags @mcp

# API tests
behave --tags @api

# Parallel execution tests
behave --tags @parallel
```

### Generate test reports
```bash
# JSON report
behave --format json.pretty --outfile reports/test_results.json

# JUnit XML report (for CI/CD)
behave --junit --junit-directory reports/junit
```

## Environment Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install behave python-dotenv
   ```

3. Configure your NCBI API key (required for PubMed access):
   - Get an API key from: https://www.ncbi.nlm.nih.gov/account/settings/
   - Add it to your `.env` file

## Test Implementation Status

All step definitions currently raise `NotImplementedError` following the BDD red-green-refactor cycle. As you implement the actual functionality:

1. Run tests to see failures
2. Implement the corresponding functionality
3. Update step definitions to test the real implementation
4. Run tests again to verify they pass

## Writing New Tests

1. Create a new `.feature` file in the `features/` directory
2. Write scenarios using Gherkin syntax
3. Run `behave --dry-run` to see undefined steps
4. Implement step definitions in appropriate files under `features/steps/`
5. Follow the existing patterns for consistency

## Common Commands

```bash
# Check for undefined steps
behave --dry-run

# Run with specific log level
behave --logging-level DEBUG

# Stop on first failure
behave --stop

# Run scenarios by name pattern
behave --name "Submit a research query"

# Generate step skeleton for undefined steps
behave --dry-run --no-skipped
```