# Agent-SK — Personal AI File & Document Assistant

A fully local AI agent that understands natural language and acts on your filesystem. Built with LangChain, FastAPI, and Ollama — no cloud, no subscriptions, runs entirely on your machine.

---

## What it does

You talk to it like a person. It reads files, writes files, lists directories, extracts text from PDFs, and manages your filesystem — all from a browser chat UI.

**Example conversations:**
```
You: List everything in D:/Projects/MyApp
SK: [DIR] src  [FILE] README.md  [FILE] config.py ...

You: Read the file notes.txt and summarize it
SK: The file contains 3 tasks: ...

You: Create a file called todo.txt with a list of 5 Python learning topics
SK: File written successfully: todo.txt

You: Extract the chapter list from Biology-Class-12.pdf
SK: Chapter 1 : The Living World
    Chapter 2 : Biological Classification ...
```

---

## Architecture

```
Browser (chat.html)
      │
      │ POST /chat  {message, working_dir, session_id}
      ▼
FastAPI Server (server.py)  ←→  Session memory (last 20 turns)
      │
      ▼
LangChain Agent (agent_core.py)
      │
      ├── read_file       — Read any text file
      ├── write_file      — Create or overwrite a file
      ├── append_to_file  — Append to an existing file
      ├── list_directory  — List files and folders
      ├── delete_file     — Delete a file (asks for confirmation)
      ├── create_directory — Create folders recursively
      └── read_pdf        — Extract text from PDF (page range aware)
      │
      ▼
Ollama  (Gemma 4B — runs locally on CPU/GPU)
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Ollama + Gemma 4B (local, no cloud) |
| Agent framework | LangChain (`langchain-ollama`) |
| API server | FastAPI + Uvicorn |
| PDF extraction | PyMuPDF (fitz) |
| Chat UI | Vanilla HTML/CSS/JS (dark theme) |
| Session memory | In-memory, last 20 turns per session |

---

## Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.10+

Pull the model before first run:
```bash
ollama pull gemma2:2b
```

Or use any model you prefer — just update `MODEL_NAME` in `agent_core.py`.

> The included `Modelfile` configures a custom `agent-sk-fast` variant of Gemma with a 4096 token context window. Create it with:
> ```bash
> ollama create agent-sk-fast -f Modelfile
> ```

---

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/sunnyvucs/PersonalAgent.git
cd PersonalAgent

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**Windows shortcut:** double-click `start.bat` — it activates the venv, installs deps, and starts the server in one step.

---

## Open the Chat UI

Once the server is running, open `chat.html` directly in your browser (no separate frontend server needed).

- Set a **Working Directory** to restrict the agent to a specific folder (recommended)
- Leave it blank to allow unrestricted access to any path
- Use **Session ID** to maintain separate conversation contexts
- Click **Clear Session** to reset conversation history

---

## API Reference

### `POST /chat`
Send a message to the agent.

```json
{
  "message": "List all files in D:/Projects",
  "working_dir": "D:/Projects",
  "session_id": "default"
}
```

Response:
```json
{
  "response": "[DIR] src\n[FILE] README.md\n[FILE] config.py",
  "session_id": "default"
}
```

### `DELETE /session/{session_id}`
Clear the conversation history for a session.

### `GET /health`
Check if the server is running.
```json
{ "status": "ok", "agent": "Agent-SK" }
```

---

## Project Structure

```
PersonalAgent/
├── agent_core.py     ← LangChain agent + all tool definitions
├── server.py         ← FastAPI server + session management
├── chat.html         ← Browser chat UI (open directly)
├── Modelfile         ← Ollama custom model config (Gemma 4B, 4096 ctx)
├── requirements.txt  ← Python dependencies
└── start.bat         ← One-click startup for Windows
```

---

## Customization

**Swap the LLM:** Change `MODEL_NAME` in `agent_core.py` to any model available in Ollama (`llama3.2`, `phi3`, `mistral`, etc.)

**Add tools:** Define a new function with `@tool` decorator in `agent_core.py` and add it to the `TOOLS` list.

**Restrict paths:** Pass a `working_dir` in every request to keep the agent sandboxed to a folder.

---

> Built as a personal learning project exploring LangChain agents, tool use, and local LLM deployment with Ollama.
