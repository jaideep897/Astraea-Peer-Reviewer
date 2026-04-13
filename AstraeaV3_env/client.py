import httpx
from typing import Dict, Any, Optional
from .models import ReviewAction, PaperObservation, ReviewReward

class PeerReviewClient:

    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.session_id: Optional[str] = None

    def reset(self, task_id: str = "task1", reviewer_persona: str = "standard", seed: int = 42) -> PaperObservation:
        resp = httpx.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id, "reviewer_persona": reviewer_persona, "seed": seed},
            timeout=30.0
        )
        resp.raise_for_status()
        data = resp.json()
        self.session_id = data["session_id"]
        return PaperObservation(**data["observation"])

    def step(self, action: ReviewAction) -> tuple[PaperObservation, ReviewReward, bool, Dict[str, Any]]:
        if not self.session_id:
            raise RuntimeError("Call reset() before step()")
        
        resp = httpx.post(
            f"{self.base_url}/step",
            json={"session_id": self.session_id, "action": action.model_dump()},
            timeout=30.0
        )
        resp.raise_for_status()
        data = resp.json()
        return (
            PaperObservation(**data["observation"]),
            ReviewReward(**data["reward"]),
            data["done"],
            data["info"]
        )

    def state(self) -> Dict[str, Any]:
        if not self.session_id:
            return {"status": "not_started"}
        resp = httpx.get(f"{self.base_url}/state", params={"session_id": self.session_id})
        resp.raise_for_status()
        return resp.json()

    def grade(self) -> float:
        if not self.session_id:
            raise RuntimeError("No active session to grade")
        resp = httpx.post(f"{self.base_url}/grader", json={"session_id": self.session_id})
        resp.raise_for_status()
        return resp.json().get("score", 0.0)

    def get_tasks(self) -> Dict[str, Any]:
        resp = httpx.get(f"{self.base_url}/tasks")
        resp.raise_for_status()
        return resp.json().get("tasks", {})
