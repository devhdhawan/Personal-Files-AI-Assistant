
# Personal Files AI Assistant

A local, privacy-first AI assistant that answers questions using only your own documents stored in a `data/` folder and indexed in ChromaDB.  
The assistant runs as an MCP server and is queried by a Gemini-based chat client.

---

## Project Structure

- `data/`  
  Folder containing your source documents (for example, `notes-python.txt`, `project-specs.txt`, `kafka-guide.txt`).  
  Every `.txt` file in this folder is loaded, chunked, and indexed into ChromaDB.

- `chroma_db/`  
  Persistent ChromaDB storage (created at runtime).

- `src/`  
  - `chromaDB.py` – MCP server exposing a `searchdocument` tool backed by ChromaDB; handles:
    - Loading all files from `data/`.
    - Splitting them into chunks.
    - Storing/retrieving embeddings from ChromaDB.
  - `browser_mcp.json` – MCP server configuration used by the client to start/connect to the MCP server.

- `main.py` – Chat client using `MCPAgent` + Gemini to talk to the MCP server and answer from retrieved chunks.

- `.env` – Environment variables (for example, `GOOGLE_API_KEY`).

- `pyproject.toml`, `requirements.txt`, `uv.lock` – Dependency and environment management files.

---

## Features

- Automatically scans the `data/` directory, reads each file, and splits content into chunks with `RecursiveCharacterTextSplitter`.
- Stores all chunks in a persistent ChromaDB instance under per-file collections (for example, one collection per source name).
- Exposes a single MCP tool `searchdocument` that:
  - Accepts a natural-language query.
  - Queries across all indexed collections for the most relevant chunks.
  - Returns the best-matching document snippets to the client.
- Chat client (`main.py`) uses Gemini (`gemini-2.5-flash`) with MCPAgent to:
  - Call `searchdocument` for each user query.
  - Generate answers using only the retrieved local document snippets.

> Note: The example code currently includes an `allowedterms` list that was tuned for tech topics; you can keep, remove, or customize that restriction depending on your use case.

---

## Prerequisites

- Python (project uses `uv run` for commands).
- Google API key with access to Gemini models.
- `uv` installed globally.
- Ability to install dependencies from `requirements.txt` / `pyproject.toml`.

---

## Setup

1. **Clone the repository** and open it in your editor.

2. **Create a `.env` file** in the project root:
```

GOOGLE_API_KEY=your_api_key_here

```

3. **Install dependencies** with `uv`:
```

uv sync

```

4. **Add your documents**  
Place any `.txt` files you want the assistant to use inside the `data/` directory.  
These can be notes, specs, guides, or any other plain-text documents.

---

## Running the MCP Server

From the project root:

```

uv run --with mcp[cli] mcp run "src/chromaDB.py"

```

On startup you should see:

- Chroma telemetry logs.
- A list of collection names corresponding to your files (for example, `['notes-python_docs', 'project-specs_docs', ...]`).

The process remains running because `mcp.run(transport="stdio")` blocks inside `if __name__ == "__main__":`.

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
"C:/Users/your-user/path/to/Personal-Files-AI-Assistant/src/chromaDB.py"
]
}
}
}

```

- Tells the MCP client how to start/connect to the `PersonalFileAssistant` server.
- Update the path to match your local project location.

---

## Running the Chat Client

With the MCP server running, in a second terminal from the project root:

```

uv run main.py

```

You should see something like:

```

Chatbot initialized. Type 'exit' to quit.
You:

```

Ask questions whose answers are contained in your documents, for example:

- “Summarize my Kafka notes.”
- “What steps are listed in the deployment checklist?”
- “Explain the concept of X from my notes.”

For each question, the agent will:

1. Call `searchdocument` on the MCP server.
2. Retrieve the most relevant chunks from all indexed collections.
3. Generate an answer using only those retrieved chunks.

---

## Customization

- **Document Types**: By default, the example ingests `.txt` files; you can extend the loader logic in `chromaDB.py` to support other formats (for example, Markdown or PDFs via additional loaders).
- **Chunking**: Adjust `chunk_size` and `chunk_overlap` in `RecursiveCharacterTextSplitter` to better suit long or short documents.
- **Retrieval Logic**: Modify how many results to return per collection (`n_results`), combine scores differently, or add filters by metadata.
- **LLM Behavior**: Tune model, temperature, and `max_steps` in `main.py` for more concise, verbose, or strictly tool-following behavior.

---

## Troubleshooting

- **Server exits immediately**
  - Ensure `if __name__ == "__main__":` in `chromaDB.py` calls `mcp.run(transport="stdio")` and does not only execute test calls.

- **No or poor answers**
  - Confirm `data/` contains non-empty text files.
  - Add debug prints in `searchdocument` to log incoming queries and the number of results before returning.

- **Client cannot connect**
  - Verify the path in `browser_mcp.json`.
  - Ensure the MCP server is running before starting `main.py`.


