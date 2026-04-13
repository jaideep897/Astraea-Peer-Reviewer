# Astraea Architecture: Scientific Peer Review OS

## 🔗 System Overview
Astraea is a high-fidelity audit environment designed to bridge the gap between static LLM evaluation and professional research peer review.

### 1. The Logic Engine (`AstraeaV3_env`)
- **Deterministic Grader**: Unlike prompt-based graders, Astraea uses a **programmatic consensus engine** that measures the "logical distance" between an agent's flags and a pre-defined expert ground-truth set.
- **Dynamic SII (Scientific Integrity Index)**:
  - Base: 100
  - Decay: -1.5 per step (simulating loss of audit focus).
  - Reward Bonus: +40x total merit (rewards precision over volume).

### 2. The HUD OS (Frontend)
- **Neural Threads**: Visualizes the agent's logical reasoning by drawing SVG paths between linked manuscript sections when a "Deep Scan" (Hint) is performed.
- **Acoustic Feedback**: Uses an FM-synthesis Audio Engine to provide haptic-equivalent feedback for audit successes and system glitches.

### 3. OpenEnv Integration
- **Server-Side**: A FastAPI implementation of the OpenEnv API (`/reset`, `/step`, `/state`).
- **Client-Side**: A Pydantic-reinforced interface for ensuring agent actions follow strict scientific schemas.

## ⚖️ Merit Calibration
To ensure compatibility with automated judges, Astraea calculates:
- **Accuracy**: (Correct Flags / Expert Set Size).
- **Rigorous Scoring**: Accuracy is strictly clamped to `[0.01, 0.99]` to ensure strict compliance with (0, 1) probability constraints.

---
<sub>Astraea Protocol v3.6.0 | Meta PyTorch OpenEnv Submission</sub>
