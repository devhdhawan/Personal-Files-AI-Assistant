
# Personal Files AI Assistant

A local, privacy-first AI assistant that answers questions using only your personal tech notes (Python, Java, SQL, PySpark, Kafka) stored in ChromaDB, exposed via an MCP server and queried by a Gemini-based chat client.

---

## Project Structure

- `data/`
  - `python.txt`
  - `java.txt`
  - `sql.txt`
  - `pyspark.txt`
  - `kafka.txt`
- `chroma_db/`
  - Persistent ChromaDB storage (created at runtime)
- `src/`
  - `chromaDB.py` – MCP server exposing the `searchdocument` tool backed by ChromaDB.
  - `browser_mcp.json` – MCP server configuration for the client.
- `main.py` – Chat client using `MCPAgent` + Gemini to talk to the MCP server.
- `.env` – Environment variables (for example, `GOOGLE_API_KEY`).
- `pyproject.toml`, `requirements.txt`, `uv.lock` – Dependency and environment management files.

---

## Features

- Ingests notes from `data/*.txt` and stores chunked embeddings in ChromaDB collections.
- Provides a `searchdocument` MCP tool that:
  - Searches across `python_docs`, `java_docs`, `sql_docs`, `pyspark_docs`, `kafka_docs` collections.
  - Restricts questions to these topics using an `allowedterms` check.
- Chat client (`main.py`) uses Gemini (`gemini-2.5-flash`) with MCPAgent to:
  - Call `searchdocument` for each query.
  - Answer using only retrieved local documents, not general model knowledge.

---

## Prerequisites

- Python (managed with `uv`, since commands use `uv run`).
- Google API key with access to Gemini models.
- `uv` installed globally.
- Ability to install dependencies from `requirements.txt` / `pyproject.toml`.

---

## Setup

1. **Clone the repository** and open it in your editor (for example, VS Code).
2. **Create a `.env` file** in the project root:
```

GOOGLE_API_KEY=your_api_key_here

```
3. **Install dependencies** with `uv`:
```

uv sync

```
4. **Fill your data files**  
Edit the text files in `data/` (`python.txt`, `java.txt`, `sql.txt`, `pyspark.txt`, `kafka.txt`) with your own notes.

---

## Running the MCP Server

From the project root:

```

uv run --with mcp[cli] mcp run "src/chromaDB.py"

```

On startup you should see:

- Chroma telemetry logs.
- A line showing loaded collections, for example:
```

['java_docs', 'kafka_docs', 'pyspark_docs', 'python_docs', 'sql_docs']

```
The process stays running because `mcp.run(transport="stdio")` blocks in `if __name__ == "__main__":`.

---

## MCP Configuration (`browser_mcp.json`)

`src/browser_mcp.json`:

```

{
"mcp_servers": {
"PersonalFileAssistant": {
"command": "uv",
"args": [
"run",
"--with",
"mcp[cli]",
"mcp",
"run",
"src/chromaDB.py"
]
}
}
}

```

- Tells the MCP client how to start/connect to the `PersonalFileAssistant` server.
- Update the path if you move the project or run on another machine.

---

## Running the Chat Client

With the MCP server already running, in a second terminal from the project root:

```

uv run main.py

```

You should see something like:

```

Chatbot initialized. Type 'exit' to quit.
You:

```

Example queries:

- `What is Python?`
- `Explain Kafka topics and partitions.`
- `What is an SQL join?`

For each question, the agent will:

1. Call `searchdocument` on the MCP server.
2. Retrieve the most relevant chunk(s) from ChromaDB.
3. Generate an answer using only those retrieved chunks.

---

## Customization

- Add more `.txt` files to `data/` and extend `allowedterms` / collection loading logic in `chromaDB.py` to support new topics.
- Tune chunking via `RecursiveCharacterTextSplitter` (chunk size, overlap) in `chromaDB.py` for different document sizes.
- Adjust LLM parameters (model name, temperature, `max_steps`) inside `main.py` to change answer style and tool-calling behavior.

---

## Troubleshooting

- **Server exits immediately**
  - Ensure `if __name__ == "__main__":` in `chromaDB.py` calls `mcp.run(transport="stdio")` and does not just run test functions.

- **No answer or empty results**
  - Confirm data files are non-empty and ingestion ran once.
  - Add debug prints in `searchdocument` to log the query and the number of results before returning.

- **Client cannot connect**
  - Verify the path in `browser_mcp.json`.
  - Ensure the MCP server is running before starting `main.py`.


