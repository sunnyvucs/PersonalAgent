from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agent_core import build_agent, run_agent

app = FastAPI(title="Agent-SK", description="Personal AI Agent powered by Gemma via Ollama")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = build_agent()

# session_id -> list of {"role": "human"/"ai", "content": "..."}
sessions: dict[str, list] = {}


class ChatRequest(BaseModel):
    message: str
    working_dir: Optional[str] = None
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or "default"

    if session_id not in sessions:
        sessions[session_id] = []

    try:
        response = run_agent(
            agent,
            user_input=req.message,
            working_dir=req.working_dir,
            chat_history=sessions[session_id],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    sessions[session_id].append({"role": "human", "content": req.message})
    sessions[session_id].append({"role": "ai", "content": response})

    # Keep last 20 turns
    sessions[session_id] = sessions[session_id][-40:]

    return ChatResponse(response=response, session_id=session_id)


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    sessions.pop(session_id, None)
    return {"message": f"Session '{session_id}' cleared."}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "Agent-SK"}
