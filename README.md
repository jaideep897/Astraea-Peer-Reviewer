<div align="center">

# 🔬 Scientific Peer Review · OpenEnv Certified
## **ASTRAEA: Peer Review OS**
**An RL-ready environment where AI agents act as Senior Research Auditors — detecting logical flaws, statistical inconsistencies, and PyTorch implementation bugs in scientific manuscripts.**

[![OpenEnv Certified](https://img.shields.io/badge/OpenEnv-Certified-brightgreen?style=for-the-badge)](https://github.com/OpenEnv)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c?style=for-the-badge&logo=pytorch)](https://pytorch.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ed?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 01 | Introduction
Peer review is the gatekeeper of scientific integrity — yet it is routinely undermined by human bias, incomplete scrutiny, and oversight. **ASTRAEA** (Automated Scientific Tracking & Research Evaluation Assistant) provides a high-fidelity simulation where AI auditors perform deep-logic scans of research papers and PyTorch code, going far beyond surface summarization.

Agents must identify evidence-based discrepancies including:
*   **Gradient Flow Errors:** Missing `zero_grad()`, improper backward passes.
*   **Statistical Inconsistencies:** Missing baselines, mismatched results.
*   **Data Leakage:** Hyperparameter tuning performed on test sets.

---

## 02 | Core Features

### ⚖️ **Scoring: Dynamic Metric System**
Cumulative reputation on the Dashboard; judge scores clamped to (0.01, 0.99) for zero boundary errors in eval scripts.

### 🧠 **Reasoning: Neural Thread Visualization**
Deep Scan maps line-of-reasoning paths between manuscript sections where internal contradictions exist.

### 🛡️ **Integrity: Scientific Integrity Index (SII)**
Real-time SII rewards precision flagging; unmerited guesswork causes score decay, mirroring real reviewer accountability.

### 🏆 **Grading: Deterministic Expert Grader**
All audit actions evaluated against ground-truth expert consensus with partial reward signals for precision.

---

## 03 | Audit Lifecycle
Astraea simulates the professional workflow of an ICLR/NeurIPS reviewer across five deterministic stages.

1.  **Neural Initialization:** The Auditor OS boots, detects available compute resources, and syncs state with the OpenEnv server.
2.  **Multidimensional Scanning:** Agent analyzes manuscript sections independently — Abstract, Introduction, Method, Results, and Conclusion.
3.  **Active Logic Flagging:** Every flagged concern is evaluated in real time against a deterministic expert consensus (ground truth).
4.  **Scientific Integrity Index (SII):** Precision rewards accumulate; unmerited steps cause integrity decay — mirroring the cost of false positives in real review.
5.  **Final Verdict:** Agent submits Accept, Reject, or Major Revision — graded for strategic alignment with expert consensus.

---

## 04 | Audit Levels

| Level | Name | Focus | Description |
| :--- | :--- | :--- | :--- |
| **task1** | **Baseline** | Audit Warmup | Initial audit warm-up — formatting checks and data clarity issues. |
| **task2** | **Soundness** | Logic & Leakage | Logic flaw detection, data leakage scan, and missing baseline identification. |
| **task3** | **Calibration**| Score Calibration | Merit score alignment with expert peer-reviewer consensus. |
| **task4** | **Rigor** | PyTorch Rigor | Deep audit of implementation and gradient logic bugs. |
| **task5** | **Global** | Full Audit | End-to-end review of an adversarial research manuscript. |

---

## 05 | Usage

### 1. Configure Environment
```bash
cp .env.example .env # fill in OPENAI_API_KEY and port config
```

### 2. Launch the Auditor Dashboard
```bash
python app.py # → http://localhost:7860/dashboard
```

### 3. Run Task Evaluation
```bash
python inference.py task1 # single task
python inference.py all   # full benchmark sweep
```

### 4. Run Scripted Demo
```bash
python demo.py # logic-linking walkthrough
```

### 5. Docker Deployment
```bash
docker-compose up --build
```

---

## 06 | Project Structure
```text
Astraea-Peer-Reviewer/
├── AstraeaV3_env/      # Core logic & audit environments
├── assets/             # Experimental logs & audit evidence
├── docs/               # Technical specifications & guidelines
├── Dockerfile          # Containerization & deployment
├── run.py              # Mission control: core startup
└── inference.py        # Independent evaluation engine
```

---

## 07 | Contributing
Contributions from the scientific AI community are welcome. Please follow the steps below to keep audit logic clean and reviewable.

1.  **Fork the repository:** Create your own copy to work from independently.
2.  **Create a feature branch:** Use descriptive names tied to the audit logic you're adding.
3.  **Commit with clarity:** Each commit should describe the logic change, not just the file.
4.  **Open a pull request:** Submit for review with a summary of what the change audits or fixes.

---

<div align="center">

**This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.**

### Thank you for your interest in ASTRAEA
*Let's advance scientific peer review together.*

**ASTRAEA Research Protocol**
MIT License | Docker · PyTorch 2.0+

</div>
