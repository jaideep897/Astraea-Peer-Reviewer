import asyncio
import httpx
import os
import json
import time

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")

TASKS_DATA = [
    {
        "id": "task1",
        "name": "Audit Warmup",
        "actions": [
            {"action_type": "flag_concern", "concern_type": "data_leakage", "concern_location": "method", "concern_description": "Test set used for hyperparameter selection."},
            {"action_type": "submit_decision", "decision": "major_revision"}
        ]
    },
    {
        "id": "task2",
        "name": "Soundness Check",
        "actions": [
            {"action_type": "flag_concern", "concern_type": "missing_baseline", "concern_location": "results", "concern_description": "Missing comparison with recent pruning methods."},
            {"action_type": "submit_decision", "decision": "minor_revision"}
        ]
    },
    {
        "id": "task3",
        "name": "Score Calibration",
        "actions": [
            {"action_type": "assign_score", "dimension": "novelty", "score": 6.0},
            {"action_type": "assign_score", "dimension": "soundness", "score": 7.0},
            {"action_type": "assign_score", "dimension": "presentation", "score": 8.0},
            {"action_type": "submit_decision", "decision": "minor_revision"}
        ]
    },
    {
        "id": "task4",
        "name": "PyTorch Rigor",
        "actions": [
            {"action_type": "flag_concern", "concern_type": "gradient_issue", "concern_location": "method", "concern_description": "Missing zero_grad() call."},
            {"action_type": "submit_decision", "decision": "reject"}
        ]
    },
    {
        "id": "task_bonus_1",
        "name": "Full Audit Protocol",
        "actions": [
            {"action_type": "flag_concern", "concern_type": "soundness", "concern_location": "method", "concern_description": "Mathematical invalidity in Theorem 3.1."},
            {"action_type": "assign_score", "dimension": "soundness", "score": 2.0},
            {"action_type": "submit_decision", "decision": "reject"}
        ]
    }
]

async def run_task(client, task_info):
    # Mapping task IDs to folder names
    task_map = {
        "task1": "task_1_audit_warmup",
        "task2": "task_2_soundness_check",
        "task3": "task_3_score_calibration",
        "task4": "task_4_pytorch_rigor",
        "task_bonus_1": "task_5_full_audit"
    }
    folder_name = task_map.get(task_info["id"], "unknown")
    actual_folder = f"assets/demo_runs/{folder_name}"
    
    log_file = os.path.join(actual_folder, "logs.txt")
    print(f"Running {task_info['name']}...")
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"=== ASTRAEA DEMO: {task_info['name']} ===\n\n")
        
        # Reset
        try:
            resp = await client.post(f"{BASE_URL}/reset", json={"task_id": task_info["id"], "reviewer_persona": "expert"})
            resp.raise_for_status()
            data = resp.json()
            session_id = data["session_id"]
            f.write(f"[INIT] Session: {session_id}\n")
            f.write(f"[INIT] Paper: {data['observation']['paper_title']}\n\n")
            
            for action in task_info["actions"]:
                f.write(f"[ACTION] {action['action_type'].upper()}: {action}\n")
                resp = await client.post(f"{BASE_URL}/step", json={"session_id": session_id, "action": action})
                resp.raise_for_status()
                step_data = resp.json()
                reward = step_data["reward"]["total"]
                feedback = step_data["info"]["explanation"]["scientific_feedback"]
                f.write(f"[REWARD] +{reward:.2f}\n")
                f.write(f"[FEEDBACK] {feedback}\n\n")
                await asyncio.sleep(0.5)
                
            # Final State
            resp = await client.get(f"{BASE_URL}/state", params={"session_id": session_id})
            resp.raise_for_status()
            state = resp.json()
            f.write(f"[STATUS] Task Completed: {state['done']}\n")
            f.write(f"[STATUS] Total Reward: {state['total_reward']:.2f}\n")
            print(f"Completed {task_info['name']}. Total Reward: {state['total_reward']:.2f}")
        except Exception as e:
            f.write(f"[ERROR] {str(e)}\n")
            print(f"Error in {task_info['name']}: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        for task in TASKS_DATA:
            await run_task(client, task)

if __name__ == "__main__":
    asyncio.run(main())
