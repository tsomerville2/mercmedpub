Feature: Medical Research Query Processing Workflow
  As a medical research agent user
  I want to process natural language queries through the Prefect workflow
  So that I can get analyzed medical research results quickly and accurately

  Background:
    Given the Prefect workflow is configured
    And the MCP PubMed server is accessible
    And an LLM API is configured for analysis

  @critical @workflow
  Scenario: Process a simple medical research query
    Given I have a query "What are the latest treatments for Type 2 Diabetes?"
    When I submit the query to the Prefect workflow
    Then the query should be parsed into PubMed search parameters
    And relevant articles should be retrieved from PubMed
    And the articles should be analyzed by the LLM
    And I should receive a summarized response within 10 seconds

  @critical @workflow @filtering
  Scenario: Apply filters to medical research query
    Given I have a query "COVID-19 vaccine side effects in children"
    And I specify filters for open-access articles only
    And I limit results to publications from 2021 onwards
    When I submit the filtered query to the workflow
    Then only open-access articles should be retrieved
    And all articles should have publication dates from 2021 or later
    And the filtered results should be analyzed appropriately

  @workflow @interactive
  Scenario: Handle follow-up queries with context
    Given I have processed a query about "breast cancer immunotherapy"
    And I received an initial analysis response
    When I ask a follow-up question "What are the success rates?"
    Then the system should maintain context from the previous query
    And the follow-up response should reference the initial results
    And the analysis should be specific to the follow-up question

  @workflow @parallel
  Scenario: Process multiple queries in parallel
    Given I have 3 different medical research queries
    When I submit all queries simultaneously
    Then each query should be processed in parallel
    And no query should block the others
    And all results should be returned independently
    And the total processing time should be less than single sequential processing

  @workflow @error-handling
  Scenario: Handle partial failures gracefully
    Given I have a query that will partially fail
    When the PubMed retrieval succeeds but LLM analysis fails
    Then I should receive the raw PubMed results
    And an error message about the analysis failure
    And the option to retry the analysis step
    And the failure should not crash the entire workflow