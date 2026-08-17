# UAV Manufacturing Readiness & Scale-up Kit — v0.1

A practical, lightweight, non-sensitive toolkit for assessing whether a working UAV, C-UAS, or autonomous-hardware prototype is ready to move toward repeatable low-rate production and scale-up.

## What it is
The kit is designed for a 20–30 minute founder/manufacturing conversation first, and a deeper follow-up second. It combines lightweight Manufacturing Readiness Level (MRL) thinking, Lean/Lean Six Sigma, DFM/DFA, takt/capacity, quality-control planning, supply-chain risk, standard work, FRACAS-style learning, field repairability, and low-rate production ramp planning.

**It is not a formal MRL assessment, certification audit, airworthiness assessment, weapon-design tool, or export-control determination.**

## Three levels
1. **Level 1 — One-page assessment:** 20 questions, 1–5 scoring, fast red/yellow/green signal.
2. **Level 2 — Spreadsheet model:** detailed questionnaire, readiness dashboard, capacity model, risk register, Kanban, action plan, report shell, and knowledge-base seed.
3. **Level 3 — Lightweight app:** Streamlit app for guided inputs and generated outputs.

## What v0.1 does
- 20-question readiness assessment
- weighted score and MRL-style maturity band
- critical-gate logic
- takt, labor-content, bottleneck and parallel-capacity calculation
- editable process-step model
- lightweight risk register
- deterministic recommended actions
- 10 / 50 / 100-unit breakpoint logic
- generated Markdown report
- JSON assessment export

## Scoring scale
- **1 — Ad hoc:** founder-dependent, undocumented, high risk
- **2 — Partially understood:** some repeatable elements, but unstable
- **3 — Defined:** process exists, but repeatability/evidence is inconsistent
- **4 — Repeatable:** documented and demonstrated for low-rate production
- **5 — Scalable:** controlled, measured, capacity-proven, continuously improved

Default MRL-style mapping:
- **<40:** Prototype Readiness
- **40–54:** Production Concept Defined
- **55–69:** Process Demonstrated
- **70–84:** Low-Rate Production Ready
- **85–100:** Scalable Production Ready

A high overall score does **not** override a critical weakness. Product maturity, capacity, quality, or supply-chain scores at 1–2 trigger an explicit gate review.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Streamlit deployment
Deploy from this GitHub repository using **`app/app.py`** as the app entrypoint. See [`docs/DEPLOY_WEB_APP.md`](docs/DEPLOY_WEB_APP.md).

The event version intentionally has **no login and no persistent backend**. This reduces setup time and minimizes the risk of collecting sensitive company data during a public event.

## Safety scope
Allowed: manufacturing readiness, flow, capacity, quality, supply-chain risk, standard work, tooling, generic maintainability/repairability, production ramp, and non-sensitive lessons learned.

Excluded: weaponization, target selection, payload integration, evasion, offensive operational guidance, sensitive procedures, classified/export-controlled content, and proprietary information.
