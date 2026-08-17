# Deploy the Web App

## Fastest path — Streamlit Community Cloud

1. Open Streamlit Community Cloud.
2. Create a new app from GitHub.
3. Select repository `andreafaina1/uav-manufacturing-readiness-kit`.
4. Select branch `main`.
5. Set the entrypoint to `app/app.py`.
6. Deploy and share the generated `*.streamlit.app` URL.

The v0.1 app has no login and no persistent database by design.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py
```

## v0.1 capability
- 20-question readiness assessment
- weighted readiness score and MRL-style band
- critical-gate logic
- takt and capacity model
- editable process-step table
- bottleneck and parallel-capacity detection
- deterministic recommended actions
- 10 / 50 / 100-unit scale-up framing
- Markdown report export
- JSON assessment export

## Recommended v0.2
Add saved assessments only after validating the workflow with real users. A sensible next stack is Streamlit or a polished React/Lovable UI plus Supabase/Postgres for authentication, persistence, assessment history, action tracking and source-backed recommendations.
