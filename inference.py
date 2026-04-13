#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import textwrap
import multiprocessing
from typing import List, Optional

try:
    import psutil
    def log_hardware_context():
        cpu_count = multiprocessing.cpu_count()
        mem = psutil.virtual_memory()
        print(f"[RESOURCES] Evaluation Context: {cpu_count} vCPUs | {mem.total/(1024**3):.2f} GB RAM", flush=True)
        print(f"[RESOURCES] Target Alignment: Optimized for 2 vCPU / 8 GB RAM (CPU-only)", flush=True)
except ImportError:
    def log_hardware_context():
        print(f"[RESOURCES] psutil not available", flush=True)

from openai import OpenAI
try:
    from dotenv import load_dotenv
    # Check root .env first, then AstraeaV3_env/.env
    if os.path.exists(".env"):
        load_dotenv(".env", override=True)
    elif os.path.exists("AstraeaV3_env/.env"):
        load_dotenv("AstraeaV3_env/.env", override=True)
    else:
        load_dotenv(override=True)
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(__file__))

from AstraeaV3_env.server.environment import (
    ActionType, Decision, ReviewAction,
    ScientificPeerReviewEnv, TASKS, grade_episode,
)

# MANDATORY env vars
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
TASK_NAME    = os.getenv("TASK_NAME", "task1")
BENCHMARK    = "astraea_peer_review"
MAX_STEPS    = 10
TERMINATION_SCORE_THRESHOLD = 0.5

# MANDATORY stdout format
def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}", flush=True)

def log_end(success, steps, score, rewards):
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={','.join(f'{r:.2f}' for r in rewards)}", flush=True)

def build_system_prompt():
    return textwrap.dedent("""
        You are ASTRAEA, a Senior Research Reviewer auditing an ML manuscript.
        VALID action_type: flag_concern, assign_score, write_review_segment, submit_decision
        VALID concern_type: reproducibility, novelty, soundness, missing_baseline, data_leakage,
          statistical, gradient_issue, non_deterministic, clarity, equation_error
        RULES:
        1. Output ONLY raw JSON matching ReviewAction schema.
        2. flag_concern needs: concern_type, concern_location, concern_description, concern_severity(0-1)
        3. assign_score needs: dimension(novelty/soundness/presentation/contribution), score(0-10)
        4. write_review_segment needs: aspect(strengths/weaknesses/methodology/future_work), text(30+ words)
        5. submit_decision needs: decision(accept/minor_revision/major_revision/reject)
        6. Always flag at least one concern before submit_decision.
    """).strip()

def build_user_prompt(step, obs, last_reward, task_id):
    sections_preview = {k: v[:200] + "..." if len(v) > 200 else v
                        for k, v in obs.get("sections", {}).items()}
    return textwrap.dedent(f"""
        AUDIT STEP: {step}/{obs.get('max_steps', 10)} | TASK: {task_id}
        MANUSCRIPT: {obs.get('paper_title', 'Unknown')}
        SECTIONS: {json.dumps(sections_preview, indent=2)}
        ALREADY FLAGGED: {[c.get('concern_type') for c in obs.get('flagged_concerns', [])]}
        SCORES GIVEN: {obs.get('dimension_scores', {})}
        LAST REWARD: {last_reward:.2f}
        Select your next review action as JSON.
    """).strip()


MOCK_SEQUENCES = {
    "task1": [
        {"action_type": "flag_concern", "concern_type": "data_leakage",
         "concern_location": "method", "concern_severity": 0.9,
         "concern_description": "Test set used for hyperparameter selection — invalidates all reported results."},
        {"action_type": "flag_concern", "concern_type": "statistical",
         "concern_location": "results", "concern_severity": 0.5,
         "concern_description": "No standard deviations or confidence intervals reported for benchmarks."},
        {"action_type": "submit_decision", "decision": "major_revision"},
    ],
    "task2": [
        {"action_type": "flag_concern", "concern_type": "missing_baseline",
         "concern_location": "results", "concern_severity": 0.6,
         "concern_description": "Missing comparison with SpAtten and recent token pruning methods from 2022-2023."},
        {"action_type": "flag_concern", "concern_type": "soundness",
         "concern_location": "method", "concern_severity": 0.4,
         "concern_description": "Percentile threshold theta selection lacks justification and sensitivity analysis."},
        {"action_type": "submit_decision", "decision": "minor_revision"},
    ],
    "task3": [
        {"action_type": "flag_concern", "concern_type": "reproducibility",
         "concern_location": "method", "concern_severity": 0.7,
         "concern_description": "Hand-crafted Prolog rules not released or described — results cannot be reproduced."},
        {"action_type": "assign_score", "dimension": "novelty",      "score": 6.0},
        {"action_type": "assign_score", "dimension": "soundness",    "score": 7.0},
        {"action_type": "assign_score", "dimension": "presentation", "score": 8.0},
        {"action_type": "assign_score", "dimension": "contribution", "score": 6.5},
        {"action_type": "submit_decision", "decision": "minor_revision"},
    ],
    "task4": [
        {"action_type": "flag_concern", "concern_type": "gradient_issue",
         "concern_location": "method", "concern_severity": 0.95,
         "concern_description": "optimizer.zero_grad() missing inside training loop — gradients accumulate infinitely causing NaN weights."},
        {"action_type": "flag_concern", "concern_type": "non_deterministic",
         "concern_location": "method", "concern_severity": 0.4,
         "concern_description": "No random seed set for distributed initialization — results are non-reproducible."},
        {"action_type": "assign_score", "dimension": "soundness",    "score": 2.0},
        {"action_type": "assign_score", "dimension": "novelty",      "score": 7.0},
        {"action_type": "submit_decision", "decision": "reject"},
    ],
}

async def get_model_action(client, step, obs, last_reward, task_id):
    use_mock = (not HF_TOKEN) or os.getenv("MOCK_BASELINE", "false").lower() == "true"
    if use_mock:
        seq = MOCK_SEQUENCES.get(task_id, MOCK_SEQUENCES["task1"])
        idx = step - 1
        if idx < len(seq):
            return seq[idx]
        return {"action_type": "submit_decision", "decision": "major_revision"}
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user",   "content": build_user_prompt(step, obs, last_reward, task_id)},
            ],
            temperature=0,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        return json.loads((completion.choices[0].message.content or "").strip())
    except Exception as exc:
        print(f"[DEBUG] LLM failed step {step}: {exc}", flush=True)
        return {"action_type": "submit_decision", "decision": "major_revision"}

async def run_episode(task_id: str) -> float:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "mock")
    env = ScientificPeerReviewEnv(task_id=task_id, seed=42)
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    try:
        obs_model   = env.reset()
        obs         = obs_model.model_dump()
        done        = False
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if done:
                break
            action_dict = await get_model_action(client, step, obs, last_reward, task_id)
            action_str  = f"{action_dict.get('action_type','unknown')}({json.dumps(action_dict, separators=(',',':'))})"
            try:
                obs_model, reward_model, done, info = env.step(ReviewAction(**action_dict))
                obs       = obs_model.model_dump()
                reward    = float(reward_model.total)
                error_msg = None
            except Exception as exc:
                reward    = 0.0
                done      = True
                error_msg = str(exc)[:80]
            rewards.append(reward)
            steps_taken = step
            last_reward = reward
            log_step(step=step, action=action_str, reward=reward, done=done, error=error_msg)
            if done:
                break

        grade_result = grade_episode(env)
        score   = float(grade_result[0]) if isinstance(grade_result, tuple) else float(grade_result)
        score   = max(0.01, min(0.99, score))
        success = score >= TERMINATION_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)
        score, success = 0.0, False
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score

def run_local_baseline(task_id: str, mock: bool = False) -> float:
    """Called by app.py /baseline endpoint."""
    if mock:
        os.environ["MOCK_BASELINE"] = "true"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_episode(task_id))
    finally:
        loop.close()
        if mock:
            os.environ["MOCK_BASELINE"] = "false"

async def main() -> None:
    log_hardware_context()
    task_id = sys.argv[1] if len(sys.argv) > 1 else TASK_NAME
    if task_id == "all":
        scores = []
        for tid in ["task1", "task2", "task3", "task4"]:
            s = await run_episode(tid)
            scores.append(s)
        print(f"[SUMMARY] Average: {sum(scores)/len(scores):.2f}", flush=True)
    else:
        await run_episode(task_id)

if __name__ == "__main__":
    asyncio.run(main())
