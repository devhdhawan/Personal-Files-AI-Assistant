# Smart Personal Knowledge Base Assistant

A Model Context Protocol (MCP) server that provides AI assistants with access to a local knowledge base. This server enables AI agents to search, add, and manage documents in a vector database for efficient retrieval and context-aware responses. It can connect with different LLMs to provide intelligent document processing and retrieval capabilities.

## Features

- **Document Search**: Semantic search across your knowledge base using vector embeddings
- **Document Management**: Add and organize documents with metadata
- **Document Summaries**: Get quick overviews of documents in the knowledge base
- **RAG Integration**: Uses ChromaDB for efficient vector storage and retrieval

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (for embeddings)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Usage

1. What is OpenAI API key? Why is it needed?
OpenAI API key is a secret token that lets your app access OpenAI’s cloud AI services (like GPT, embeddings, etc.).
Why needed:
In your project, you use OpenAI’s embedding models to convert text/documents into vectors for semantic search. The API key authenticates your requests and enables these features.

2. What is STORAGE_PATH? Why is it needed?
STORAGE_PATH is a configuration variable (from .env) that tells your server where to store and find your knowledge base (documents, notes, etc.).
Why needed:
It keeps your data organized and persistent.
Example: If STORAGE_PATH=./knowledge_base, all files and vector databases are saved in the knowledge_base folder.

3. What is LangChain? What is ChromaDB? (Detailed)
LangChain
LangChain is a Python library for building applications with language models (LLMs).
Features:
Loads documents in various formats (PDF, DOCX, TXT)
Splits text into manageable chunks
Integrates with vector stores and LLMs
Chains together multiple AI operations (search, summarize, etc.)
ChromaDB
ChromaDB is an open-source vector database.
Features:
Stores vector embeddings of text/documents
Enables fast similarity search (find documents similar to a query)
Persistent storage (saves data between server restarts)
Why used together:
LangChain loads and processes documents, generates embeddings (with OpenAI), and stores them in ChromaDB for semantic search.

4. Why did we choose FastAPI web server?
FastAPI is a modern, fast Python web framework.
Reasons for choice:
High performance (async support)
Automatic API docs (Swagger/OpenAPI)
Easy endpoint definition with Python type hints
Great for building APIs that interact with AI models and clients

5. Where do we load our documents/knowledge base?
Documents are loaded from the folder specified by STORAGE_PATH (e.g., ./knowledge_base).
The KnowledgeBase class in server.py uses LangChain’s loaders to read files from this directory, process them, and store their embeddings in ChromaDB.

6. Explain mcp.json in detail. How do we start the MCP server?
mcp.json is a VS Code configuration file for MCP servers.

Purpose:
Tells VS Code how to start your MCP server so AI clients can connect.

Example:
{
    "servers": {
        "knowledge-base-server": {
            "type": "stdio",
            "command": "python",
            "args": ["server.py"]
        }
    }
}

"type": "stdio" means the server communicates over standard input/output.
"command": "python" and "args": ["server.py"] tells VS Code to run your server with python server.py.
How to start:
In VS Code, you can use the MCP extension or run the command defined in mcp.json to start the server.

7. What AI client do we choose? Can we add others?
AI client chosen:
You can use Claude Desktop, Cursor, or any MCP-compatible client.
Can you add others?
Yes! Any client that supports MCP protocol (JSON-RPC over stdio or HTTP) can connect.
You can also write your own custom client in Python, TypeScript, etc.

## Development

### Project Structure

```
mcp-knowledge-base/
├── server.py             # Main MCP server implementation
├── requirements.txt      # Python dependencies
├── .env                 # Configuration settings
└── knowledge_base/      # Local storage for vector database
```

### Adding New Features

To add new tools or capabilities:

1. Add new methods to the `KnowledgeBaseServer` class
2. Register them as tools using the `@app.tool()` decorator
3. Update documentation as needed

## Security Notes

- The server is designed for local use and requires proper configuration for production deployments
- API keys should be kept secure and never committed to version control
- Consider implementing authentication if deploying in a multi-user environment

=======
# Smart-Personal-Knowledge-Base-Assistant
Smart Personal Knowledge Base Assistant using MCP to connect with Different LLM's
