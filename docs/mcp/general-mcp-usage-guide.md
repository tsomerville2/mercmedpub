# General Model Context Protocol (MCP) Usage Guide

## What is MCP?

The Model Context Protocol (MCP) is an open standard introduced by Anthropic that enables developers to build secure, two-way connections between AI systems and external data sources/tools. Think of it as "USB for AI" - a universal protocol that replaces fragmented integrations with a single standard.

## Core Concepts

### 1. MCP Architecture

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│  MCP Host   │◄────────│  MCP Client  │────────►│ MCP Server │
│  (Claude)   │         │              │         │  (Tools)   │
└─────────────┘         └──────────────┘         └────────────┘
```

### 2. Key Components

**MCP Servers Provide Three Main Capabilities:**

1. **Resources**: File-like data that can be read by clients
   - API responses
   - File contents
   - Database query results

2. **Tools**: Functions that can be called by the LLM (with user approval)
   - Execute commands
   - Make API calls
   - Perform calculations

3. **Prompts**: Pre-written templates for specific tasks
   - Common queries
   - Workflow templates
   - Best practices

### 3. Communication Flow

1. **Initialization**: Host creates MCP clients and performs handshake
2. **Discovery**: Clients request available capabilities
3. **Execution**: LLM calls tools/resources as needed
4. **Response**: Server returns results to client

## Setting Up MCP Servers

### Prerequisites

- **Python**: Version 3.10 or higher
- **Node.js**: Version 18 or higher (for TypeScript servers)
- **Package Manager**: `uv` for Python, `npm` for TypeScript

### Python MCP Server Setup

#### 1. Install UV Package Manager
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Create Project Structure
```bash
# Create project directory
uv init my-mcp-server
cd my-mcp-server

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install MCP SDK
uv add "mcp[cli]"
```

#### 3. Basic Server Implementation
```python
from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize server
mcp = FastMCP("my-server")

@mcp.tool()
def hello_world(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

@mcp.resource("greeting://hello")
def get_greeting() -> str:
    """Get a greeting resource"""
    return "Welcome to MCP!"

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### TypeScript MCP Server Setup

#### 1. Initialize Project
```bash
mkdir my-mcp-server-ts
cd my-mcp-server-ts
npm init -y
npm install @modelcontextprotocol/sdk
npm install -D typescript @types/node tsx
```

#### 2. Create Server
```typescript
import { Server } from '@modelcontextprotocol/sdk/server';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio';

const server = new Server({
  name: 'my-server',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
    resources: {},
  },
});

// Add a tool
server.setRequestHandler('tools/list', async () => ({
  tools: [{
    name: 'hello_world',
    description: 'Say hello to someone',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string' }
      },
      required: ['name']
    }
  }]
}));

// Handle tool calls
server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'hello_world') {
    return {
      content: [{
        type: 'text',
        text: `Hello, ${request.params.arguments.name}!`
      }]
    };
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Claude Desktop Configuration

### Config File Location
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Basic Configuration Structure
```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["argument1", "argument2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Configuration Examples

#### Python Server
```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/my-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

#### TypeScript Server
```json
{
  "mcpServers": {
    "my-ts-server": {
      "command": "node",
      "args": ["/path/to/my-server/dist/index.js"]
    }
  }
}
```

#### Using NPX
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Documents"
      ]
    }
  }
}
```

#### Multiple Servers
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:pass@localhost/db"
      ]
    }
  }
}
```

## Available Pre-built MCP Servers

### Official Servers
1. **Filesystem** - File system access
   ```bash
   npx -y @modelcontextprotocol/server-filesystem /path/to/directory
   ```

2. **GitHub** - GitHub repository access
   ```bash
   npx -y @modelcontextprotocol/server-github
   ```

3. **PostgreSQL** - Database access
   ```bash
   npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
   ```

4. **Slack** - Slack workspace integration
   ```bash
   npx -y @modelcontextprotocol/server-slack
   ```

5. **Google Drive** - Google Drive access
   ```bash
   npx -y @modelcontextprotocol/server-gdrive
   ```

### Community Servers
- **Brave Search** - Web search
- **SQLite** - SQLite database access
- **Puppeteer** - Browser automation
- **Sequential Thinking** - Chain of thought tools
- **PubMed** - Medical literature search

## Best Practices

### 1. Error Handling
```python
@mcp.tool()
def safe_operation(param: str) -> str:
    try:
        # Perform operation
        result = perform_operation(param)
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### 2. Input Validation
```python
@mcp.tool()
def validated_tool(number: int) -> str:
    if number < 0:
        raise ValueError("Number must be non-negative")
    return f"Valid number: {number}"
```

### 3. Resource Management
```python
@mcp.resource("data://item/{item_id}")
def get_item(item_id: str) -> dict:
    # Validate item_id format
    if not item_id.isalnum():
        raise ValueError("Invalid item ID")
    
    # Fetch and return item
    return fetch_item_from_database(item_id)
```

### 4. Logging
```python
import logging

logger = logging.getLogger(__name__)

@mcp.tool()
def logged_operation(param: str) -> str:
    logger.info(f"Starting operation with param: {param}")
    result = perform_operation(param)
    logger.info(f"Operation completed: {result}")
    return result
```

## Debugging MCP Servers

### 1. Check Claude Logs
```bash
# macOS
tail -n 50 -f ~/Library/Logs/Claude/mcp*.log

# Windows
Get-Content "$env:APPDATA\Claude\logs\mcp*.log" -Tail 50 -Wait
```

### 2. Test Server Standalone
```bash
# Python
python server.py

# TypeScript
node dist/index.js
```

### 3. Common Issues

**Server Not Appearing in Claude:**
- Verify config file syntax (valid JSON)
- Check file paths are absolute
- Ensure server executable permissions
- Restart Claude completely

**Connection Errors:**
- Check server is not already running
- Verify no port conflicts
- Review server logs for errors
- Test with simple "hello world" server

**Tool Not Working:**
- Verify tool registration
- Check input schema matches
- Review error responses
- Test tool function standalone

## Advanced Features

### 1. Streaming Responses
```python
@mcp.tool()
async def stream_data() -> AsyncGenerator[str, None]:
    for i in range(10):
        yield f"Data chunk {i}\n"
        await asyncio.sleep(1)
```

### 2. Context Management
```python
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now()
        }
        return session_id
```

### 3. Custom Prompts
```python
@mcp.prompt()
def analysis_prompt(topic: str) -> str:
    return f"""
    Analyze the following topic in detail:
    Topic: {topic}
    
    Please provide:
    1. Overview
    2. Key points
    3. Implications
    4. Recommendations
    """
```

## Security Considerations

### 1. Authentication
```python
def validate_api_key(api_key: str) -> bool:
    return api_key == os.getenv('VALID_API_KEY')

@mcp.tool()
def secure_operation(api_key: str, data: str) -> str:
    if not validate_api_key(api_key):
        raise PermissionError("Invalid API key")
    return process_data(data)
```

### 2. Input Sanitization
```python
import re

def sanitize_input(text: str) -> str:
    # Remove potentially dangerous characters
    return re.sub(r'[<>&\"\'`]', '', text)
```

### 3. Rate Limiting
```python
from functools import wraps
import time

def rate_limit(calls_per_minute: int):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@mcp.tool()
@rate_limit(30)  # 30 calls per minute
def limited_operation() -> str:
    return "Operation completed"
```

## Resources

- [Official MCP Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol/servers)
- [Claude Desktop MCP Docs](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [MCP Community Servers](https://github.com/modelcontextprotocol/servers)
- [MCP SDK Documentation](https://modelcontextprotocol.io/reference)

## Conclusion

MCP provides a powerful, standardized way to extend AI capabilities with external tools and data sources. By following this guide, you can create custom MCP servers that integrate seamlessly with Claude and other MCP-compatible systems, enabling sophisticated AI-powered workflows and applications.