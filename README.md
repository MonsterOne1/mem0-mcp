# mem0-mcp

A simplified MCP (Model Context Protocol) server for persistent memory management using [mem0.ai](https://mem0.ai). This server enables AI assistants to remember information across conversations.

## Features

- **Persistent Memory**: Store and retrieve information across conversations
- **Semantic Search**: Find relevant memories using natural language
- **Simple API**: Just 3 core tools for memory management

## Quick Start

### Prerequisites

- Python 3.8+
- mem0.ai API key (get one at [mem0.ai](https://mem0.ai))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mem0-mcp.git
cd mem0-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your MEM0_API_KEY
```

### Running the Server

```bash
python main.py
```

#### Custom Configuration
```bash
python main.py --host 0.0.0.0 --port 8080 --debug
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM0_API_KEY` | Your mem0.ai API key | Required |
| `PORT` | Server port | 8080 |
| `DEFAULT_USER_ID` | Default user ID for memories | cursor_mcp |

### Command Line Options

```
python main.py [OPTIONS]

Options:
  --host HOST           Host to bind to (default: 0.0.0.0)
  --port PORT           Port to bind to (default: 8080)
  --name NAME           Server name (default: mem0-mcp)
  --debug               Enable debug mode
  --no-instructions     Disable custom instructions
```

## Available Tools

1. **add_memory** - Add new information to memory
2. **search_memories** - Search memories using natural language
3. **get_all_memories** - Retrieve all stored memories

## Integration

### Claude Desktop / Cursor

Add to your MCP settings:

```json
{
  "mcpServers": {
    "mem0-mcp": {
      "command": "python",
      "args": ["/path/to/mem0-mcp/main.py"]
    }
  }
}
```

## Project Structure

```
mem0-mcp/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── mem0_client.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── memory_tools.py
│   └── server/
│       ├── __init__.py
│       ├── main.py
│       └── server_factory.py
├── main.py
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [mem0.ai](https://mem0.ai) for the memory API
- [Anthropic MCP](https://github.com/anthropics/mcp) for the protocol specification