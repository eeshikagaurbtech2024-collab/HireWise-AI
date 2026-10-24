# HireWise AI — Agentic Recruitment

## What it demonstrates
HireWise AI is a local, explainable proof of concept for recruitment screening. It uses four cooperating software agents:
1. **Planner Agent** — turns a recruitment request into ordered tasks.
2. **Candidate Analysis Agent** — compares listed skills and experience with job requirements.
3. **Scoring & Ranking Agent** — applies a documented 60/20/20 rubric and ranks candidates.
4. **Critic / Validation Agent** — checks score bounds, duplicate IDs, rank sequence, and required-skill accounting.

This PoC uses deterministic Python functions, not a paid API or an LLM. That makes the workflow reproducible and easy to explain. It still demonstrates planning, tool execution, decision-making, agent collaboration, validation, and a Streamlit interface.

## Requirements
Python 3.10 or newer recommended.

## Run on Windows
1. Extract the ZIP.
2. Open the extracted `HireWise_AI` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
5. Activate it:
   ```bash
   .venv\\Scripts\\activate
   ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. Start the app:
   ```bash
   streamlit run app.py
   ```
8. The app opens in your browser. Change job requirements and click **Run agent workflow**.

## Run tests
```bash
pytest -q
```
Expected: 5 tests pass. Tests cover score bounds, output structure, ranking order, duplicate-ID detection, and missing required skills. If a test fails, fix it before presenting.

## Scoring rubric
- Required skill fit: 60%
- Preferred skill fit: 20%
- Experience fit: 20%
- Formula: `0.60 × required fit + 0.20 × preferred fit + 0.20 × experience fit`
- Each component is between 0 and 100. Experience fit is capped at 100%. This is an illustrative rubric, not a scientifically validated hiring test.

## Files
- `app.py` — Streamlit interface
- `agents.py` — agents and orchestration
- `data/synthetic_candidates.json` — fictional candidate profiles
- `tests/test_agents.py` — automated tests
- `architecture.png` — architecture illustration
- `HireWise_AI_Presentation.pptx` — editable presentation
- `results_and_demo_notes.md` — demo flow and evaluation notes

## Suggested 5-minute demo
1. (30 sec) Explain manual screening and the time-consuming comparison task.
2. (45 sec) Show the job description controls and synthetic profiles.
3. (60 sec) Run the workflow and point out the execution trace.
4. (60 sec) Explain scores, matched/missing skills, and ranking.
5. (45 sec) Show critic validation and the human-reviewed shortlist/export.
6. (40 sec) State limitations, fairness safeguards, and future work.

## Responsible use and limitations
- Synthetic profiles do not demonstrate real-world effectiveness.
- Exact keyword matching misses synonyms and context.
- A score is not proof of job performance or a fair selection decision.
- The Critic validates internal consistency; it cannot prove the rubric is unbiased or job-valid.
- Human review is required. Do not use protected attributes or automatically reject applicants based only on this score.
- A real deployment needs job-analysis validation, accessibility review, privacy/security controls, bias audits, consent and legal review.

## Future scope
- Parse uploaded resumes locally with explicit user consent.
- Add synonym-aware skill extraction and evidence citations.
- Use LangGraph for explicit graph-based orchestration.
- Add audit logs, configurable rubrics, fairness metrics, reviewer feedback, and role-based access.
