import json
from datetime import date

import pandas as pd
import streamlit as st

from ai_assistant import answer_question, get_ai_config, synthesize
from lean import MVPS_GATES, SIX_S, WASTE_LENSES, lean_actions, lean_readiness, top_wastes
from model import DIMENSIONS, QUESTIONS, SAMPLE_STEPS, capacity, dimension_scores, readiness_band, recommendations, signal, weighted_score

st.set_page_config(page_title="UAV Manufacturing Readiness Kit", page_icon="🛠️", layout="wide")

if "responses" not in st.session_state:
    st.session_state.responses = [3] * len(QUESTIONS)
if "dimension_notes" not in st.session_state:
    st.session_state.dimension_notes = {dim: "" for dim in DIMENSIONS}
if "steps" not in st.session_state:
    st.session_state.steps = SAMPLE_STEPS.copy()
if "capacity_inputs" not in st.session_state:
    st.session_state.capacity_inputs = {"demand": 50, "days": 20, "hours": 7.0, "shifts": 1, "operators": 3, "availability": 0.90}
if "six_s_scores" not in st.session_state:
    st.session_state.six_s_scores = {name: 3 for name in SIX_S}
if "waste_scores" not in st.session_state:
    st.session_state.waste_scores = {name: 0 for name in WASTE_LENSES}
if "mvps_scores" not in st.session_state:
    st.session_state.mvps_scores = {name: 3 for name in MVPS_GATES}
if "lean_notes" not in st.session_state:
    st.session_state.lean_notes = ""
if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = ""
if "ai_chat" not in st.session_state:
    st.session_state.ai_chat = []

st.title("Manufacturing Scale-up Preflight")
st.caption("UAV Manufacturing Readiness & Scale-up Kit · v0.1.1 · prototype → repeatable batches → scalable production")
st.markdown("**What breaks first when you move from a working prototype toward 10, 50 or 100 units?**")

with st.expander("See the assessment flow before you start", expanded=True):
    st.graphviz_chart(
        """
        digraph {
          rankdir=LR;
          node [shape=box, style="rounded"];
          context [label="1. Context & target rate"];
          assess [label="2. 20-question readiness screen"];
          gate [label="Critical gate?", shape=diamond];
          capacity [label="3. Takt / capacity / bottlenecks"];
          over [label="Step over takt?", shape=diamond];
          lean [label="4. Lean cell & MVPS check"];
          synth [label="5. Synthesize priorities"];
          report [label="6. 30/60/90 actions & report"];
          stabilize [label="Stabilize product / quality / supply basics"];
          rebalance [label="Reduce / split / fixture / parallelize"];
          context -> assess -> gate;
          gate -> stabilize [label="yes"];
          gate -> capacity [label="no / after containment"];
          stabilize -> capacity;
          capacity -> over;
          over -> rebalance [label="yes"];
          over -> lean [label="no"];
          rebalance -> lean;
          lean -> synth -> report;
        }
        """,
        width="stretch",
    )
    st.caption("AI synthesis is optional. The deterministic assessment, capacity model, Lean checks and report work without an AI key.")

with st.sidebar:
    st.subheader("Assessment context")
    product = st.text_input("Product / anonymized team", "Anonymous UAV team")
    current = st.number_input("Current units / period", min_value=0, value=10)
    target = st.number_input("Next target units / period", min_value=1, value=50)
    period = st.selectbox("Period", ["month", "week"])
    st.info("Use anonymized, high-level production information only. Do not enter sensitive, classified, export-controlled or proprietary technical details.")

assessment_tab, capacity_tab, lean_tab, ai_tab, actions_tab, report_tab, about_tab = st.tabs([
    "1 · Assessment", "2 · Capacity", "3 · Lean cell", "4 · AI coach", "5 · Actions", "6 · Report", "7 · About"
])

with assessment_tab:
    st.subheader("20-question readiness screen")
    st.write("Score the evidence you actually have. Add short notes only where they help explain a constraint, assumption or missing proof.")
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
                responses[i] = st.selectbox("Score", [1, 2, 3, 4, 5], index=st.session_state.responses[i] - 1, key=f"score_{i}", label_visibility="collapsed")
        st.session_state.dimension_notes[dim] = st.text_area(
            "Optional evidence / observation",
            value=st.session_state.dimension_notes.get(dim, ""),
            key=f"note_{dim}",
            height=70,
            placeholder="Example: wiring still depends on one technician; second supplier not yet qualified.",
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
    defaults = st.session_state.capacity_inputs
    a, b, c, d, e = st.columns(5)
    demand = a.number_input("Demand / period", min_value=1, value=int(defaults.get("demand", target)), key="cap_demand")
    days = b.number_input("Productive days", min_value=1, value=int(defaults.get("days", 20 if period == "month" else 5)), key="cap_days")
    hours = c.number_input("Productive h/day", min_value=0.5, value=float(defaults.get("hours", 7.0)), step=0.5, key="cap_hours")
    shifts = d.number_input("Shifts/day", min_value=1, value=int(defaults.get("shifts", 1)), key="cap_shifts")
    operators = e.number_input("Operators", min_value=1, value=int(defaults.get("operators", 3)), key="cap_operators")
    availability = st.slider("Production availability", 0.50, 1.00, float(defaults.get("availability", 0.90)), 0.05, key="cap_availability")
    st.session_state.capacity_inputs = {"demand": demand, "days": days, "hours": hours, "shifts": shifts, "operators": operators, "availability": availability}
    st.write("Edit the process steps. Rework rate is a decimal, for example 0.10 = 10%.")
    edited = st.data_editor(st.session_state.steps, num_rows="dynamic", use_container_width=True, key="process_steps")
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

with lean_tab:
    st.subheader("Lean Production System Starter")
    st.write("Design one excellent minimum viable production cell before scaling a weak process. This module uses **6S + Security**, a **10-lens waste walk**, and a **Minimum Viable Production System (MVPS)** check.")

    st.markdown("### 6S + Security")
    six_cols = st.columns(2)
    for idx, (name, description) in enumerate(SIX_S.items()):
        with six_cols[idx % 2]:
            st.caption(description)
            st.session_state.six_s_scores[name] = st.slider(name, 1, 5, st.session_state.six_s_scores[name], key=f"sixs_{name}")

    st.markdown("### 10-lens waste walk")
    st.caption("The first eight are the common DOWNTIME Lean wastes. Safety/ergonomics and information/configuration loss are explicit extensions for hardware scale-up. Severity: 0 none, 1 low, 2 medium, 3 high.")
    waste_cols = st.columns(2)
    for idx, (name, description) in enumerate(WASTE_LENSES.items()):
        with waste_cols[idx % 2]:
            st.caption(description)
            st.session_state.waste_scores[name] = st.select_slider(name, options=[0, 1, 2, 3], value=st.session_state.waste_scores[name], format_func=lambda x: ["0 · none", "1 · low", "2 · medium", "3 · high"][x], key=f"waste_{name}")

    st.markdown("### Minimum Viable Production System")
    mvps_cols = st.columns(2)
    for idx, (name, description) in enumerate(MVPS_GATES.items()):
        with mvps_cols[idx % 2]:
            st.caption(description)
            st.session_state.mvps_scores[name] = st.slider(name, 1, 5, st.session_state.mvps_scores[name], key=f"mvps_{name}")

    st.session_state.lean_notes = st.text_area("Lean-cell observations", value=st.session_state.lean_notes, height=90, placeholder="Example: tools shared across benches; test queue forms after integration; no fixed WIP limit before final test.")
    lean_result = lean_readiness(st.session_state.six_s_scores, st.session_state.waste_scores, st.session_state.mvps_scores)
    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Lean cell readiness", f"{lean_result['overall']:.0f}/100")
    l2.metric("6S + Security", f"{lean_result['six_s']:.0f}/100")
    l3.metric("Waste control", f"{lean_result['waste']:.0f}/100")
    l4.metric("MVPS", f"{lean_result['mvps']:.0f}/100")
    wastes = top_wastes(st.session_state.waste_scores)
    if wastes:
        st.markdown("**Highest waste lenses:** " + ", ".join(f"{name} ({severity}/3)" for name, severity in wastes))
    lean_recs = lean_actions(st.session_state.six_s_scores, st.session_state.waste_scores, st.session_state.mvps_scores)
    if lean_recs:
        st.dataframe(pd.DataFrame(lean_recs, columns=["Lean topic", "Suggested countermeasure"]), use_container_width=True, hide_index=True)
    with st.expander("Cell setup guide: first batches with scale in mind"):
        st.markdown("""
1. **Map one-direction flow:** Kit → Prepare → Assemble → Integrate → Configure → Inspect → Test → Release.
2. **Create point-of-use work:** recurring tools, consumables and parts have visible homes close to the task.
3. **Pre-kit the batch:** expose shortages before assembly starts rather than during the build.
4. **Define standard work:** expected sequence, cycle time, standard WIP and acceptance evidence.
5. **Limit WIP:** use FIFO and explicit maximum buffers between major steps.
6. **Build quality at source:** place checks and error-proofing where defects originate, not only at final inspection.
7. **Visualize plan vs actual:** use a lightweight SQDCP board for Safety, Quality, Delivery, Cost and People/Problems.
8. **Close the loop:** defects, shortages and recurring delays become owned improvement actions with validation dates.
""")


def current_context():
    scores = dimension_scores(st.session_state.responses)
    overall = weighted_score(scores)
    ci = st.session_state.capacity_inputs
    cap = capacity(st.session_state.steps, ci["demand"], ci["days"], ci["hours"], ci["shifts"], ci["availability"], ci["operators"])
    lean_result = lean_readiness(st.session_state.six_s_scores, st.session_state.waste_scores, st.session_state.mvps_scores)
    return {
        "product": product,
        "current_rate": current,
        "target_rate": target,
        "period": period,
        "readiness": {"overall": round(overall, 1), "band": readiness_band(overall), "signal": signal(overall, scores), "dimension_scores": scores, "dimension_notes": st.session_state.dimension_notes},
        "capacity": {
            "inputs": ci,
            "takt_min_per_unit": round(cap["takt"], 1),
            "labor_content_min_per_unit": round(cap["labor"], 1),
            "bottleneck": cap["bottleneck"],
            "bottleneck_time_min": round(cap["bottleneck_time"], 1),
            "labor_limited_output": round(cap["labor_output"], 1),
            "required_operators": cap["required_operators"],
            "steps_over_takt": cap["df"][cap["df"]["Effective min"] > cap["takt"]][["Step", "Effective min"]].to_dict("records"),
        },
        "lean": {"scores": {k: round(v, 1) for k, v in lean_result.items()}, "six_s_security": st.session_state.six_s_scores, "waste_severity": st.session_state.waste_scores, "mvps": st.session_state.mvps_scores, "notes": st.session_state.lean_notes},
    }

with ai_tab:
    st.subheader("Optional AI synthesis & coach")
    st.write("The deterministic model remains the source for scores and capacity math. AI is used only to **aggregate notes, connect signals and explain likely bottlenecks** in concise language.")
    st.warning("Only use anonymized, non-sensitive information. If enabled, the assessment context is sent to an external LLM API for processing.")
    try:
        ai_config = get_ai_config(st.secrets)
    except Exception:
        ai_config = get_ai_config({})
    if not ai_config["api_key"]:
        st.info("AI is not configured yet. Add OPENAI_API_KEY and AI_ACCESS_CODE to Streamlit Secrets to enable this tab. The rest of the app is fully functional without AI.")
    elif not ai_config["access_code"]:
        st.info("An API key is present, but AI is intentionally disabled until an AI_ACCESS_CODE is also configured to protect a public deployment from open API usage.")
    else:
        access = st.text_input("AI access code", type="password")
        consent = st.checkbox("I confirm the inputs are anonymized, non-sensitive and appropriate to send to the configured AI service.")
        unlocked = access == ai_config["access_code"] and consent
        if unlocked:
            context = current_context()
            if st.button("Generate AI synthesis", type="primary", use_container_width=True):
                with st.spinner("Synthesizing readiness, capacity, Lean and notes..."):
                    try:
                        st.session_state.ai_summary = synthesize(context, ai_config["api_key"], ai_config["model"])
                    except Exception as exc:
                        st.error(f"AI request failed: {exc}")
            if st.session_state.ai_summary:
                st.markdown(st.session_state.ai_summary)
            st.markdown("### Ask the manufacturing coach")
            for item in st.session_state.ai_chat:
                with st.chat_message(item["role"]):
                    st.markdown(item["content"])
            question = st.chat_input("Ask about bottlenecks, Lean priorities, evidence gaps or the next-rate production system")
            if question:
                st.session_state.ai_chat.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing the current assessment..."):
                        try:
                            answer = answer_question(context, question, ai_config["api_key"], ai_config["model"])
                        except Exception as exc:
                            answer = f"AI request failed: {exc}"
                        st.markdown(answer)
                st.session_state.ai_chat.append({"role": "assistant", "content": answer})

with actions_tab:
    context = current_context()
    scores = context["readiness"]["dimension_scores"]
    ci = st.session_state.capacity_inputs
    cap = capacity(st.session_state.steps, ci["demand"], ci["days"], ci["hours"], ci["shifts"], ci["availability"], ci["operators"])
    actions = recommendations(scores, cap)
    lean_recs = lean_actions(st.session_state.six_s_scores, st.session_state.waste_scores, st.session_state.mvps_scores)
    combined = actions + [(f"Lean · {topic}", action) for topic, action in lean_recs]
    st.subheader("Recommended actions")
    if combined:
        st.dataframe(pd.DataFrame(combined[:12], columns=["Topic", "Recommended action"]), use_container_width=True, hide_index=True)
    else:
        st.success("No automatic red-flag recommendation triggered. Validate the assessment with objective build evidence.")
    st.markdown("### Suggested improvement Kanban")
    st.write("Observed issue → Clarify requirement → Root cause → Countermeasure → Implement standard → Validate in build → Update SOP/training → Monitor")
    st.markdown("### Daily / weekly visual management")
    st.write("Use a lightweight **SQDCP** review: Safety · Quality · Delivery · Cost · People/Problems. Keep plan-vs-actual, top blockers and action owners visible.")

with report_tab:
    context = current_context()
    scores = context["readiness"]["dimension_scores"]
    overall = context["readiness"]["overall"]
    ci = st.session_state.capacity_inputs
    cap = capacity(st.session_state.steps, ci["demand"], ci["days"], ci["hours"], ci["shifts"], ci["availability"], ci["operators"])
    actions = recommendations(scores, cap)
    lean_recs = lean_actions(st.session_state.six_s_scores, st.session_state.waste_scores, st.session_state.mvps_scores)
    lean_result = lean_readiness(st.session_state.six_s_scores, st.session_state.waste_scores, st.session_state.mvps_scores)
    score_rows = "\n".join(f"| {d} | {scores[d]:.1f}/5 |" for d in DIMENSIONS)
    action_rows = "\n".join(f"- **{topic}:** {action}" for topic, action in (actions + [(f"Lean · {t}", a) for t, a in lean_recs])[:12]) or "- Validate the current assessment with objective build evidence."
    top_steps = cap["df"].sort_values("Effective min", ascending=False).head(5)
    bottlenecks = "\n".join(f"{i+1}. {r['Step']} — {r['Effective min']:.1f} min/unit" for i, (_, r) in enumerate(top_steps.iterrows()))
    wastes = top_wastes(st.session_state.waste_scores)
    waste_rows = "\n".join(f"- {name}: severity {severity}/3" for name, severity in wastes) or "- No Lean waste lens rated above zero."
    report = f"""# UAV Manufacturing Readiness Report

**Product/team:** {product}  
**Date:** {date.today().isoformat()}  
**Current rate:** {current} units/{period}  
**Next target:** {target} units/{period}

## Executive summary
Readiness is **{overall:.1f}/100 — {readiness_band(overall)} — {signal(overall, scores)}**.  
Lean cell readiness is **{lean_result['overall']:.0f}/100**.

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

## Lean Production System Starter
- 6S + Security: **{lean_result['six_s']:.0f}/100**
- Waste control: **{lean_result['waste']:.0f}/100**
- Minimum Viable Production System: **{lean_result['mvps']:.0f}/100**

### Highest waste lenses
{waste_rows}

## Recommended actions
{action_rows}

## Scale-up view
- **~10 units:** prove repeatability, configuration control and technician-independent builds.
- **~50 units:** make takt, WIP, line balance, supplier capacity, training, fixtures and defect control explicit.
- **~100 units:** operate a managed production system with material flow, visual management, traceability, test capacity and cross-trained staffing.

## Recommended next workshop
Run a 90-minute next-rate production-cell review using measured build times, top defects, 6S/waste observations, tooling gaps and supplier assumptions.

---
This is a lightweight operational readiness screen, not a formal certification or compliance assessment. Keep inputs anonymized and non-sensitive.
"""
    st.markdown(report)
    if st.session_state.ai_summary:
        with st.expander("AI synthesis generated in this session"):
            st.markdown(st.session_state.ai_summary)
    st.download_button("Download report (.md)", report, file_name="uav_manufacturing_readiness_report.md", mime="text/markdown", use_container_width=True)
    payload = json.dumps(context, indent=2, default=str)
    st.download_button("Download assessment data (.json)", payload, file_name="uav_manufacturing_readiness_assessment.json", mime="application/json", use_container_width=True)

with about_tab:
    st.subheader("Method and guardrails")
    st.markdown("""
**Purpose:** fast, evidence-oriented manufacturing-readiness screening for prototype → low-rate production → scale-up.

**Methods combined:** MRL-style maturity logic, Lean/VSM, 6S, waste identification, DFM/DFA, takt and line balancing, standard work, WIP control, quality at source, visual management, simplified risk logic, supply-chain risk, maintainability and ramp planning.

**Lean terminology:** the app uses the common eight DOWNTIME wastes and adds two explicit hardware-scale-up lenses: safety/ergonomics exposure and information/configuration loss. These two are extensions, not claimed as universally canonical Lean wastes.

**AI role:** AI never determines the numeric score or capacity math. It is an optional synthesis layer for comments and existing metrics. The app works without AI.

The app does not replace formal certification, quality-system, regulatory, EHS, information-security or compliance reviews.
""")
