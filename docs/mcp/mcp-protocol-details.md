# Model Context Protocol (MCP) Technical Details

## Protocol Overview

The Model Context Protocol (MCP) is a standardized communication protocol that enables Large Language Models to interact with external services through well-defined interfaces. For the Medical Research Agent, MCP provides the critical bridge between AI capabilities and PubMed's vast biomedical database.

## Core Concepts

### 1. Transport Layer

MCP supports multiple transport mechanisms:

**STDIO (Standard Input/Output)**:
```json
{
  "mcpServers": {
    "pubmed": {
      "command": "python",
      "args": ["-m", "pubmed_mcp_server"],
      "transport": "stdio"
    }
  }
}
```

**HTTP Transport**:
```json
{
  "mcpServers": {
    "pubmed": {
      "url": "http://localhost:8080/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

### 2. Message Format

MCP uses JSON-RPC 2.0 for message exchange:

**Request Structure**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_pubmed_articles",
    "arguments": {
      "query": "COVID-19 vaccines",
      "maxResults": 50,
      "filters": {
        "publicationDateStart": "2023-01-01",
        "openAccess": true
      }
    }
  },
  "id": "request-123"
}
```

**Response Structure**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 50 articles matching your query..."
      },
      {
        "type": "resource",
        "resource": {
          "uri": "pubmed://articles/batch/123",
          "mimeType": "application/json",
          "data": {
            "articles": [...]
          }
        }
      }
    ]
  },
  "id": "request-123"
}
```

### 3. Tool Definitions

MCP servers expose tools with structured schemas:

```typescript
interface Tool {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, any>;
    required?: string[];
  };
}

// Example: PubMed search tool
const searchTool: Tool = {
  name: "search_pubmed_articles",
  description: "Search PubMed for biomedical literature",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query using PubMed syntax"
      },
      maxResults: {
        type: "number",
        description: "Maximum number of results (1-10000)",
        minimum: 1,
        maximum: 10000
      },
      filters: {
        type: "object",
        properties: {
          publicationDateStart: {
            type: "string",
            format: "date"
          },
          publicationDateEnd: {
            type: "string",
            format: "date"
          },
          openAccess: {
            type: "boolean"
          },
          publicationTypes: {
            type: "array",
            items: {
              type: "string",
              enum: ["Clinical Trial", "Review", "Meta-Analysis"]
            }
          }
        }
      }
    },
    required: ["query"]
  }
};
```

## PubMed MCP Implementation

### 1. Server Initialization

```typescript
import { Server } from '@modelcontextprotocol/sdk/server';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio';

class PubMedMCPServer {
  private server: Server;
  private ncbiApiKey?: string;

  constructor() {
    this.server = new Server(
      {
        name: 'pubmed-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    this.setupTools();
    this.setupResources();
  }

  private setupTools() {
    this.server.setRequestHandler('tools/list', async () => ({
      tools: [
        searchPubMedTool,
        fetchArticleContentTool,
        getArticleConnectionsTool,
        generateResearchPlanTool
      ]
    }));

    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;
      
      switch (name) {
        case 'search_pubmed_articles':
          return await this.searchPubMed(args);
        case 'fetch_article_content':
          return await this.fetchArticle(args);
        // ... other tool handlers
      }
    });
  }
}
```

### 2. E-utilities Integration

```typescript
class PubMedClient {
  private baseUrl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';
  private apiKey?: string;
  private rateLimiter: RateLimiter;

  constructor(apiKey?: string) {
    this.apiKey = apiKey;
    // 10 req/sec with key, 3 req/sec without
    const rateLimit = apiKey ? 10 : 3;
    this.rateLimiter = new RateLimiter(rateLimit);
  }

  async search(query: string, options: SearchOptions): Promise<SearchResult> {
    await this.rateLimiter.acquire();

    const params = new URLSearchParams({
      db: 'pubmed',
      term: this.formatQuery(query, options.filters),
      retmax: options.maxResults.toString(),
      retmode: 'json',
      ...(this.apiKey && { api_key: this.apiKey })
    });

    const response = await fetch(
      `${this.baseUrl}/esearch.fcgi?${params}`
    );

    if (response.status === 429) {
      throw new RateLimitError('E-utilities rate limit exceeded');
    }

    const data = await response.json();
    return this.parseSearchResults(data);
  }

  private formatQuery(query: string, filters?: FilterOptions): string {
    let formattedQuery = query;

    if (filters?.publicationDateStart) {
      const dateFilter = `("${filters.publicationDateStart}"[Date - Publication] : "3000"[Date - Publication])`;
      formattedQuery = `(${formattedQuery}) AND ${dateFilter}`;
    }

    if (filters?.openAccess) {
      formattedQuery = `(${formattedQuery}) AND "open access"[filter]`;
    }

    return formattedQuery;
  }
}
```

### 3. Resource Management

MCP supports resource URIs for efficient data handling:

```typescript
class ResourceManager {
  private cache = new Map<string, Resource>();

  async createBatchResource(articles: Article[]): Promise<string> {
    const resourceId = generateUUID();
    const resourceUri = `pubmed://articles/batch/${resourceId}`;

    const resource: Resource = {
      uri: resourceUri,
      name: `Article batch (${articles.length} items)`,
      description: `Batch of ${articles.length} PubMed articles`,
      mimeType: 'application/json',
      data: articles
    };

    this.cache.set(resourceUri, resource);
    
    // Set expiration
    setTimeout(() => {
      this.cache.delete(resourceUri);
    }, 3600000); // 1 hour

    return resourceUri;
  }

  async getResource(uri: string): Promise<Resource | null> {
    return this.cache.get(uri) || null;
  }
}
```

## Advanced Features

### 1. Streaming Responses

For large result sets, MCP supports streaming:

```typescript
async function* streamSearchResults(query: string): AsyncGenerator<PartialResult> {
  let offset = 0;
  const batchSize = 100;

  while (true) {
    const batch = await searchBatch(query, offset, batchSize);
    
    yield {
      articles: batch.articles,
      progress: batch.totalCount > 0 ? (offset + batch.articles.length) / batch.totalCount : 1,
      isComplete: false
    };

    if (batch.articles.length < batchSize) {
      yield { isComplete: true };
      break;
    }

    offset += batchSize;
  }
}
```

### 2. Context Preservation

MCP servers can maintain context across requests:

```typescript
class SessionManager {
  private sessions = new Map<string, SessionContext>();

  createSession(userId: string): string {
    const sessionId = generateUUID();
    this.sessions.set(sessionId, {
      userId,
      queries: [],
      articles: [],
      createdAt: new Date()
    });
    return sessionId;
  }

  addToContext(sessionId: string, query: string, results: Article[]) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.queries.push(query);
      session.articles.push(...results);
    }
  }

  getContext(sessionId: string): SessionContext | null {
    return this.sessions.get(sessionId) || null;
  }
}
```

### 3. Error Handling

Structured error responses in MCP:

```typescript
class MCPError extends Error {
  code: string;
  details?: any;

  constructor(message: string, code: string, details?: any) {
    super(message);
    this.code = code;
    this.details = details;
  }

  toJSON() {
    return {
      error: {
        code: this.code,
        message: this.message,
        data: this.details
      }
    };
  }
}

// Usage
if (!ncbiApiKey) {
  throw new MCPError(
    'NCBI API key required for this operation',
    'AUTH_REQUIRED',
    { requiredScope: 'ncbi.pubmed.read' }
  );
}
```

## Security Considerations

### 1. Authentication

```typescript
interface AuthConfig {
  type: 'bearer' | 'api-key' | 'oauth2';
  credentials: string;
  scope?: string[];
}

class AuthManager {
  async validateRequest(headers: Headers): Promise<boolean> {
    const authHeader = headers.get('Authorization');
    if (!authHeader) return false;

    if (authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      return await this.validateBearerToken(token);
    }

    return false;
  }
}
```

### 2. Rate Limiting

```typescript
class RateLimiter {
  private queue: Array<() => void> = [];
  private running = 0;
  private lastRequest = 0;

  constructor(private maxPerSecond: number) {}

  async acquire(): Promise<void> {
    return new Promise((resolve) => {
      this.queue.push(resolve);
      this.process();
    });
  }

  private process() {
    if (this.queue.length === 0 || this.running >= this.maxPerSecond) {
      return;
    }

    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;
    const minInterval = 1000 / this.maxPerSecond;

    if (timeSinceLastRequest < minInterval) {
      setTimeout(() => this.process(), minInterval - timeSinceLastRequest);
      return;
    }

    const resolve = this.queue.shift()!;
    this.running++;
    this.lastRequest = now;

    resolve();

    setTimeout(() => {
      this.running--;
      this.process();
    }, 1000);
  }
}
```

## Integration Patterns

### 1. Direct Integration

```python
from mcp import Client

async def query_pubmed(query: str):
    async with Client("pubmed://localhost:8080") as client:
        result = await client.call_tool(
            "search_pubmed_articles",
            {
                "query": query,
                "maxResults": 100
            }
        )
        return result
```

### 2. Through Prefect

```python
from prefect import task, flow
from mcp import Client

@task
async def search_via_mcp(query: str, filters: dict):
    async with Client("pubmed://localhost:8080") as client:
        return await client.call_tool(
            "search_pubmed_articles",
            {"query": query, "filters": filters}
        )

@flow
async def research_workflow(query: str):
    # MCP handles all PubMed interaction
    articles = await search_via_mcp(query, {"openAccess": True})
    return articles
```

## Performance Optimization

### 1. Connection Pooling

```typescript
class MCPConnectionPool {
  private connections: Connection[] = [];
  private available: Connection[] = [];

  async getConnection(): Promise<Connection> {
    if (this.available.length > 0) {
      return this.available.pop()!;
    }

    if (this.connections.length < this.maxConnections) {
      const conn = await this.createConnection();
      this.connections.push(conn);
      return conn;
    }

    // Wait for available connection
    return await this.waitForConnection();
  }

  releaseConnection(conn: Connection) {
    this.available.push(conn);
  }
}
```

### 2. Caching Strategy

```typescript
class MCPCache {
  private cache = new LRUCache<string, CachedResult>({
    max: 1000,
    ttl: 1000 * 60 * 60 // 1 hour
  });

  getCacheKey(method: string, params: any): string {
    return `${method}:${JSON.stringify(params)}`;
  }

  async get(method: string, params: any): Promise<any | null> {
    const key = this.getCacheKey(method, params);
    return this.cache.get(key);
  }

  set(method: string, params: any, result: any) {
    const key = this.getCacheKey(method, params);
    this.cache.set(key, result);
  }
}
```

## Monitoring & Debugging

### 1. Request Logging

```typescript
interface MCPLogEntry {
  timestamp: Date;
  method: string;
  params: any;
  duration: number;
  status: 'success' | 'error';
  error?: string;
}

class MCPLogger {
  log(entry: MCPLogEntry) {
    console.log(JSON.stringify({
      ...entry,
      timestamp: entry.timestamp.toISOString()
    }));
  }
}
```

### 2. Metrics Collection

```typescript
class MCPMetrics {
  private metrics = {
    requests: new Counter('mcp_requests_total'),
    errors: new Counter('mcp_errors_total'),
    duration: new Histogram('mcp_request_duration_seconds')
  };

  recordRequest(method: string, duration: number, status: string) {
    this.metrics.requests.inc({ method, status });
    this.metrics.duration.observe({ method }, duration / 1000);
    
    if (status === 'error') {
      this.metrics.errors.inc({ method });
    }
  }
}
```

This comprehensive technical documentation provides the detailed information needed to understand and implement MCP integration for the Medical Research Agent project.