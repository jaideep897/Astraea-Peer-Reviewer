"""
Tests for ScientificPeerReview-Env.
Run with: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from AstraeaV3_env.server.environment import (
    ActionType,
    ConcernType,
    Decision,
    ReviewAction,
    ScientificPeerReviewEnv,
    TASKS,
    grade_episode,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def task1_env():
    env = ScientificPeerReviewEnv(task_id="task1", seed=42)
    env.reset()
    return env


@pytest.fixture
def task2_env():
    env = ScientificPeerReviewEnv(task_id="task2", seed=42)
    env.reset()
    return env


@pytest.fixture
def task3_env():
    env = ScientificPeerReviewEnv(task_id="task3", seed=42)
    env.reset()
    return env


# ---------------------------------------------------------------------------
# Basic functionality tests
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_returns_observation(self):
        env = ScientificPeerReviewEnv(task_id="task1", seed=42)
        obs = env.reset()
        assert obs is not None
        assert obs.paper_title
        assert obs.sections
        assert obs.task_id == "task1"
        assert obs.step_count == 0
        assert not obs.decision_submitted

    def test_reset_clears_state(self, task1_env):
        env = task1_env
        env.step(ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.SOUNDNESS,
            concern_location="method",
            concern_severity=0.5,
            concern_description="test",
        ))
        env.reset()
        assert len(env._observation.flagged_concerns) == 0
        assert env._observation.step_count == 0

    def test_reset_requires_valid_task(self):
        with pytest.raises(ValueError):
            ScientificPeerReviewEnv(task_id="invalid_task")


class TestStep:
    def test_step_returns_tuple(self, task1_env):
        env = task1_env
        action = ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.DATA_LEAKAGE,
            concern_location="method",
            concern_severity=0.9,
            concern_description="Test set used for hyperparameter selection",
        )
        obs, reward, done, info = env.step(action)
        assert obs is not None
        assert reward is not None
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_step_increments_counter(self, task1_env):
        env = task1_env
        env.step(ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.STATISTICAL,
            concern_location="results",
            concern_severity=0.5,
            concern_description="No error bars",
        ))
        assert env._observation.step_count == 1

    def test_step_after_done_raises(self, task1_env):
        env = task1_env
        env.step(ReviewAction(
            action_type=ActionType.SUBMIT_DECISION,
            decision=Decision.MAJOR_REVISION,
            confidence=0.8,
        ))
        with pytest.raises(RuntimeError):
            env.step(ReviewAction(
                action_type=ActionType.SUBMIT_DECISION,
                decision=Decision.REJECT,
                confidence=0.5,
            ))

    def test_step_without_reset_raises(self):
        env = ScientificPeerReviewEnv(task_id="task1")
        with pytest.raises(RuntimeError):
            env.step(ReviewAction(
                action_type=ActionType.SUBMIT_DECISION,
                decision=Decision.ACCEPT,
                confidence=0.5,
            ))


class TestActions:
    def test_flag_correct_concern_gives_reward(self, task1_env):
        env = task1_env
        action = ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.DATA_LEAKAGE,
            concern_location="method",
            concern_severity=0.9,
            concern_description="Test set used for hyperparameter selection",
        )
        _, reward, _, _ = env.step(action)
        assert reward.concern_precision > 0

    def test_flag_wrong_concern_gives_penalty(self, task1_env):
        env = task1_env
        action = ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.CITATION,
            concern_location="conclusion",
            concern_severity=0.3,
            concern_description="Missing citations",
        )
        _, reward, _, _ = env.step(action)
        assert reward.concern_penalty < 0

    def test_assign_score_well_calibrated(self, task2_env):
        env = task2_env
        action = ReviewAction(
            action_type=ActionType.ASSIGN_SCORE,
            dimension="soundness",
            score=6.5,  # GT is 6.5
        )
        _, reward, _, _ = env.step(action)
        assert reward.score_calibration > 0

    def test_write_substantive_segment_rewarded(self, task3_env):
        env = task3_env
        action = ReviewAction(
            action_type=ActionType.WRITE_REVIEW_SEGMENT,
            aspect="weaknesses",
            text="The paper has a critical flaw: the test set is used for hyperparameter selection which completely invalidates all reported results. This needs to be corrected with a proper train/validation/test split.",
        )
        _, reward, _, _ = env.step(action)
        assert reward.review_quality > 0

    def test_submit_correct_decision(self, task1_env):
        env = task1_env
        action = ReviewAction(
            action_type=ActionType.SUBMIT_DECISION,
            decision=Decision.MAJOR_REVISION,
            confidence=0.9,
        )
        _, reward, done, _ = env.step(action)
        assert done
        assert reward.decision_accuracy > 0


class TestState:
    def test_state_before_reset(self):
        env = ScientificPeerReviewEnv(task_id="task1")
        state = env.state()
        assert state["status"] == "not_started"

    def test_state_after_reset(self, task1_env):
        state = task1_env.state()
        assert "task_id" in state
        assert state["task_id"] == "task1"
        assert state["done"] == False


class TestGraders:
    def test_task1_grader_perfect_score(self):
        env = ScientificPeerReviewEnv(task_id="task1", seed=42)
        env.reset()
        
        # Flag all ground truth concerns
        env.step(ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.DATA_LEAKAGE,
            concern_location="method",
            concern_severity=0.9,
            concern_description="Test set used for hyperparameter selection",
        ))
        env.step(ReviewAction(
            action_type=ActionType.FLAG_CONCERN,
            concern_type=ConcernType.STATISTICAL,
            concern_location="results",
            concern_severity=0.5,
            concern_description="No confidence intervals",
        ))
        env.step(ReviewAction(
            action_type=ActionType.SUBMIT_DECISION,
            decision=Decision.MAJOR_REVISION,
            confidence=0.9,
        ))
        
        score, feedback = grade_episode(env)
        print(f"DEBUG: score={score}, feedback={feedback}")
        assert score > 0.7  # Should score well
        assert 0.0 <= score <= 1.0

    def test_task1_grader_zero_score(self):
        env = ScientificPeerReviewEnv(task_id="task1", seed=42)
        env.reset()
        env.step(ReviewAction(
            action_type=ActionType.SUBMIT_DECISION,
            decision=Decision.ACCEPT,  # Wrong decision
            confidence=0.5,
        ))
        score, feedback = grade_episode(env)
        assert score < 0.3

    def test_task2_grader_range(self):
        env = ScientificPeerReviewEnv(task_id="task2", seed=42)
        env.reset()
        for dim, val in [("novelty", 4.0), ("soundness", 6.5), ("presentation", 7.5), ("contribution", 5.0)]:
            env.step(ReviewAction(action_type=ActionType.ASSIGN_SCORE, dimension=dim, score=val))
        env.step(ReviewAction(action_type=ActionType.SUBMIT_DECISION, decision=Decision.MINOR_REVISION, confidence=0.8))
        score, feedback = grade_episode(env)
        assert 0.0 <= score <= 1.0
        assert score >= 0.3

    def test_task3_grader_range(self):
        env = ScientificPeerReviewEnv(task_id="task3", seed=42)
        env.reset()
        env.step(ReviewAction(action_type=ActionType.WRITE_REVIEW_SEGMENT, aspect="strengths", text="The paper addresses an important problem with clear experimental results across multiple benchmarks."))
        env.step(ReviewAction(action_type=ActionType.WRITE_REVIEW_SEGMENT, aspect="weaknesses", text="Critical data leakage issue invalidates results. No statistical significance testing provided."))
        env.step(ReviewAction(action_type=ActionType.SUBMIT_DECISION, decision=Decision.MAJOR_REVISION, confidence=0.85))
        score, feedback = grade_episode(env)
        assert 0.0 <= score <= 1.0

    def test_all_grader_scores_in_range(self):
        """Graders must always return 0.0–1.0."""
        for task_id in ["task1", "task2", "task3"]:
            env = ScientificPeerReviewEnv(task_id=task_id, seed=42)
            env.reset()
            env.step(ReviewAction(
                action_type=ActionType.SUBMIT_DECISION,
                decision=Decision.REJECT,
                confidence=0.5,
            ))
            score, feedback = grade_episode(env)
            assert 0.0 <= score <= 1.0, f"Grader for {task_id} returned out-of-range score: {score}"


class TestTasks:
    def test_all_tasks_defined(self):
        for task_id in ["task1", "task2", "task3"]:
            assert task_id in TASKS

    def test_task_difficulty_progression(self):
        difficulties = {"easy": 1, "medium": 2, "hard": 3}
        for i, task_id in enumerate(["task1", "task2", "task3"]):
            expected_level = i + 1
            actual_level = difficulties[TASKS[task_id]["difficulty"]]
            assert actual_level == expected_level

    def test_max_steps_increases_with_difficulty(self):
        steps = [TASKS[f"task{i}"]["max_steps"] for i in range(1, 4)]
        assert steps[0] < steps[1] < steps[2]
