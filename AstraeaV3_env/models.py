from __future__ import annotations

import json
import random
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Action Space
# ---------------------------------------------------------------------------

class ActionType(str, Enum):
    REQUEST_CLARIFICATION = "request_clarification"
    FLAG_CONCERN = "flag_concern"
    ASSIGN_SCORE = "assign_score"
    WRITE_REVIEW_SEGMENT = "write_review_segment"
    SUBMIT_DECISION = "submit_decision"


class ConcernType(str, Enum):
    REPRODUCIBILITY = "reproducibility"
    NOVELTY = "novelty"
    SOUNDNESS = "soundness"
    MISSING_BASELINE = "missing_baseline"
    DATA_LEAKAGE = "data_leakage"
    STATISTICAL = "statistical"
    CITATION = "citation"
    SCOPE = "scope"
    CLARITY = "clarity"
    EQUATION_ERROR = "equation_error"
    METHODOLOGICAL_FLAW = "methodological_flaw"
    NON_DETERMINISTIC = "non_deterministic"
    MEMORY_INEFFICIENCY = "memory_inefficiency"
    GRADIENT_ISSUE = "gradient_issue"


class Decision(str, Enum):
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"


class ReviewAction(BaseModel):
    """The action an agent can take in the peer review environment."""
    action_type: ActionType = Field(..., description="Type of review action")

    # For REQUEST_CLARIFICATION
    section: Optional[str] = Field(None, description="Section to clarify (abstract/intro/method/results/conclusion)")
    question: Optional[str] = Field(None, description="Clarification question text")

    # For FLAG_CONCERN
    concern_type: Optional[ConcernType] = Field(None, description="Type of concern")
    concern_location: Optional[str] = Field(None, description="Where in paper (section name)")
    concern_severity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Severity 0.0–1.0")
    concern_description: Optional[str] = Field(None, description="Description of the concern")

    # For ASSIGN_SCORE
    dimension: Optional[str] = Field(None, description="Dimension: novelty/soundness/presentation/contribution")
    score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Score 0–10")

    # For WRITE_REVIEW_SEGMENT
    aspect: Optional[str] = Field(None, description="Aspect: strengths/weaknesses/questions/limitations")
    text: Optional[str] = Field(None, description="Review text for this segment")

    # For SUBMIT_DECISION
    decision: Optional[Decision] = Field(None, description="Final accept/reject decision")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in decision")


# ---------------------------------------------------------------------------
# Observation Space
# ---------------------------------------------------------------------------

class PaperSection(BaseModel):
    title: str
    content: str
    code_context: Optional[str] = Field(None, description="Optional PyTorch code snippet for this section")


class FlaggedConcern(BaseModel):
    concern_type: str
    location: str
    severity: float
    description: str


class ReviewSegment(BaseModel):
    aspect: str
    text: str


class PaperObservation(BaseModel):
    """Full observation returned after each step."""
    episode_id: str = Field(..., description="Unique episode identifier")
    paper_id: str = Field(..., description="Paper identifier")
    paper_title: str
    sections: Dict[str, str] = Field(..., description="Paper sections: abstract/intro/method/results/conclusion")
    
    # Accumulated review state
    flagged_concerns: List[FlaggedConcern] = Field(default_factory=list)
    review_segments: Dict[str, str] = Field(default_factory=dict)
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    clarification_history: List[Dict[str, str]] = Field(default_factory=list)
    
    # Task metadata
    task_id: str = Field(..., description="Task identifier: task1/task2/task3")
    step_count: int = Field(0)
    max_steps: int = Field(20)
    total_reward: float = Field(0.0, description="Cumulative reward in this session")
    reviewer_persona: str = Field("standard", description="Reviewer persona type")
    
    # Adaptive Telemetry (PALE)
    neural_xp: float = Field(0.0, description="Total experience points earned")
    expert_level: int = Field(1, description="Current auditor level")
    
    # Episode status
    decision_submitted: bool = False
    submitted_decision: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure mutable defaults are always properly initialized
        if self.flagged_concerns is None:
            object.__setattr__(self, 'flagged_concerns', [])
        if self.review_segments is None:
            object.__setattr__(self, 'review_segments', {})
        if self.dimension_scores is None:
            object.__setattr__(self, 'dimension_scores', {})
        if self.clarification_history is None:
            object.__setattr__(self, 'clarification_history', [])


# ---------------------------------------------------------------------------
# Reward Model
# ---------------------------------------------------------------------------

class ReviewReward(BaseModel):
    """Reward signal with breakdown."""
    total: float = Field(..., description="Total reward this step")
    concern_precision: float = Field(0.0, description="Reward for correct concern flags")
    concern_penalty: float = Field(0.0, description="Penalty for hallucinated concerns")
    question_relevance: float = Field(0.0, description="Reward for relevant clarification questions")
    score_calibration: float = Field(0.0, description="Reward for well-calibrated scores")
    review_quality: float = Field(0.0, description="Reward for review segment quality")
    decision_accuracy: float = Field(0.0, description="Reward for correct final decision")
    step_efficiency: float = Field(0.0, description="Small penalty per step to encourage efficiency")
    neural_xp: float = Field(0.0, description="XP earned from this specific action")
    feedback: str = Field("", description="Detailed scientific critique from the environment")
