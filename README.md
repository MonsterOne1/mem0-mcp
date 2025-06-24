# MCP Server with Mem0 for Personal AI Assistant Memory

This demonstrates a structured approach for using an [MCP](https://modelcontextprotocol.io/introduction) server with [mem0](https://mem0.ai) to manage personal information and preferences for AI assistants. The server can be used with Cursor and provides essential tools for storing, retrieving, and searching personal memories and information.

## Installation

1. Clone this repository
2. Initialize the `uv` environment:

```bash
uv venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`:

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Update `.env` file in the root directory with your mem0 API key:

```bash
MEM0_API_KEY=your_api_key_here
```

## Usage

1. Start the MCP server:

```bash
uv run main.py
```

2. In Cursor, connect to the SSE endpoint, follow this [doc](https://docs.cursor.com/context/model-context-protocol) for reference:

```
http://0.0.0.0:8080/sse
```

3. Open the Composer in Cursor and switch to `Agent` mode.

## Demo with Cursor

https://github.com/user-attachments/assets/56670550-fb11-4850-9905-692d3496231c

## Features

The server provides three main tools for managing personal information:

1. `add_memory`: Store personal information, preferences, and important details including:
   - Personal preferences and habits
   - Important facts and knowledge
   - Contact information and relationships
   - Goals, plans, and aspirations
   - Skills, expertise, and learning interests
   - Important dates and events
   - Context from previous conversations

2. `get_all_memories`: Retrieve all stored personal information to review patterns, check preferences, and ensure no relevant information is missed.

3. `search_memories`: Semantically search through stored personal information to find relevant:
   - Personal preferences and details
   - Knowledge and facts
   - Important dates and events
   - Skills and expertise
   - Goals and plans
   - Context from previous conversations

## Why?

This implementation allows for a persistent personal memory system that can be accessed via MCP. The SSE-based server can run as a process that AI assistants connect to, use, and disconnect from whenever needed. This pattern fits well with "cloud-native" use cases where the server and clients can be decoupled processes on different nodes.

### Server

By default, the server runs on 0.0.0.0:8080 but is configurable with command line arguments like:

```
uv run main.py --host <your host> --port <your port>
```

The server exposes an SSE endpoint at `/sse` that MCP clients can connect to for accessing the personal memory management tools.

