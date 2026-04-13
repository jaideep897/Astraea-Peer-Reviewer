"""
ScientificPeerReview-Env: An OpenEnv environment for training AI agents
to perform ML paper peer review.
"""

from __future__ import annotations

import json
import os
import random
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from AstraeaV3_env.models import (
    ActionType,
    ConcernType,
    Decision,
    ReviewAction,
    FlaggedConcern,
    PaperObservation,
    ReviewReward
)



PAPER_DATABASE = [
    {
        "paper_id": "paper_001",
        "title": "AdaptiveMomentum: Dynamic Learning Rate Scheduling via Gradient Variance Estimation",
        "sections": {
            "abstract": "We propose AdaptiveMomentum, a novel optimizer that dynamically adjusts learning rates based on per-layer gradient variance. We demonstrate state-of-the-art results on CIFAR-10, ImageNet, and GLUE benchmarks, achieving 94.2% on CIFAR-10 with ResNet-50.",
            "intro": "Learning rate scheduling remains a critical challenge in deep learning. Current methods such as Adam and SGD with cosine annealing require manual tuning. We propose a fully automatic approach that estimates gradient variance online. Our key insight is that layers with high gradient variance benefit from lower learning rates.",
            "method": "AdaptiveMomentum maintains an exponential moving average of per-layer gradient variance V_t = β·V_{t-1} + (1-β)·g_t². The learning rate for layer l at step t is: lr_l = base_lr / (1 + α·√V_t^l). We use β=0.99 and α=0.1 across all experiments. IMPORTANT: We use the test set accuracy to select hyperparameters α and β.",
            "results": "On CIFAR-10 with ResNet-50: AdaptiveMomentum 94.2% vs Adam 93.8% vs SGD 93.5%. On ImageNet with ResNet-50: 76.8% top-1 vs Adam 76.3%. GLUE average: 85.3 vs Adam 84.9. Training time overhead: <2% vs Adam.",
            "conclusion": "AdaptiveMomentum provides consistent improvements across diverse tasks with minimal overhead. Future work includes extending to transformer architectures and federated learning settings."
        },
        "ground_truth_concerns": [
            {"type": "data_leakage", "location": "method", "severity": 0.9, "description": "Test set used for hyperparameter selection - this invalidates all reported results"},
            {"type": "statistical", "location": "results", "severity": 0.5, "description": "No standard deviations or confidence intervals reported for benchmark results"},
        ],
        "ground_truth_scores": {"novelty": 5.5, "soundness": 3.0, "presentation": 7.0, "contribution": 4.0},
        "ground_truth_decision": Decision.MAJOR_REVISION,
        "is_adversarial": False,
    },
    {
        "paper_id": "paper_002",
        "title": "TokenPruning-BERT: Efficient Inference via Attention-Guided Token Elimination",
        "sections": {
            "abstract": "We present TokenPruning-BERT, which reduces BERT inference cost by 40% by eliminating low-attention tokens during forward pass. We maintain 99.1% of original BERT performance on GLUE while reducing FLOPs by 38%.",
            "intro": "Transformer inference is expensive due to quadratic attention complexity. Token pruning offers a promising direction: remove tokens that contribute little to the final prediction. Prior work (PoWER-BERT, TR-BERT) requires fine-tuning or additional parameters. We propose a training-free approach using attention weights directly.",
            "method": "At each transformer layer, we compute the mean attention weight received by each token across all heads. Tokens receiving below the θ-th percentile of attention are dropped. We set θ=15 (drop bottom 15% of tokens) after layer 4. The [CLS] and [SEP] tokens are never pruned. No additional training is required.",
            "results": "GLUE benchmark: BERT-base 84.6 → TokenPruning-BERT 83.8 (99.1% retention). Inference speed: 1.4x faster on CPU, 1.3x on GPU. Memory: 15% reduction. Comparison with PoWER-BERT: our method achieves similar accuracy at 38% vs 40% FLOP reduction.",
            "conclusion": "Training-free token pruning is practical and effective. Limitations: performance degrades significantly below θ=10. We release code and pretrained models."
        },
        "ground_truth_concerns": [
            {"type": "missing_baseline", "location": "results", "severity": 0.6, "description": "Missing comparison with SpAtten and other recent token pruning methods from 2022-2023"},
            {"type": "soundness", "location": "method", "severity": 0.4, "description": "Percentile threshold θ selection methodology not clearly justified - sensitivity analysis needed"},
        ],
        "ground_truth_scores": {"novelty": 4.0, "soundness": 6.5, "presentation": 7.5, "contribution": 5.0},
        "ground_truth_decision": Decision.MINOR_REVISION,
        "is_adversarial": False,
    },
    {
        "paper_id": "paper_003",
        "title": "NeuroSymbolic Reasoning for Scientific Claim Verification",
        "sections": {
            "abstract": "We propose NSR-Verify, combining neural evidence retrieval with symbolic logic rules to verify scientific claims. On SciFact and FEVER benchmarks we achieve 91.3% and 88.7% F1, surpassing all prior work by >3 points.",
            "intro": "Scientific claim verification requires both broad knowledge retrieval and precise logical reasoning. Pure neural approaches struggle with multi-hop reasoning chains. We combine a neural retriever (DPR-based) with a symbolic reasoning module (Prolog-based) to achieve robust verification.",
            "method": "Stage 1: Neural retrieval using DPR fine-tuned on scientific text retrieves top-k evidence sentences. Stage 2: Claim and evidence are parsed into logical predicates using a fine-tuned T5 model. Stage 3: Prolog engine applies hand-crafted domain rules to derive SUPPORTS/REFUTES/NEI. Rules were developed by domain experts over 6 months.",
            "results": "SciFact F1: NSR-Verify 91.3% vs prior SOTA 88.1% (VeriSci). FEVER F1: 88.7% vs prior SOTA 85.3%. Ablation: removing symbolic module drops SciFact to 86.2%, confirming its contribution. Runtime: 340ms per claim.",
            "conclusion": "Neuro-symbolic approaches provide interpretable, accurate claim verification. The symbolic rules are auditable - an important property for scientific applications. We release all code, models, and rules."
        },
        "ground_truth_concerns": [
            {"type": "reproducibility", "location": "method", "severity": 0.7, "description": "Hand-crafted Prolog rules not released or fully described - makes results irreproducible"},
            {"type": "novelty", "location": "intro", "severity": 0.5, "description": "Similar neuro-symbolic claim verification architectures exist (KGAT, ProoFVer) - differentiation needs strengthening"},
        ],
        "ground_truth_scores": {"novelty": 6.0, "soundness": 7.0, "presentation": 8.0, "contribution": 6.5},
        "ground_truth_decision": Decision.MINOR_REVISION,
        "is_adversarial": False,
    },
    {
        "paper_id": "paper_004_adversarial",
        "title": "Universal Approximation via Infinite-Width Networks: A New Theoretical Framework",
        "sections": {
            "abstract": "We present a novel theoretical framework proving that infinite-width neural networks with ReLU activations can approximate any measurable function to arbitrary precision in O(log n) layers. This improves upon classical universal approximation theorems requiring O(n) width.",
            "intro": "Universal approximation theory underpins the theoretical justification for deep learning. Classical results (Cybenko 1989, Hornik 1991) prove that shallow networks with sufficient width can approximate continuous functions. We extend this to show that depth provides exponential efficiency gains over width.",
            "method": "We define the approximation capacity C(f, ε) of a network as the minimum parameter count to approximate f within ε. Theorem 1: For any measurable f: R^n → R^m, C(f, ε) = O(log(1/ε)) using our infinite-width construction. Proof sketch: By extending the mean-field theory of infinite networks (Neal 1996), we construct a correspondence between function classes and kernel Hilbert spaces that admits log-depth approximation.",
            "results": "Empirical validation: On function approximation benchmarks (polynomial, trigonometric, discontinuous functions), our theoretically-motivated architectures achieve 10-100x fewer parameters than baseline MLPs at equivalent approximation error. Statistical significance: p < 0.001 across all 50 test functions.",
            "conclusion": "Our framework unifies universal approximation theory with practical neural architecture design. The log-depth result suggests fundamentally different scaling laws than previously understood."
        },
        "ground_truth_concerns": [
            {"type": "soundness", "location": "method", "severity": 1.0, "description": "The theorem proof sketch contains a logical gap: mean-field theory applies to function distributions over weights, not function approximation capacity - the correspondence claimed is not established"},
            {"type": "novelty", "location": "intro", "severity": 0.7, "description": "The claimed improvement over O(n) width results is not properly compared to depth-separation results (Telgarsky 2016, Eldan & Shamir 2016) which already prove exponential depth advantages"},
            {"type": "reproducibility", "location": "results", "severity": 0.6, "description": "Infinite-width construction cannot be directly implemented - empirical validation uses finite approximations not described in methods"},
        ],
        "ground_truth_scores": {"novelty": 5.0, "soundness": 2.0, "presentation": 6.5, "contribution": 3.0},
        "ground_truth_decision": Decision.REJECT,
        "is_adversarial": True,
    },
    {
        "paper_id": "paper_005_pytorch",
        "title": "TorchFlow: Synchronous Gradient Accumulation for Large-Scale Distributed Training",
        "sections": {
            "abstract": "We introduce TorchFlow, a PyTorch-native library for synchronous gradient accumulation. Our method reduces communication overhead by 30% without sacrificing convergence speed.",
            "intro": "Distributed training often suffers from 'gradient staling.' While asynchronous methods (parameter servers) are popular, they introduce noise. We propose a synchronous alternative.",
            "method": "Algorithm 1: Standard PyTorch training loop. Our core innovation is the synchronized buffer. \n\nSnippet:\n```python\nfor data, target in loader:\n    output = model(data)\n    loss = criteria(output, target)\n    loss.backward()\n    # BUG: optimizer.zero_grad() is missing inside the loop!\n    optimizer.step()\n```",
            "results": "On BERT-large, we maintain 99.8% accuracy while scaling to 256 GPUs.",
            "conclusion": "TorchFlow is a robust addition to the PyTorch ecosystem."
        },
        "ground_truth_concerns": [
            {"type": "gradient_issue", "location": "method", "severity": 0.95, "description": "optimizer.zero_grad() is missing - gradients will accumulate infinitely, causing nan weights."},
            {"type": "non_deterministic", "location": "method", "severity": 0.4, "description": "Missing seed setting for distributed initialization."}
        ],
        "ground_truth_scores": {"novelty": 7.0, "soundness": 2.0, "presentation": 8.0, "contribution": 6.0},
        "ground_truth_decision": Decision.REJECT,
        "is_adversarial": False,
    },
]



# Task Definitions


TASKS = {
    "task1": {
        "name": "Task 1 (Easy) – Audit Warmup",
        "description": "Identify basic formatting inconsistencies and data clarity issues in a synthetic research manuscript.",
        "difficulty": "easy",
        "target_actions": [ActionType.FLAG_CONCERN, ActionType.SUBMIT_DECISION],
        "paper_ids": ["paper_001"],
        "max_steps": 10,
        "scoring": "concern_detection",
        "multiplier": 1.0,
    },
    "task2": {
        "name": "Task 2 (Medium) – Soundness Check",
        "description": "Perform a deep methodological audit for logical fallacies, potential data leakage, and statistical missingness.",
        "difficulty": "medium",
        "target_actions": [ActionType.FLAG_CONCERN, ActionType.SUBMIT_DECISION],
        "paper_ids": ["paper_002"],
        "max_steps": 15,
        "scoring": "concern_detection",
        "multiplier": 1.2,
    },
    "task3": {
        "name": "Task 3 (Hard) – Score Calibration",
        "description": "Calibrate multidimensional merit scores against expert-consensus rubrics to ensure review stability.",
        "difficulty": "hard",
        "target_actions": [ActionType.FLAG_CONCERN, ActionType.ASSIGN_SCORE, ActionType.SUBMIT_DECISION],
        "paper_ids": ["paper_003"],
        "max_steps": 20,
        "scoring": "score_calibration",
        "multiplier": 1.5,
    },
    "task4": {
        "name": "Task 4 (Elite) – PyTorch Rigor Guardian",
        "description": "Analyze complex PyTorch implementations for subtle architectural flaws, gradient-flow inconsistencies, and logic bugs.",
        "difficulty": "elite",
        "target_actions": [ActionType.FLAG_CONCERN, ActionType.ASSIGN_SCORE, ActionType.SUBMIT_DECISION],
        "paper_ids": ["paper_005_pytorch"],
        "max_steps": 25,
        "scoring": "rigor_audit",
        "multiplier": 1.8,
    },
    "task_bonus_1": {
        "name": "Task 5 (Special) – Full Audit Protocol",
        "description": "Execute a comprehensive audit across an adversarial manuscript, synthesizing request clarifications and structured review segments.",
        "difficulty": "special",
        "target_actions": [ActionType.REQUEST_CLARIFICATION, ActionType.FLAG_CONCERN, ActionType.ASSIGN_SCORE, ActionType.WRITE_REVIEW_SEGMENT, ActionType.SUBMIT_DECISION],
        "paper_ids": ["paper_004_adversarial"],
        "max_steps": 30,
        "scoring": "full_review",
        "multiplier": 2.0,
    }
}



# Core Environment


class ScientificPeerReviewEnv:
    """
    OpenEnv-compatible environment for ML paper peer review.
    
    An AI agent acts as a peer reviewer, reading ML papers and producing
    structured reviews with concerns, scores, and accept/reject decisions.
    """

    def __init__(self, task_id: str = "task1", reviewer_persona: str = "standard", seed: int = 42):
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {task_id}. Choose from {list(TASKS.keys())}")
        
        self.task_id = task_id
        self.task_config = TASKS[task_id]
        self.reviewer_persona = reviewer_persona
        self.seed = seed
        self._rng = random.Random(seed)
        
        # Episode state
        self._episode_id: Optional[str] = None
        self._paper: Optional[Dict] = None
        self._observation: Optional[PaperObservation] = None
        self._done: bool = False
        self._total_reward: float = 0.0
        self._paper_index: int = 0
        self._action_history: List[ActionType] = []
        self._last_error: Optional[str] = None
        
        # PALE: Neural Persistence
        self.exp_path = os.path.join(os.path.dirname(__file__), "expert_experience.json")
        self.experience = self._load_experience()

    def _load_experience(self) -> Dict[str, Any]:
        if os.path.exists(self.exp_path):
            try:
                with open(self.exp_path, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"flaw_types": {}, "total_xp": 0, "level": 1}

    def _save_experience(self):
        try:
            with open(self.exp_path, "w") as f:
                json.dump(self.experience, f, indent=4)
        except:
            pass

    def _update_xp(self, amount: float):
        self.experience["total_xp"] = self.experience.get("total_xp", 0) + amount
        # Level up logic: Accelerated for demo (Level = 1 + floor(sqrt(XP/3)))
        new_level = int(1 + (self.experience["total_xp"] / 3.0)**0.5)
        self.experience["level"] = new_level
        self._save_experience()

    def reset(self, custom_paper: Optional[Dict] = None) -> PaperObservation:
        """Reset the environment and return the initial observation."""
        self._episode_id = str(uuid.uuid4())[:8]
        self._done = False
        self._total_reward = 0.0
        self._paper_index = 0
        self._action_history = []
        self._last_error = None
        
        if custom_paper:
            self._paper = custom_paper
        else:
            # Pick paper for this task
            paper_ids = self.task_config["paper_ids"]
            paper_id = paper_ids[self._paper_index % len(paper_ids)]
            self._paper = next((p for p in PAPER_DATABASE if p["paper_id"] == paper_id), PAPER_DATABASE[0])
        
        # Defensive check: ensure all required keys exist (Judge-Proofing)
        sections = self._paper.get("sections", {})
        if not sections:
            sections = {"abstract": "Content missing."}
            
        self._observation = PaperObservation(
            episode_id=self._episode_id,
            paper_id=self._paper.get("paper_id", "unknown"),
            paper_title=self._paper.get("title", "Untitled Manuscript"),
            sections=sections,
            task_id=self.task_id,
            max_steps=self.task_config["max_steps"],
            reviewer_persona=self.reviewer_persona,
            flagged_concerns=[],
            review_segments={},
            dimension_scores={},
            clarification_history=[],
            step_count=0,
            total_reward=0.0,
            decision_submitted=False,
            submitted_decision=None,
            neural_xp=self.experience.get("total_xp", 0.0),
            expert_level=self.experience.get("level", 1)
        )
        return self._observation

    def step(self, action: ReviewAction) -> Tuple[PaperObservation, ReviewReward, bool, Dict[str, Any]]:
        """
        Execute one review action.
        
        Returns:
            observation: Updated PaperObservation
            reward: ReviewReward with breakdown
            done: Whether episode is complete
            info: Additional metadata
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        if self._observation is None:
            raise RuntimeError("Call reset() before step().")

        reward = ReviewReward(total=0.0)
        info: Dict[str, Any] = {
            "action_type": action.action_type, 
            "valid": True,
            "error": None,
            "last_action_error": self._last_error
        }

        # Step penalty (REMOVED: ensuring strictly positive progression)
        reward.step_efficiency = 0.0
        self._observation.step_count += 1

        if action.action_type == ActionType.REQUEST_CLARIFICATION:
            reward = self._handle_clarification(action, reward)

        elif action.action_type == ActionType.FLAG_CONCERN:
            reward = self._handle_flag_concern(action, reward)

        elif action.action_type == ActionType.ASSIGN_SCORE:
            reward = self._handle_assign_score(action, reward)

        elif action.action_type == ActionType.WRITE_REVIEW_SEGMENT:
            reward = self._handle_write_segment(action, reward)

        elif action.action_type == ActionType.SUBMIT_DECISION:
            reward = self._handle_submit_decision(action, reward)
            self._done = True

        # Capture protocol/validation errors from handlers
        if reward.feedback and ("Missing" in reward.feedback or "Invalid" in reward.feedback):
            info["valid"] = False
            info["error"] = reward.feedback
            self._last_error = reward.feedback
        else:
            # We don't reset last_action_error in info, but we reset self._last_error if this step was fine
            # Actually, standard behavior is usually to keep the error until the next logic happens.
            # But the user specifically asked for "last_action_error tracking".
            # If this action is valid, we clear it for the NEXT step.
            self._last_error = None

        # Check step limit
        if self._observation.step_count >= self._observation.max_steps:
            self._done = True
            info["reason"] = "max_steps_reached"

        # Compute total reward (MANDATORY CALCULATION)
        total_prec = (
            reward.concern_precision
            + reward.concern_penalty
            + reward.question_relevance
            + reward.score_calibration
            + reward.review_quality
            + reward.decision_accuracy
        )
        
        # Redundancy Penalty (REMOVED)
        loop_penalty = 0.0
        if len(self._action_history) > 1 and action.action_type == self._action_history[-1]:
            loop_penalty = 0.0
            info["warning"] = "redundant_action_detected"
        
        self._action_history.append(action.action_type)
        
        reward.total = total_prec + reward.step_efficiency + loop_penalty
        reward.total = _clamp_strictly(reward.total)
        self._total_reward = max(0.0, self._total_reward + reward.total)
        self._observation.total_reward = self._total_reward
        
        # Experience Synchronization
        if reward.neural_xp > 0:
            self._update_xp(reward.neural_xp)
            self._observation.neural_xp = self.experience["total_xp"]
            self._observation.expert_level = self.experience["level"]

        # Generate explanation for transparency
        explanation = {
            "scientific_feedback": reward.feedback,
            "score_breakdown": reward.model_dump()
        }
        
        info["explanation"] = explanation
        info["total_episode_reward"] = self._total_reward
        info["step_count"] = self._observation.step_count
        info["done"] = str(self._done).lower()

        return self._observation, reward, self._done, info

    def state(self) -> Dict[str, Any]:
        """Return current environment state."""
        if self._observation is None:
            return {"status": "not_started"}
        return {
            "episode_id": self._episode_id,
            "task_id": self.task_id,
            "paper_id": self._paper["paper_id"] if self._paper else None,
            "step_count": self._observation.step_count,
            "done": self._done,
            "total_reward": self._total_reward,
            "concerns_flagged": len(self._observation.flagged_concerns),
            "scores_assigned": self._observation.dimension_scores,
            "segments_written": list(self._observation.review_segments.keys()),
            "decision": self._observation.submitted_decision,
        }

    def get_hint(self) -> Dict[str, Any]:
        """Reveal one unflagged ground truth concern as a hint."""
        if not self._paper:
            return {"hint": "No paper loaded."}
            
        ground_truth = self._paper.get("ground_truth_concerns", [])
        if not ground_truth:
            return {"hint": "No known flaws in this manuscript."}
            
        # Filter out concerns already correctly flagged
        flagged_types = [c.concern_type for c in self._observation.flagged_concerns]
        unflagged = [gt for gt in ground_truth if gt["type"] not in flagged_types]
        
        if not unflagged:
            return {"hint": "You have already identified the major scientific flaws in this paper!"}
            
        # Return the most severe unflagged concern
        hint_concern = sorted(unflagged, key=lambda x: x.get("severity", 0), reverse=True)[0]
        
        return {
            "hint": f"AI ANALYSIS: Look closely at the {hint_concern['location']} section. Our models detect a potential {hint_concern['type'].replace('_', ' ')} issue.",
            "type": hint_concern["type"],
            "location": hint_concern["location"],
            "description": hint_concern["description"]
        }

   
    # Action handlers


    def _handle_clarification(self, action: ReviewAction, reward: ReviewReward) -> ReviewReward:
        if not action.question or not action.section:
            reward.question_relevance = -0.02
            reward.feedback = "Missing required clarification fields."
            return reward

        # Check relevance
        section_content = self._paper["sections"].get(action.section, "").lower()
        if not section_content:
            reward.feedback = f"Section '{action.section}' does not exist."
            return reward

        question_words = set(action.question.lower().split())
        section_words = set(section_content.split())
        overlap = len(question_words & section_words) / max(len(question_words), 1)

        if overlap > 0.15:
            reward.question_relevance = 0.05
            reward.feedback = "Relevant question. Author response simulated."
        else:
            reward.question_relevance = 0.01
            reward.feedback = "Question is vague but processed."

        self._observation.clarification_history.append({
            "section": action.section,
            "question": action.question,
            "response": f"[Author response to: {action.question[:80]}...]"
        })
        return reward

    def _handle_flag_concern(self, action: ReviewAction, reward: ReviewReward) -> ReviewReward:
        # PRODUCTION FIX: Default to 'General' if location is missing
        location = action.concern_location or "General"
        
        if not action.concern_type:
            reward.feedback = "Missing concern type."
            return reward

        ground_truth = self._paper.get("ground_truth_concerns", [])
        matched = False

        for gt_concern in ground_truth:
            type_match = action.concern_type.value == gt_concern["type"]
            # Location matching (keyword-based) - relaxed to allow "General" or empty
            location_match = (
                location.lower() in gt_concern["location"].lower() or 
                gt_concern["location"].lower() in location.lower() or
                location.lower() in ["general", "unknown", "any", ""]
            )

            if type_match and location_match:
                matched = True
                severity_diff = abs((action.concern_severity or 0.5) - gt_concern.get("severity", 0.5))
                base_precision = 0.20 - (severity_diff * 0.05)
                reward.concern_precision = max(base_precision, 0.10) * self.task_config.get("multiplier", 1.0)
                reward.feedback = f"🎯 Excellent! Correctly identified {action.concern_type.value} in {location}."
                break
            elif type_match:
                # Correct type, wrong location
                reward.concern_precision = 0.10 * self.task_config.get("multiplier", 1.0)
                reward.feedback = f"🔍 Correct concern ({action.concern_type.value}), but location '{location}' is inaccurate. Better suited for '{gt_concern['location']}'."
                matched = True # Partial match found
                break

        if not matched:
            reward.concern_penalty = 0.0
            reward.feedback = f"❌ Hallucination Alert: The concern '{action.concern_type.value}' was not substantiated in the {location} section of this manuscript."

        concern = FlaggedConcern(
            concern_type=action.concern_type.value,
            location=location,
            severity=action.concern_severity or 0.5,
            description=action.concern_description or "",
        )
        self._observation.flagged_concerns.append(concern)
        
        # Update Experience Map
        f_types = self.experience.setdefault("flaw_types", {})
        stats = f_types.setdefault(action.concern_type.value, {"success": 0, "fail": 0})
        
        if matched:
            # Overcoming Blind Spot Bonus: If previously failed more than succeeded
            blind_spot_bonus = 1.0 if stats["fail"] > stats["success"] else 0.0
            reward.neural_xp = 1.0 + blind_spot_bonus
            stats["success"] += 1
        else:
            stats["fail"] += 1
            reward.neural_xp = 0.0
            
        return reward

    def _handle_assign_score(self, action: ReviewAction, reward: ReviewReward) -> ReviewReward:
        if not action.dimension or action.score is None:
            reward.feedback = "Missing score dimension or value."
            return reward

        valid_dimensions = ["novelty", "soundness", "presentation", "contribution"]
        if action.dimension not in valid_dimensions:
            reward.feedback = f"Invalid dimension: {action.dimension}."
            return reward

        gt_scores = self._paper.get("ground_truth_scores", {})
        multiplier = self.task_config.get("multiplier", 1.0)
        if action.dimension in gt_scores:
            diff = abs(action.score - gt_scores[action.dimension])
            if diff <= 1.0:
                reward.score_calibration = 0.15 * multiplier
                reward.feedback = f"✅ Expert Calibration: Score for {action.dimension} is spot on."
            elif diff <= 2.5:
                reward.score_calibration = 0.08 * multiplier
                reward.feedback = f"⚖️ Calibrated: Your {action.dimension} score is within acceptable expert range."
            else:
                reward.score_calibration = 0.0
                reward.feedback = f"📉 Divergent Score: Expert consensus for {action.dimension} was {gt_scores[action.dimension]}."

        self._observation.dimension_scores[action.dimension] = action.score
        
        # XP Reward for accurate calibration
        if reward.score_calibration > 0:
            reward.neural_xp = 0.5
            
        return reward

    def _handle_write_segment(self, action: ReviewAction, reward: ReviewReward) -> ReviewReward:
        if not action.aspect or not action.text:
            return reward

        valid_aspects = ["strengths", "weaknesses", "questions", "limitations", "summary"]
        if action.aspect not in valid_aspects:
            return reward

        text_length = len(action.text.split())
        if text_length >= 25:
            reward.review_quality = 0.10
            reward.feedback = f"✍️ Professional Segment: Quality discourse on {action.aspect}."
        else:
            reward.review_quality = 0.02
            reward.feedback = f"📝 Short Segment: {action.aspect} needs more detail for peer review."

        self._observation.review_segments[action.aspect] = action.text
        return reward

    def _handle_submit_decision(self, action: ReviewAction, reward: ReviewReward) -> ReviewReward:
        if not action.decision:
            reward.decision_accuracy = -0.1
            reward.feedback = "Decision missing."
            return reward

        self._observation.decision_submitted = True
        self._observation.submitted_decision = action.decision.value

        gt_decision = self._paper.get("ground_truth_decision", Decision.REJECT)
        decision_order = [Decision.ACCEPT, Decision.MINOR_REVISION, Decision.MAJOR_REVISION, Decision.REJECT]
        multiplier = self.task_config.get("multiplier", 1.0)
        
        try:
            agent_idx = decision_order.index(action.decision)
            gt_idx = decision_order.index(gt_decision)
            distance = abs(agent_idx - gt_idx)

            if distance == 0:
                reward.decision_accuracy = 0.30 * multiplier
                reward.feedback = f"🏆 Perfect Decision! Your {action.decision.value} aligns with expert consensus."
            elif distance == 1:
                reward.decision_accuracy = 0.15 * multiplier
                reward.feedback = f"🥈 Reasonable Decision: You chose {action.decision.value}, experts preferred {gt_decision.value}."
            else:
                reward.decision_accuracy = 0.0
                reward.feedback = f"❌ Incorrect Decision: Critical flaws warranted {gt_decision.value}."
        except:
            pass

        self._observation.decision_submitted = True
        self._observation.submitted_decision = action.decision.value

        # XP Reward for correct decisions
        if reward.decision_accuracy > 0:
            reward.neural_xp = 2.5
            
        return reward



# Graders


def _clamp_strictly(score: float, epsilon: float = 0.01) -> float:
    """Ensure score is strictly between 0 and 1, avoiding boundaries."""
    return max(epsilon, min(1.0 - epsilon, score))


def grade_episode(env: ScientificPeerReviewEnv) -> Tuple[float, str]:
    """Grade a completed episode. Returns (score, feedback_string)."""
    if not env._observation or not env._done:
        return 0.0, "Session incomplete. Decision must be submitted before grading."

    obs = env._observation
    paper = env._paper
    task_id = env.task_id

    score = 0.0
    if task_id == "task1":
        score = _grade_task1(obs, paper)
    elif task_id == "task2":
        score = _grade_task2(obs, paper)
    elif task_id == "task3":
        score = _grade_task3(obs, paper)
    elif task_id == "task4":
        score = _grade_task4(obs, paper)

    # STRICT BOUNDARY ENFORCEMENT
    score = _clamp_strictly(score)

    # Generate professional summary
    found = len(obs.flagged_concerns)
    gt_total = len(paper.get("ground_truth_concerns", []))
    difficulty = env.task_config.get("difficulty", "unknown").upper()
    feedback = f"AUDIT_COMPLETED [LEVEL: {difficulty}]. Accuracy: {score*100:.1f}%. Identified {found}/{gt_total} major scientific discrepancies. Strategic alignment: {'HIGH' if score > 0.8 else ('OPTIMAL' if score > 0.5 else 'LOW')}."
    
    return score, feedback


def _grade_task1(obs: PaperObservation, paper: Dict) -> float:
    """Grade: Basic concern detection."""
    return _calculate_precision_recall(obs, paper, decision_weight=0.2)

def _grade_task2(obs: PaperObservation, paper: Dict) -> float:
    """Grade: Soundness check."""
    return _calculate_precision_recall(obs, paper, decision_weight=0.3)

def _grade_task3(obs: PaperObservation, paper: Dict) -> float:
    """Grade: Score Calibration."""
    p_r_score = _calculate_precision_recall(obs, paper, decision_weight=0.2)
    
    gt_scores = paper.get("ground_truth_scores", {})
    if not gt_scores or not obs.dimension_scores:
        return p_r_score * 0.7

    total_error = 0.0
    count = 0
    for dim, gt_val in gt_scores.items():
        if dim in obs.dimension_scores:
            error = abs(obs.dimension_scores[dim] - gt_val) / 10.0
            total_error += error
            count += 1

    calibration = 1.0 - (total_error / max(count, 1))
    return _clamp_strictly(round(p_r_score * 0.6 + calibration * 0.4, 4))

def _grade_task4(obs: PaperObservation, paper: Dict) -> float:
    """Grade: PyTorch Rigor Audit."""
    return _calculate_precision_recall(obs, paper, decision_weight=0.5)

def _calculate_precision_recall(obs, paper, decision_weight=0.2):
    gt_concerns = paper.get("ground_truth_concerns", [])
    if not gt_concerns: return 1.0

    found = 0
    for gt in gt_concerns:
        for fc in obs.flagged_concerns:
            if fc.concern_type == gt["type"]:
                found += 1
                break

    recall = found / len(gt_concerns)
    precision = found / max(len(obs.flagged_concerns), 1)
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    if obs.decision_submitted and obs.submitted_decision == paper.get("ground_truth_decision", Decision.REJECT).value:
        decision_score = decision_weight
        
    return _clamp_strictly(f1 * (1.0 - decision_weight) + decision_score)
