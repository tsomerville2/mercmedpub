Feature: Medical Research Agent API Interface
  As an external application developer
  I want to interact with the medical research agent via REST API
  So that I can integrate medical research capabilities into my application

  Background:
    Given the FastAPI server is running
    And authentication is configured
    And the medical research workflow is available

  @critical @api
  Scenario: Submit a research query via API
    Given I have a valid API key
    When I POST to "/api/query" with JSON payload:
      """
      {
        "query": "Recent advances in CAR-T cell therapy",
        "filters": {
          "publication_date_start": "2022-01-01",
          "open_access": true
        }
      }
      """
    Then I should receive a 200 OK response
    And the response should contain a query_id
    And the response should contain analyzed results
    And the response time should be under 10 seconds

  @api @authentication
  Scenario: Reject unauthorized API requests
    Given I have an invalid API key
    When I POST to "/api/query" with a research query
    Then I should receive a 401 Unauthorized response
    And the response should contain an authentication error message

  @api @validation
  Scenario: Validate API request payload
    Given I have a valid API key
    When I POST to "/api/query" with invalid JSON:
      """
      {
        "query": "",
        "filters": {
          "invalid_field": "value"
        }
      }
      """
    Then I should receive a 422 Unprocessable Entity response
    And the response should detail the validation errors

  @api @async
  Scenario: Handle asynchronous query processing
    Given I have a valid API key
    When I POST to "/api/query/async" with a complex research query
    Then I should receive a 202 Accepted response
    And the response should contain a task_id
    When I GET "/api/query/status/{task_id}"
    Then I should see the query processing status
    And eventually the status should be "completed"

  @api @batch
  Scenario: Submit batch queries via API
    Given I have a valid API key
    When I POST to "/api/query/batch" with multiple queries:
      """
      {
        "queries": [
          {"query": "COVID-19 long-term effects"},
          {"query": "Monoclonal antibody treatments"},
          {"query": "mRNA vaccine mechanisms"}
        ]
      }
      """
    Then I should receive a 200 OK response
    And the response should contain results for all queries
    And each result should have its own query_id

  @api @openapi
  Scenario: Access API documentation
    When I GET "/docs"
    Then I should receive the OpenAPI documentation
    And it should describe all available endpoints
    And it should include request/response schemas