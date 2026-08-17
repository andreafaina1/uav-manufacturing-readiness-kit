import json
from datetime import date

import pandas as pd
import streamlit as st

from model import DIMENSIONS, QUESTIONS, SAMPLE_STEPS, capacity, dimension_scores, readiness_band, recommendations, signal, weighted_score

st.set_page_config(page_title="UAV Manufacturing Readiness Kit", page_icon="🛠️", layout="wide")

if "responses" not in st.session_state:
    st.session_state.responses = [3] * len(QUESTIONS)
if "steps" not in st.session_state:
    st.session_state.steps = SAMPLE_STEPS.copy()

st.title("UAV Manufacturing Readiness & Scale-up Kit")
st.caption("v0.1 • Prototype → repeatable low-rate production → scale-up")

with st.sidebar:
    st.subheader("Assessment context")
    product = st.text_input("Product / anonymized team", "Anonymous UAV team")
    current = st.number_input("Current units / period", min_value=0, value=10)
    target = st.number_input("Next target units / period", min_value=1, value=50)
    period = st.selectbox("Period", ["month", "week"])
    st.info("Keep event inputs anonymized and non-sensitive. Use only high-level manufacturing and production data.")

assessment_tab, capacity_tab, actions_tab, report_tab, about_tab = st.tabs([
    "1 · Assessment",
    "2 · Capacity",
    "3 · Actions",
    "4 · Report",
    "5 · About",
])

with assessment_tab:
    st.subheader("20-question readiness screen")
    st.write("Use the evidence you actually have. Scores of 4–5 should be supported by repeatable, controlled evidence.")
    responses = [None] * len(QUESTIONS)
    for dim in DIMENSIONS:
        st.markdown(f"### {dim}")
        for i, (question_dim, question) in enumerate(QUESTIONS):
            if question_dim != dim:
                continue
            left, right = st.columns([4, 1])
            with left:
                st.write(question)
            with right:
                responses[i] = st.selectbox(
                    "Score",
                    [1, 2, 3, 4, 5],
                    index=st.session_state.responses[i] - 1,
                    key=f"score_{i}",
                    label_visibility="collapsed",
                )
    st.session_state.responses = responses
    scores = dimension_scores(responses)
    overall = weighted_score(scores)
    c1, c2, c3 = st.columns(3)
    c1.metric("Weighted readiness", f"{overall:.1f}/100")
    c2.metric("MRL-style band", readiness_band(overall))
    c3.metric("Signal", signal(overall, scores))
    score_df = pd.DataFrame({"Dimension": list(scores.keys()), "Score": list(scores.values())}).set_index("Dimension")
    st.bar_chart(score_df, horizontal=True)

with capacity_tab:
    st.subheader("Takt, work content and capacity")
    st.caption("Takt is the demanded production pace. Labor content and station time are modeled separately.")
    a, b, c, d, e = st.columns(5)
    demand = a.number_input("Demand / period", min_value=1, value=int(target))
    days = b.number_input("Productive days", min_value=1, value=20 if period == "month" else 5)
    hours = c.number_input("Productive h/day", min_value=0.5, value=7.0, step=0.5)
    shifts = d.number_input("Shifts/day", min_value=1, value=1)
    operators = e.number_input("Operators", min_value=1, value=3)
    availability = st.slider("Production availability", 0.50, 1.00, 0.90, 0.05)
    st.write("Edit the process steps. Rework rate is entered as a decimal, for example 0.10 = 10%.")
    edited = st.data_editor(st.session_state.steps, num_rows="dynamic", use_container_width=True)
    st.session_state.steps = edited
    cap = capacity(edited, demand, days, hours, shifts, availability, operators)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Target takt", f"{cap['takt']:.1f} min/unit")
    k2.metric("Labor content", f"{cap['labor']:.1f} min/unit")
    k3.metric("Bottleneck", cap["bottleneck"] or "—")
    k4.metric("Labor-limited output", f"{cap['labor_output']:.1f} units/{period}")
    display = cap["df"].copy()
    display["Over takt?"] = display["Effective min"] > cap["takt"]
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.bar_chart(cap["df"].set_index("Step")[["Effective min"]], horizontal=True)

with actions_tab:
    scores = dimension_scores(st.session_state.responses)
    cap = capacity(st.session_state.steps, target, 20 if period == "month" else 5, 7, 1, 0.90, 3)
    actions = recommendations(scores, cap)
    st.subheader("Recommended actions")
    if actions:
        st.dataframe(pd.DataFrame(actions, columns=["Topic", "Recommended action"]), use_container_width=True, hide_index=True)
    else:
        st.success("No automatic red-flag recommendation triggered. Validate the assessment with evidence.")
    st.markdown("### Suggested Kanban flow")
    st.write("Intake / Observed Issue → Clarify Requirement → Analyze Root Cause → Design Countermeasure → Implement Standard → Validate in Build → Update SOP / Training → Monitor in Production")

with report_tab:
    scores = dimension_scores(st.session_state.responses)
    overall = weighted_score(scores)
    cap = capacity(st.session_state.steps, target, 20 if period == "month" else 5, 7, 1, 0.90, 3)
    actions = recommendations(scores, cap)
    score_rows = "\n".join(f"| {d} | {scores[d]:.1f}/5 |" for d in DIMENSIONS)
    action_rows = "\n".join(f"- **{topic}:** {action}" for topic, action in actions) or "- Validate the current assessment with objective build evidence."
    top_steps = cap["df"].sort_values("Effective min", ascending=False).head(5)
    bottlenecks = "\n".join(f"{i+1}. {r['Step']} — {r['Effective min']:.1f} min/unit" for i, (_, r) in enumerate(top_steps.iterrows()))
    report = f"""# UAV Manufacturing Readiness Report

**Product/team:** {product}  
**Date:** {date.today().isoformat()}  
**Current rate:** {current} units/{period}  
**Next target:** {target} units/{period}

## Executive summary
Readiness is **{overall:.1f}/100 — {readiness_band(overall)} — {signal(overall, scores)}**.

## Score by dimension
| Dimension | Score |
|---|---:|
{score_rows}

## Takt / capacity
- Available production time: **{cap['available']:.0f} min/{period}**
- Target takt: **{cap['takt']:.1f} min/unit**
- Modeled labor content: **{cap['labor']:.1f} min/unit**
- Bottleneck: **{cap['bottleneck']} — {cap['bottleneck_time']:.1f} min/unit**
- Labor-limited output: **{cap['labor_output']:.1f} units/{period}**
- Approximate operators required: **{cap['required_operators']}**

## Top bottlenecks
{bottlenecks}

## Recommended actions
{action_rows}

## Scale-up view
- **~10 units:** prove repeatability, configuration control and technician-independent builds.
- **~50 units:** expect labor content, station imbalance, supplier capacity, training, tooling and rework to become explicit constraints.
- **~100 units:** expect material flow, supplier quality, WIP control, traceability, test capacity and supervisory bandwidth to require a managed production system.

## Recommended next workshop
Run a 90-minute next-rate production-cell review using measured build times, top defects, tooling gaps and supplier assumptions.

---
This is a lightweight operational readiness screen, not a formal certification or compliance assessment. Keep inputs non-sensitive.
"""
    st.markdown(report)
    st.download_button("Download report (.md)", report, file_name="uav_manufacturing_readiness_report.md", mime="text/markdown", use_container_width=True)
    payload = json.dumps({"product": product, "current_rate": current, "target_rate": target, "period": period, "dimension_scores": scores, "overall": overall, "band": readiness_band(overall)}, indent=2)
    st.download_button("Download assessment data (.json)", payload, file_name="uav_manufacturing_readiness_assessment.json", mime="application/json", use_container_width=True)

with about_tab:
    st.subheader("Method and guardrails")
    st.markdown("""
**Purpose:** fast, evidence-oriented manufacturing-readiness screening for prototype → low-rate production → scale-up.

**Methods combined:** MRL-style maturity logic, Lean/VSM, DFM/DFA, takt and line balancing, standard work, simplified risk logic, quality control planning, failure-feedback loops, supply-chain risk, maintainability and ramp planning.

The app is intended for high-level, non-sensitive manufacturing assessment and does not replace formal certification, quality-system, regulatory or compliance reviews.
""")
