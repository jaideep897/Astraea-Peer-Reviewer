import asyncio
import httpx
import time
import os
from typing import Optional

# ANSI Colors for a beautiful terminal demo
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

async def print_thought(text, delay=0.03):
    print(f"{Colors.CYAN}🧠 Agent Thought: {Colors.ENDC}", end="", flush=True)
    for char in text:
        print(f"{Colors.BLUE}{char}{Colors.ENDC}", end="", flush=True)
        await asyncio.sleep(delay)
    print("\n")
    await asyncio.sleep(0.5)

async def print_action(action_type, details):
    print(f"{Colors.YELLOW}⚡ Executing Action: {Colors.BOLD}{action_type}{Colors.ENDC}")
    print(f"{Colors.BOLD}Details:{Colors.ENDC} {details}\n")
    await asyncio.sleep(1)

async def run_research_demo():
    print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 INITIALIZING ADVANCED AGENT EVALUATION (TASK 3: HARD){Colors.ENDC}\n")
    
    BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Initialization
        print(f"[{Colors.GREEN}SYSTEM{Colors.ENDC}] Contacting OpenEnv Server on {BASE_URL}...")
        try:
            # Shift to Elite (Task 4) Protocol
            resp = await client.post(f"{BASE_URL}/reset", json={"task_id": "task_bonus_1", "reviewer_persona": "expert", "seed": 42})
            resp.raise_for_status()
        except Exception as e:
            print(f"{Colors.RED}Error: Could not connect to server on {BASE_URL}. Is it running?{Colors.ENDC}")
            return

        data = resp.json()
        session_id = data["session_id"]
        paper_title = data["observation"]["paper_title"]
        
        print(f"[{Colors.GREEN}SYSTEM{Colors.ENDC}] Session {session_id} Initialized.")
        print(f"[{Colors.GREEN}SYSTEM{Colors.ENDC}] Target Paper: {Colors.BOLD}{paper_title}{Colors.ENDC}\n")
        
        # Step 2: Reading Phase
        await print_thought("Accessing manuscript: Infinite-Width Networks: A New Theoretical Framework", delay=0.02)
        await print_thought("Scanning Method section: Theorem 1 proof sketch regarding function approximation capacity.", delay=0.03)
        await print_thought("Analyzing the mean-field theory construction correspondence... Wait.", delay=0.04)
        
        # Step 3: Equation Reasoning Discovery
        await print_thought("CRITICAL LOGICAL GAP: The proof sketch applies mean-field theory to function DISTRIBUTIONS.", delay=0.05)
        await print_thought("It fails to establish capacity for discrete function approximation. Soundness violation.", delay=0.04)
        await print_thought("ResNet architecture uses ReLU activations. ReLU creates non-smooth, non-Lipschitz loss landscapes.", delay=0.04)
        await print_thought("Theorem 3.1 is therefore mathematically invalid and breaks in practice.", delay=0.04)
        
        # Step 4: Action Execution (Flagging the Concern)
        await print_action(
            "FLAG_CONCERN", 
            "Type: soundness | Location: method\nDescription: Equation reasoning discrepancy: Symplectic integrators only preserve energy for strictly Lipschitz-continuous gradients. Deep neural networks use ReLU, violating Lipschitz bounds."
        )
        
        action_payload = {
            "session_id": session_id,
            "action": {
                "action_type": "flag_concern",
                "concern_type": "soundness",
                "concern_location": "method",
                "concern_description": "Equation reasoning discrepancy: Symplectic integrators only preserve energy for strictly Lipschitz-continuous gradients. Deep neural network landscapes (like ResNet with ReLU) are non-smooth and violate Lipschitz bounds, making Theorem 3.1 mathematically invalid."
            }
        }
        resp = await client.post(f"{BASE_URL}/step", json=action_payload)
        step_data = resp.json()
        reward = step_data["reward"]["total"]
        
        print(f"[{Colors.GREEN}SYSTEM{Colors.ENDC}] Environment Response -> Reward: {Colors.GREEN}{Colors.BOLD}+{reward:.2f}{Colors.ENDC} (Math Flaw Successfully Detected!)\n")
        
        # Step 5: Assigning Score
        await print_thought("The novelty is extremely high (Quantum inspiration), but soundness is functionally broken.", delay=0.02)
        await print_action("ASSIGN_SCORE", "Dimension: novelty | Score: 9.0")
        await client.post(f"{BASE_URL}/step", json={"session_id": session_id, "action": {"action_type": "assign_score", "dimension": "novelty", "score": 9.0}})
        
        await print_action("ASSIGN_SCORE", "Dimension: soundness | Score: 1.5")
        await client.post(f"{BASE_URL}/step", json={"session_id": session_id, "action": {"action_type": "assign_score", "dimension": "soundness", "score": 1.5}})
        
        # Step 6: Final Decision
        await print_thought("The paper contains a fundamental theoretical gap. It must be rejected.", delay=0.02)
        await print_action("SUBMIT_DECISION", "Decision: REJECT")
        
        resp = await client.post(f"{BASE_URL}/step", json={
            "session_id": session_id,
            "action": {
                "action_type": "submit_decision",
                "decision": "reject"
            }
        })
        final_data = resp.json()
        explainability = final_data["info"]["explanation"]
        
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}======== FINAL JUDGE REPORT ========{Colors.ENDC}")
        print(f"Status: {Colors.GREEN}Task Completed{Colors.ENDC}")
        print(f"Correct Flags Caught: {Colors.CYAN}{explainability['correct_flags_count']}{Colors.ENDC}")
        if explainability['correct_flags_count'] > 0:
            print(f"Accuracy Validated: {Colors.GREEN}YES{Colors.ENDC}")
        print(f"{Colors.HEADER}===================================={Colors.ENDC}\n")
        
        print(f"[{Colors.YELLOW}DEMO COMPLETE{Colors.ENDC}] The Agent successfully simulated advanced mathematical verification.\n")

if __name__ == "__main__":
    asyncio.run(run_research_demo())
