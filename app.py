"""
FastAPI server for AstraeaV3_env.
Implements the full OpenEnv HTTP API:
  POST /reset
  POST /step
  GET  /state
  GET  /tasks
  POST /grader
  POST /baseline
"""

import asyncio
import os
import time
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from pydantic import BaseModel

import sys
import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from AstraeaV3_env.models import (
    ActionType,
    Decision,
    ReviewAction,
    ReviewReward
)
from AstraeaV3_env.server.environment import (
    ScientificPeerReviewEnv,
    TASKS,
    grade_episode
)

app = FastAPI(
    title="AstraeaV3_env",
    description="OpenEnv environment for training AI agents to perform ML paper peer review.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Support for Hugging Face/Reverse Proxies (HTTPS)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")


_sessions: Dict[str, ScientificPeerReviewEnv] = {}
_session_locks: Dict[str, asyncio.Lock] = {}


dashboard_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(dashboard_dir):
    app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")



# Request/Response schemas


class ResetRequest(BaseModel):
    task_id: str = "task1"
    reviewer_persona: str = "standard"
    seed: int = 42


class StepRequest(BaseModel):
    session_id: str
    action: ReviewAction


class GraderRequest(BaseModel):
    session_id: str


class BaselineRequest(BaseModel):
    task_ids: Optional[list] = None
    model: str = "gpt-4o-mini"



# OpenEnv endpoints


@app.get("/")
def root():
    # Redirect to dashboard if available, otherwise return info
    if os.path.exists(dashboard_dir):
        return RedirectResponse(url="/dashboard/", status_code=303)
    return {
        "name": "AstraeaV3_env",
        "version": "1.0.0",
        "description": "Train AI agents to perform ML paper peer review",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/grader", "/baseline"],
    }


@app.post("/reset")
def reset(req: ResetRequest):
    """Reset the environment and return initial observation."""
    env = ScientificPeerReviewEnv(
        task_id=req.task_id,
        reviewer_persona=req.reviewer_persona,
        seed=req.seed,
    )
    obs = env.reset()
    session_id = obs.episode_id
    _sessions[session_id] = env
    _session_locks[session_id] = asyncio.Lock()
    return {
        "session_id": session_id,
        "observation": obs.model_dump(),
    }


@app.post("/upload_paper")
def upload_paper(paper: Dict[str, Any]):
    """Special endpoint for Task 5: Upload a custom paper and start a session."""

    env = ScientificPeerReviewEnv(
        task_id="task_bonus_2",
        reviewer_persona="expert",
        seed=int(time.time()),
    )
   
    obs = env.reset(custom_paper=paper)
    session_id = obs.episode_id
    _sessions[session_id] = env
    _session_locks[session_id] = asyncio.Lock()
    
    return {
        "session_id": session_id,
        "observation": obs.model_dump(),
    }


@app.post("/step")
async def step(req: StepRequest):
    """Execute one action in the environment."""
    env = _sessions.get(req.session_id)
    lock = _session_locks.get(req.session_id)
    
    if not env or not lock:
        raise HTTPException(status_code=404, detail=f"Session {req.session_id} not found. Call /reset first.")

    async with lock:
        try:
            # Run the synchronous step in a thread pool to avoid blocking the event loop
            obs, reward, done, info = await asyncio.to_thread(env.step, req.action)
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Environment Error: {str(e)}")

    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def state(session_id: str):
    """Return current environment state."""
    env = _sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return env.state()


@app.get("/hint")
async def hint(session_id: str):
    """Provide an AI hint for the current manuscipt."""
    env = _sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return env.get_hint()


@app.get("/tasks")
def tasks():
    """Return available tasks and action schema."""
    return {
        "tasks": [
            {
                "task_id": tid,
                "name": tcfg["name"],
                "description": tcfg["description"],
                "difficulty": tcfg["difficulty"],
                "max_steps": tcfg["max_steps"],
                "scoring": tcfg["scoring"],
                "target_actions": tcfg["target_actions"],
            }
            for tid, tcfg in TASKS.items()
        ],
        "action_schema": ReviewAction.model_json_schema(),
        "observation_schema": "See /reset response for full observation structure",
        "reward_schema": ReviewReward.model_json_schema(),
    }


@app.post("/grader")
def grader(req: GraderRequest):
    """Grade a completed episode. Returns score 0.0-1.0."""
    env = _sessions.get(req.session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session {req.session_id} not found.")

    score, feedback = grade_episode(env)
    return {
        "session_id": req.session_id,
        "task_id": env.task_id,
        "score": score,
        "feedback": feedback,
        "episode_state": env.state(),
    }


@app.post("/baseline")
async def baseline(req: BaselineRequest):
    """Run the baseline agent against all 3 tasks and return scores."""
    task_ids = req.task_ids or ["task1", "task2", "task3"]
    results = {}

    for task_id in task_ids:
        try:
            score = _run_baseline_agent_local(task_id)
            results[task_id] = {"score": score, "status": "success"}
        except Exception as e:
            results[task_id] = {"score": 0.0, "status": "error", "error": str(e)}

    return {
        "model": req.model,
        "results": results,
        "average_score": sum(r["score"] for r in results.values()) / len(results),
    }


def _run_baseline_agent_local(task_id: str) -> float:
    """Run the baseline agent. Uses LLM if OPENAI_API_KEY/HF_TOKEN is set, otherwise mock."""
    from inference import run_local_baseline
    has_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN"))
    return run_local_baseline(task_id, mock=not has_key)


@app.get("/health")
def health():
    return {"status": "healthy"}


def main():
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 1))
    
    uvicorn.run(
        "AstraeaV3_env.server.app:app", 
        host=host, 
        port=port, 
        workers=workers,
        reload=(os.environ.get("ENABLE_RELOAD", "false").lower() == "true")
    )

if __name__ == "__main__":
    main()
