# MCP in Claude Code Guide

## Overview

Claude Code has built-in support for Model Context Protocol (MCP) servers, allowing seamless integration with external tools and data sources. This guide covers MCP usage specifically within the Claude Code environment.

## MCP in Claude Code vs Claude Desktop

### Key Differences

1. **Configuration Location**:
   - Claude Code: `~/.claude/settings.json` or project-specific `.claude/settings.json`
   - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Server Management**:
   - Claude Code: Servers start/stop with each session
   - Claude Desktop: Servers persist across conversations

3. **Available Tools**:
   - Claude Code: Optimized for development workflows
   - Claude Desktop: General-purpose tools

## Claude Code MCP Configuration

### Settings File Structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "permissions": {
        "resources": true,
        "tools": true,
        "prompts": true
      }
    }
  },
  "permissions": {
    "tools": {
      "Read": true,
      "Write": true,
      "Edit": true,
      "Bash": true
    }
  }
}
```

### Project-Specific Configuration

Create `.claude/settings.json` in your project root:

```json
{
  "mcpServers": {
    "project-tools": {
      "type": "stdio",
      "command": "python",
      "args": ["tools/mcp_server.py"],
      "permissions": {
        "resources": true,
        "tools": true
      }
    }
  }
}
```

## Common MCP Servers for Development

### 1. Filesystem Server
```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "."
      ]
    }
  }
}
```

### 2. Git Server
```json
{
  "mcpServers": {
    "git": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ]
    }
  }
}
```

### 3. Database Servers

**SQLite**:
```json
{
  "mcpServers": {
    "sqlite": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "mcp-server-sqlite",
        "--db-path",
        "./database.db"
      ]
    }
  }
}
```

**PostgreSQL**:
```json
{
  "mcpServers": {
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
      ],
      "env": {
        "PGUSER": "username",
        "PGPASSWORD": "password"
      }
    }
  }
}
```

### 4. Development Tools

**Sequential Thinking**:
```json
{
  "mcpServers": {
    "thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-sequentialthinking-tools"]
    }
  }
}
```

**Web Search**:
```json
{
  "mcpServers": {
    "search": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-omnisearch"],
      "env": {
        "BRAVE_API_KEY": "your-key"
      }
    }
  }
}
```

## Creating Custom MCP Servers for Claude Code

### Python Example

```python
#!/usr/bin/env python3
"""Custom MCP server for project-specific tools"""

from mcp.server.fastmcp import FastMCP
import subprocess
import json

# Initialize server
mcp = FastMCP("project-tools")

@mcp.tool()
def run_tests(test_file: str = "") -> str:
    """Run project tests"""
    cmd = ["python", "-m", "pytest"]
    if test_file:
        cmd.append(test_file)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"Exit code: {result.returncode}\n\nOutput:\n{result.stdout}\n\nErrors:\n{result.stderr}"

@mcp.tool()
def format_code(file_path: str) -> str:
    """Format Python code with black"""
    result = subprocess.run(
        ["black", file_path],
        capture_output=True,
        text=True
    )
    return f"Formatted {file_path}: {result.stdout}"

@mcp.tool()
def run_linter(file_path: str) -> str:
    """Run flake8 linter"""
    result = subprocess.run(
        ["flake8", file_path],
        capture_output=True,
        text=True
    )
    return result.stdout or "No linting issues found!"

@mcp.resource("project://info")
def get_project_info() -> dict:
    """Get project information"""
    with open("pyproject.toml", "r") as f:
        return {"content": f.read()}

if __name__ == "__main__":
    mcp.run()
```

### TypeScript Example

```typescript
import { Server } from '@modelcontextprotocol/sdk/server';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const server = new Server({
  name: 'project-tools',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
    resources: {},
  },
});

// Tool: Run npm scripts
server.setRequestHandler('tools/list', async () => ({
  tools: [{
    name: 'npm_script',
    description: 'Run npm script',
    inputSchema: {
      type: 'object',
      properties: {
        script: { 
          type: 'string',
          description: 'Script name from package.json'
        }
      },
      required: ['script']
    }
  }]
}));

server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'npm_script') {
    const { script } = request.params.arguments;
    try {
      const { stdout, stderr } = await execAsync(`npm run ${script}`);
      return {
        content: [{
          type: 'text',
          text: `Output:\n${stdout}\n\nErrors:\n${stderr}`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error: ${error.message}`
        }]
      };
    }
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## MCP Usage Patterns in Claude Code

### 1. Development Workflow Integration

```python
@mcp.tool()
def dev_workflow(action: str) -> str:
    """Execute development workflow steps"""
    workflows = {
        "test": "python -m pytest",
        "lint": "flake8 . && mypy .",
        "format": "black . && isort .",
        "build": "python setup.py build",
        "docs": "sphinx-build -b html docs docs/_build"
    }
    
    if action not in workflows:
        return f"Unknown action. Available: {', '.join(workflows.keys())}"
    
    result = subprocess.run(
        workflows[action].split(),
        capture_output=True,
        text=True
    )
    return f"{action} completed:\n{result.stdout}"
```

### 2. Code Analysis Tools

```python
@mcp.tool()
def analyze_complexity(file_path: str) -> str:
    """Analyze code complexity"""
    result = subprocess.run(
        ["radon", "cc", file_path, "-s"],
        capture_output=True,
        text=True
    )
    return result.stdout

@mcp.tool()
def find_todos() -> str:
    """Find all TODO comments in the project"""
    result = subprocess.run(
        ["grep", "-r", "TODO", ".", "--include=*.py"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### 3. Project-Specific Resources

```python
@mcp.resource("project://readme")
def get_readme() -> dict:
    """Get project README"""
    with open("README.md", "r") as f:
        return {"content": f.read(), "mimeType": "text/markdown"}

@mcp.resource("project://dependencies")
def get_dependencies() -> dict:
    """Get project dependencies"""
    with open("requirements.txt", "r") as f:
        deps = f.read().splitlines()
    return {"dependencies": deps}
```

## Best Practices for Claude Code MCP

### 1. Session Management
- Servers restart with each Claude Code session
- Use stateless tools when possible
- Store state in files if persistence needed

### 2. Performance Optimization
- Minimize server startup time
- Use lightweight servers for common tasks
- Cache expensive operations

### 3. Error Handling
```python
@mcp.tool()
def safe_tool(param: str) -> str:
    """Tool with proper error handling"""
    try:
        # Validate input
        if not param:
            return "Error: Parameter required"
        
        # Perform operation
        result = perform_operation(param)
        
        # Return success
        return f"Success: {result}"
        
    except FileNotFoundError:
        return "Error: File not found"
    except PermissionError:
        return "Error: Permission denied"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

### 4. Security in Claude Code
- Never expose sensitive credentials in server code
- Use environment variables for secrets
- Validate all inputs
- Limit file system access scope

## Debugging MCP in Claude Code

### 1. Enable Verbose Logging
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 2. Test Server Independently
```bash
# Test Python server
python server.py

# Test TypeScript server
node dist/server.js

# Check for JSON-RPC responses
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python server.py
```

### 3. Common Issues and Solutions

**Server Not Available**:
- Check settings.json syntax
- Verify server file exists and is executable
- Look for startup errors in logs

**Tools Not Working**:
- Verify tool registration in server
- Check input parameter types match schema
- Test tool functions directly

**Performance Issues**:
- Profile server startup time
- Check for blocking operations
- Consider async implementations

## Advanced MCP Features in Claude Code

### 1. Dynamic Tool Registration
```python
def register_project_commands():
    """Dynamically register tools based on project structure"""
    if os.path.exists("Makefile"):
        @mcp.tool()
        def make(target: str) -> str:
            """Run make target"""
            result = subprocess.run(["make", target], capture_output=True, text=True)
            return result.stdout
    
    if os.path.exists("package.json"):
        @mcp.tool()
        def npm(command: str) -> str:
            """Run npm command"""
            result = subprocess.run(["npm", command], capture_output=True, text=True)
            return result.stdout
```

### 2. Context-Aware Tools
```python
@mcp.tool()
def smart_search(query: str) -> str:
    """Search project with context awareness"""
    # Detect project type
    if os.path.exists("requirements.txt"):
        file_pattern = "*.py"
    elif os.path.exists("package.json"):
        file_pattern = "*.js,*.ts"
    else:
        file_pattern = "*"
    
    # Perform search
    result = subprocess.run(
        ["rg", query, "--type-add", f"proj:{file_pattern}", "--type", "proj"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Integration with Claude Code Features

### 1. Complementing Built-in Tools
MCP servers should complement, not duplicate, Claude Code's built-in tools:
- Use MCP for project-specific operations
- Leverage built-in tools for file operations
- Combine both for powerful workflows

### 2. Workflow Example
```python
# Claude Code built-in tools handle file operations
# MCP server handles project-specific tasks

@mcp.tool()
def validate_changes() -> str:
    """Validate recent changes before commit"""
    checks = []
    
    # Run tests
    test_result = subprocess.run(["pytest", "--tb=short"], capture_output=True)
    checks.append(f"Tests: {'✓' if test_result.returncode == 0 else '✗'}")
    
    # Check linting
    lint_result = subprocess.run(["flake8", "."], capture_output=True)
    checks.append(f"Linting: {'✓' if lint_result.returncode == 0 else '✗'}")
    
    # Check formatting
    format_result = subprocess.run(["black", "--check", "."], capture_output=True)
    checks.append(f"Formatting: {'✓' if format_result.returncode == 0 else '✗'}")
    
    return "\n".join(checks)
```

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Claude Code Settings Reference](https://docs.anthropic.com/en/docs/claude-code/settings)
- [MCP SDK Documentation](https://modelcontextprotocol.io/reference)

This guide provides comprehensive information for using MCP servers effectively within Claude Code, enabling powerful development workflows and custom tool integration.