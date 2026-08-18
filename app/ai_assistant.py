import json
import os


def _openai_client(api_key):
    from openai import OpenAI
    return OpenAI(api_key=api_key)


def get_ai_config(secrets):
    api_key = secrets.get("OPENAI_API_KEY") if secrets else None
    access_code = secrets.get("AI_ACCESS_CODE") if secrets else None
    model = secrets.get("OPENAI_MODEL", "gpt-5-mini") if secrets else "gpt-5-mini"
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    access_code = access_code or os.getenv("AI_ACCESS_CODE")
    model = os.getenv("OPENAI_MODEL", model)
    return {"api_key": api_key, "access_code": access_code, "model": model}


def _context_text(context):
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)


def synthesize(context, api_key, model="gpt-5-mini"):
    client = _openai_client(api_key)
    prompt = f"""
You are a manufacturing-readiness coach supporting an early-stage autonomous-hardware team.
Use ONLY the anonymized, high-level manufacturing information below. Do not infer or request sensitive, classified, proprietary, export-controlled, or security-critical technical details.
Treat free-text notes as unverified observations, not facts. Separate evidence from assumptions.

Produce concise Markdown with exactly these headings:
## Executive synthesis
## Top bottlenecks
## Lean / production-system risks
## 30-day priorities
## Evidence gaps to validate

For bottlenecks, combine quantitative capacity evidence, readiness scores, Lean/waste findings, and notes. Rank no more than five items and explain why each matters to the next production rate. Prefer specific operational countermeasures over generic advice.

ASSESSMENT CONTEXT:
{_context_text(context)}
"""
    response = client.responses.create(model=model, input=prompt, store=False)
    return response.output_text


def answer_question(context, question, api_key, model="gpt-5-mini"):
    client = _openai_client(api_key)
    prompt = f"""
You are a manufacturing-readiness coach. Answer the user's question using ONLY the anonymized assessment context below.
Stay within manufacturing readiness, Lean production systems, flow, takt/capacity, quality, tooling, supply chain, standard work, maintainability and scale-up planning.
Do not ask for or infer sensitive, classified, proprietary, export-controlled, mission, payload or operational details.
If evidence is insufficient, say what evidence would be needed.
Be concise and practical.

ASSESSMENT CONTEXT:
{_context_text(context)}

USER QUESTION:
{question}
"""
    response = client.responses.create(model=model, input=prompt, store=False)
    return response.output_text
