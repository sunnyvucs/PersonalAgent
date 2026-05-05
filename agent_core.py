import os
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.tools import tool
import fitz  # pymupdf

MODEL_NAME = "agent-sk-fast"

SYSTEM_PROMPT = """You are Agent-SK, a helpful personal AI assistant.
You can read, write, update, delete, and list files on the user's machine. You can also read and extract text from PDF files.
When given a working directory, prefer using full absolute paths.
Always confirm what action you took after completing it.
If you are unsure about a destructive action (like deleting), ask for confirmation first.

When listing chapters or any numbered items from a document, always format them exactly like this:
Chapter 1 : The Living World
Chapter 2 : Biological Classification
...and so on. No extra commentary, no bullet points, just the clean list."""


@tool
def read_file(path: str) -> str:
    """Read the contents of a file at the given absolute or relative path."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, creating it if it doesn't exist and overwriting if it does."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"File written successfully: {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def append_to_file(path: str, content: str) -> str:
    """Append content to an existing file without overwriting it."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Content appended to: {path}"
    except Exception as e:
        return f"Error appending to file: {e}"


@tool
def list_directory(path: str) -> str:
    """List all files and folders in a directory."""
    try:
        entries = list(Path(path).iterdir())
        if not entries:
            return "Directory is empty."
        return "\n".join(
            f"[DIR]  {e.name}" if e.is_dir() else f"[FILE] {e.name}"
            for e in sorted(entries)
        )
    except Exception as e:
        return f"Error listing directory: {e}"


@tool
def delete_file(path: str) -> str:
    """Delete a file at the given path."""
    try:
        Path(path).unlink()
        return f"File deleted: {path}"
    except Exception as e:
        return f"Error deleting file: {e}"


@tool
def create_directory(path: str) -> str:
    """Create a directory (and any missing parent directories)."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return f"Directory created: {path}"
    except Exception as e:
        return f"Error creating directory: {e}"


@tool
def read_pdf(path: str, start_page: int = 1, end_page: int = 10) -> str:
    """Read and extract text from a PDF file. start_page and end_page are 1-based page numbers."""
    try:
        doc = fitz.open(path)
        total = len(doc)
        s = max(1, start_page) - 1
        e = min(end_page, total)
        parts = []
        for i in range(s, e):
            text = doc[i].get_text().strip()
            if text:
                parts.append(f"--- Page {i+1} ---\n{text}")
        doc.close()
        return "\n\n".join(parts) if parts else "No text found in the specified page range."
    except Exception as ex:
        return f"Error reading PDF: {ex}"


TOOLS = [read_file, write_file, append_to_file, list_directory, delete_file, create_directory, read_pdf]


def build_agent():
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    return create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)


def run_agent(agent, user_input: str, working_dir: str = None, chat_history: list = None):
    full_input = user_input
    if working_dir:
        full_input = f"[Working directory: {working_dir}]\n{user_input}"

    messages = list(chat_history or [])
    messages.append({"role": "human", "content": full_input})

    result = agent.invoke({"messages": messages})

    # Extract the last AI message from the result
    output_messages = result.get("messages", [])
    for msg in reversed(output_messages):
        role = getattr(msg, "type", None) or getattr(msg, "role", None)
        if role in ("ai", "assistant"):
            return msg.content

    return "No response generated."
