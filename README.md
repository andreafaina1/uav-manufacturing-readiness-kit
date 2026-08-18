# UAV Manufacturing Readiness & Scale-up Kit — v0.1.2

A practical, lightweight, non-sensitive toolkit for assessing whether a working UAV, C-UAS, or autonomous-hardware prototype is ready to move toward repeatable low-rate production and scale-up.

**Live app:** https://uav-manufacturing-readiness-kit-4ahgiybzgvmbtrgfrkfruh.streamlit.app/

## What it does

The kit combines lightweight Manufacturing Readiness Level thinking with Lean / Lean Six Sigma, DFM/DFA, takt and capacity analysis, quality-control planning, supply-chain risk, standard work, field repairability and scale-up planning.

Current app flow:

1. **Assessment** — 20-question readiness screen with evidence notes.
2. **Capacity** — takt, labor content, bottlenecks and parallelization.
3. **Lean cell** — 6S + Security, 10-lens waste walk and Minimum Viable Production System checks.
4. **AI coach** — optional synthesis of deterministic results and anonymized observations.
5. **Actions** — prioritized manufacturing and Lean countermeasures.
6. **Report** — Markdown and JSON export.
7. **Feedback** — structured user feedback and post-assessment usefulness signal.

The deterministic engine remains the source of truth for scoring and capacity math. AI is an optional interpretation layer.

## Feedback and product discovery

The sidebar includes **Give feedback**, available throughout the app. Users can provide:

- optional role
- assessment area
- 1–5 rating
- feedback category
- free-text comment
- improvement suggestion

The Report tab also asks **Was this assessment useful? Yes / Partly / No**.

Feedback is stored separately from assessment data. The feedback database does **not** automatically receive readiness answers, process-step data, capacity inputs or technical notes.

See [`docs/FEEDBACK_SYSTEM.md`](docs/FEEDBACK_SYSTEM.md) and [`supabase/feedback_schema.sql`](supabase/feedback_schema.sql).

## Documentation

- [Assessment questionnaire](docs/ASSESSMENT_QUESTIONNAIRE.md)
- [Lean Production System](docs/LEAN_PRODUCTION_SYSTEM.md)
- [AI Coach](docs/AI_COACH.md)
- [Feedback system](docs/FEEDBACK_SYSTEM.md)
- [Safety and data boundaries](docs/SAFETY.md)
- [Streamlit deployment](docs/DEPLOY_WEB_APP.md)

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

A high overall score does **not** override a critical weakness. Product maturity, capacity, quality or supply-chain scores at 1–2 trigger an explicit gate review.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Configuration

Optional AI features use Streamlit Secrets. Feedback collection uses Supabase and is enabled after adding the following Streamlit Secrets:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_OR_ANON_KEY"
FEEDBACK_TABLE = "feedback"
```

Run `supabase/feedback_schema.sql` once in the Supabase SQL Editor before enabling feedback collection.

## Safety scope

Allowed: manufacturing readiness, flow, capacity, quality, supply-chain risk, standard work, tooling, generic maintainability/repairability, production ramp and non-sensitive lessons learned.

Excluded: sensitive or proprietary technical details and any classified/export-controlled content. The tool is not a formal MRL certification, airworthiness assessment, quality-system audit or regulatory/compliance determination.
