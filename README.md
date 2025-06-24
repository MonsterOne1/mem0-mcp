# mem0-mcp

A unified MCP (Model Context Protocol) server for persistent memory management using [mem0.ai](https://mem0.ai). This server enables AI assistants to remember information across conversations, providing a human-like memory system.

## Features

- **Persistent Memory**: Store and retrieve information across conversations
- **Semantic Search**: Find relevant memories using natural language
- **Auto-categorization**: Automatically categorize memories (personal info, work, goals, etc.)
- **Two Modes**: 
  - **Basic Mode**: Essential memory operations (add, search, get all)
  - **Full Mode**: Advanced features including update, delete, statistics, and analysis
- **Multiple Deployment Options**: Local development, cloud deployment (Render, etc.)
- **Chatwise Integration**: Import/export memories from Chatwise chat exports
- **Extensible Architecture**: Modular design for easy customization

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

#### Basic Mode (3 tools)
```bash
python main.py
```

#### Full Mode (all tools)
```bash
python src/server/main.py --mode full
```

#### Custom Configuration
```bash
python src/server/main.py --host 0.0.0.0 --port 8080 --mode full --debug
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM0_API_KEY` | Your mem0.ai API key | Required |
| `PORT` | Server port | 8080 |
| `MODE` | Server mode (basic/full) | full |
| `DEBUG` | Enable debug logging | false |
| `DEFAULT_USER_ID` | Default user ID for memories | cursor_mcp |

### Command Line Options

```
python src/server/main.py [OPTIONS]

Options:
  --mode {basic,full}    Server mode (default: full)
  --host HOST           Host to bind to (default: 0.0.0.0)
  --port PORT           Port to bind to (default: 8080)
  --name NAME           Server name (default: mem0-mcp)
  --debug               Enable debug mode
  --no-instructions     Disable custom instructions
```

## Available Tools

### Basic Mode Tools

1. **add_memory** - Add new information to memory
2. **search_memories** - Search memories using natural language
3. **get_all_memories** - Retrieve all stored memories

### Full Mode Tools (includes Basic tools plus)

4. **update_memory** - Update existing memories
5. **delete_memory** - Delete specific memories
6. **advanced_search_memories** - Search with filters (category, score)
7. **get_memory_stats** - Get statistics about stored memories
8. **analyze_memories** - Analyze patterns and insights
9. **get_memories_by_category** - Get memories by category
10. **export_memories** - Export all memories in JSON format
11. **check_relevant_memories** - Quick check for topic-relevant memories

## Memory Categories

Memories are automatically categorized into:

- **personal_info** - Name, age, location, contact details
- **work** - Job, career, professional information
- **relationships** - Family, friends, social connections
- **goals** - Plans, aspirations, objectives
- **knowledge** - Facts, learning, information
- **skills** - Abilities, languages, expertise
- **dates_events** - Important dates, appointments
- **preferences** - Likes, dislikes, favorites
- **health** - Medical, wellness, fitness
- **hobbies** - Entertainment, leisure activities
- **technical** - Programming, technology
- **finance** - Money, budget, investments

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

### Chatwise

1. Start the server with SSE support
2. In Chatwise, add MCP server:
   - Name: `mem0-mcp`
   - URL: `http://localhost:8080/sse`
   - Transport: SSE

## Import/Export

### Import from Chatwise

```python
from src.importers import import_memories

# Import a single file
result = import_memories("chatwise_export.json")

# Preview before importing
from src.importers import preview_import
preview = preview_import("chatwise_export.json", limit=10)
```

### Export Memories

```python
from src.importers import export_memories

# Export all memories
export_memories("my_memories_backup.json", include_metadata=True)
```

## Development

### Project Structure

```
mem0-mcp/
├── src/
│   ├── core/           # Core modules (client, config, categories)
│   ├── tools/          # Memory tools implementation
│   ├── server/         # Server implementation
│   └── importers/      # Import/export utilities
├── scripts/            # Utility scripts
├── docs/              # Documentation
└── main.py            # Legacy entry point
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Deployment

### Render

1. Click [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
2. Set environment variables
3. Deploy

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/server/main.py", "--mode", "full"]
```

## Troubleshooting

### Common Issues

1. **"MEM0_API_KEY is required"** - Set your API key in .env file
2. **"Failed to validate request"** - Ensure the server is fully initialized before making requests
3. **Connection errors** - Check firewall settings and port availability

### Debug Mode

Enable debug logging:
```bash
python src/server/main.py --debug
# or
export DEBUG=true
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [mem0.ai](https://mem0.ai) for the memory API
- [Anthropic MCP](https://github.com/anthropics/mcp) for the protocol specification
- Contributors and maintainers