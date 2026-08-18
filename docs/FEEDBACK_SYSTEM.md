# Feedback System

The app includes an always-available feedback flow and a lightweight post-assessment usefulness check.

## What is collected

The feedback database is intentionally separated from the manufacturing assessment itself. It stores only product-discovery data such as:

- app version
- anonymous session ID
- assessment stage selected by the user
- optional role
- 1–5 app rating
- feedback category
- free-text feedback
- optional improvement request
- Yes / Partly / No assessment-usefulness response
- product-backlog fields reserved for later AI triage

It does **not** automatically store readiness answers, capacity inputs, process-step data, company names, or technical assessment notes.

## Feedback flow

1. User selects **Give feedback** from the sidebar.
2. User optionally identifies their role and the area of the app they are commenting on.
3. User gives a 1–5 rating, category, comment, and optional improvement suggestion.
4. User confirms that the feedback itself contains no sensitive or proprietary information.
5. The server writes one structured row to Supabase.
6. At the end of the Report tab, the user can also answer **Was this assessment useful? Yes / Partly / No**.

## Supabase setup

1. Create a Supabase project.
2. Open the project's SQL Editor.
3. Run `supabase/feedback_schema.sql` from this repository.
4. In Streamlit Community Cloud, open **App settings → Secrets**.
5. Add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_OR_ANON_KEY"
FEEDBACK_TABLE = "feedback"
```

The SQL enables Row Level Security and grants the public app role **insert only**. Users of the public app cannot read the feedback table through the app credential.

## LLM-ready fields

The schema reserves these fields for a later product-discovery pipeline:

- `ai_theme`
- `ai_priority`
- `ai_summary`
- `ai_recommended_action`
- `status`
- `github_issue_url`

A future batch job can cluster repeated feedback, identify high-frequency themes, summarize evidence, and propose a consolidated GitHub issue. Raw feedback should remain the source evidence; AI-generated fields should be treated as derived analysis.

Recommended future flow:

`Raw feedback → batch LLM triage → recurring themes → human review → selected GitHub issue`

Do not create one GitHub issue per individual feedback row.
