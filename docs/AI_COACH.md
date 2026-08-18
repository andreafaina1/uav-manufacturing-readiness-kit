# Optional AI Coach

The app can optionally use an LLM to synthesize deterministic readiness results, capacity metrics, Lean assessment and short free-text notes.

## Design principle
The LLM is **not** the source of truth for readiness scoring or takt/capacity calculations. Those remain deterministic. AI is limited to:
- summarizing comments
- connecting signals across modules
- ranking likely bottlenecks
- suggesting practical questions/evidence to validate
- explaining Lean and scale-up priorities

## Configuration on Streamlit Community Cloud
Add these values in the app's **Secrets** settings, not in GitHub:

```toml
OPENAI_API_KEY = "..."
AI_ACCESS_CODE = "choose-a-private-event-code"
OPENAI_MODEL = "gpt-5-mini"
```

`AI_ACCESS_CODE` is required so a public app does not expose unlimited use of the owner's API key.

Never commit `.streamlit/secrets.toml` to the repository.

## Data boundary
Only send anonymized, high-level manufacturing information. Do not submit classified, export-controlled, proprietary, mission, payload or security-critical technical details.

The implementation uses the OpenAI Responses API with `store=False`; standard API retention policies may still apply unless the API organization has additional data-retention controls.
