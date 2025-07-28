SOW  Development of Medical Research Agent Using Prefect Framework
Goal
The goal is to build a Medical Research Agent that delivers pinpoint-accurate, real-time article queries from PubMed’s massive database, using the MCP protocol to create personalized news feeds for Coach users based on their personal health metrics and biology. Accuracy is the top priority—ensuring the agent confidently pulls all relevant articles for a query, with results ideally delivered in about five seconds. Developers should leverage Prefect’s existing framework, focusing on its orchestration capabilities to manage agents effectively. You, as the user, need full admin access to the Prefect Cloud dashboard to directly edit the system prompt via a simple chat box interface (like ChatGPT’s) and input queries in a separate box. No new tools need to be built—use existing ones like Langraph, Grafana, or Prometheus for monitoring. Doc’s key tasks will be tweaking the system prompt to optimize accuracy and analyzing performance metrics to ensure the agent nails query result
Project Overview
This SOW outlines the development of a modular medical research agent built within the Prefect orchestration framework. The agent will leverage the PubMed MCP Server from the MCPmed GitHub repository (https://github.com/MCPmed, associated with MCPmed: A Call for MCP-Enabled Bioinformatics Web Services for LLM-Driven Discovery https://arxiv.org/html/2507.08055v1 to query PubMed's API for biomedical literature. The agent will process natural-language user queries, retrieve and filter relevant data, analyze it via a frontier LLM (e.g., Claude or GPT models), and support interactive follow-up queries. The design will emphasize modularity, speed optimization through parallelism (e.g., using Prefect's concurrent tasks and Dask integration where applicable), and an API interface for integration with other applications. The development team, based in India and familiar with Python, APIs, and data orchestration, will deliver a production-ready solution at an hourly rate of $30 USD.
Scope of Work
The project includes the following key activities:
Setup and integration of the PubMed MCP Server to interface with PubMed's API via NCBI E-Utilities.
Development of a Prefect flow that handles end-to-end query processing: input parsing, data retrieval, filtering, LLM analysis, and interactive querying.
Optimization for speed, including parallel execution of API calls, data processing, and LLM interactions where feasible (e.g., batching queries or using asynchronous Prefect tasks).
Implementation of modularity: separate modules for query handling, data retrieval, filtering, LLM integration, and response generation.
Creation of a RESTful API or callable interface (e.g., via FastAPI) for external applications to invoke the agent.
Testing for compliance with NCBI rate limits (e.g., 3 requests/second without API key, 10 with key) and error handling.
Documentation and basic deployment guidance (e.g., Docker containerization).
Out-of-scope items include: hosting the solution, providing LLM API keys, or integrating with non-specified databases.
Deliverables
Prefect Flow Setup: A fully configured Prefect workflow (e.g., as a Python script or module) orchestrating the agent's pipeline, with tasks for query input, MCP server interaction, data filtering, LLM analysis, and output.
MCP Server Integration: Code to deploy and use the PubMed MCP Server (based on MCPmed templates or existing implementations like https://github.com/cyanheads/pubmed-mcp-server), including setup scripts for local or containerized deployment.
Modular Agent Components: 
Query Parser: Accepts natural-language input and converts to PubMed search parameters.
Data Retriever: Queries PubMed via MCP, retrieves metadata/full-text links, and applies filters (e.g., publication date > 2020, open-access only).
LLM Analyzer: Integrates with a frontier LLM API for summarization and analysis; supports interactive follow-ups via stateful sessions.
Response Handler: Formats outputs for user or API consumption.
API/Interface: A FastAPI-based endpoint (e.g., POST /query with JSON payload) for invoking the agent, including authentication if needed.
Documentation: 
API specs (e.g., OpenAPI/Swagger docs).
User guide for running the Prefect flow and MCP server.
Code comments and setup instructions.
Testing Artifacts: Unit/integration tests, sample queries, and performance benchmarks demonstrating parallelism (e.g., reduced latency via concurrent tasks).
All code will be delivered via a private GitHub repository, with MIT licensing unless specified otherwise.
