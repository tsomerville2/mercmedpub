Feature: MCP PubMed Server Integration
  As a medical research agent
  I want to connect to the PubMed MCP server
  So that I can query biomedical literature from PubMed's database

  Background:
    Given the MCP PubMed server is configured with proper NCBI API credentials
    And the server respects NCBI rate limits

  @critical @mcp
  Scenario: Successfully connect to PubMed MCP server
    Given I have the MCP PubMed server endpoint configured
    When I initialize the MCP client connection
    Then the connection should be established successfully
    And I should be able to retrieve the server capabilities

  @critical @mcp
  Scenario: Query PubMed for recent medical research
    Given I have an active MCP PubMed server connection
    When I search for "COVID-19 vaccine efficacy" with publication date after 2020
    Then I should receive a list of relevant articles
    And each article should contain title, authors, and abstract
    And the results should be filtered by the date constraint

  @critical @mcp @rate-limit
  Scenario: Handle NCBI rate limiting gracefully
    Given I have an active MCP PubMed server connection
    When I make 5 rapid sequential queries without an API key
    Then the system should respect the 3 requests per second limit
    And no requests should fail due to rate limiting
    And appropriate delays should be introduced between requests

  @mcp @error-handling
  Scenario: Handle connection failures gracefully
    Given the MCP PubMed server is unavailable
    When I attempt to initialize the MCP client connection
    Then I should receive a meaningful error message
    And the system should suggest retry options
    And the failure should be logged for monitoring