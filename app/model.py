import math

import pandas as pd

DIMENSIONS = {
    "Product maturity": 12,
    "DFM/DFA maturity": 12,
    "Assembly readiness": 10,
    "Takt/capacity readiness": 12,
    "Quality readiness": 12,
    "Supply chain readiness": 12,
    "Tooling readiness": 8,
    "Documentation readiness": 10,
    "Field repairability": 6,
    "Scale-up readiness": 6,
}

CRITICAL = {
    "Product maturity",
    "Takt/capacity readiness",
    "Quality readiness",
    "Supply chain readiness",
}

QUESTIONS = [
    ("Product maturity", "Is the product architecture stable enough that the next 3–5 builds should use the same baseline?"),
    ("Product maturity", "Is the BOM controlled, with critical parts and constraints visible?"),
    ("DFM/DFA maturity", "Can a technician build the product without founder-only tricks or undocumented judgment?"),
    ("DFM/DFA maturity", "Are variants, fasteners, connectors, wiring practices and interfaces standardized where practical?"),
    ("Assembly readiness", "Is the end-to-end build sequence defined and measured by step?"),
    ("Assembly readiness", "Are bottlenecks, WIP, handoffs and rework loops visible?"),
    ("Takt/capacity readiness", "Is target demand translated into takt and compared with effective cycle time?"),
    ("Takt/capacity readiness", "Is labor content known well enough to estimate staffing and parallelization needs?"),
    ("Quality readiness", "Are CTQs, acceptance criteria, inspection/test points and release criteria documented?"),
    ("Quality readiness", "Are defects and field failures logged and closed through corrective action?"),
    ("Supply chain readiness", "Are single-source, long-lead, custom, constrained and unqualified items explicit?"),
    ("Supply chain readiness", "Are second-source, substitution, make/buy and supplier-capacity actions defined for top risks?"),
    ("Tooling readiness", "Are jigs, fixtures, calibrated tools and production test equipment identified?"),
    ("Tooling readiness", "Is a minimum viable production cell defined for the current and next rate?"),
    ("Documentation readiness", "Could a new technician build and inspect a unit from controlled documentation?"),
    ("Documentation readiness", "Are configuration changes, training, deviations and SOP updates traceable?"),
    ("Field repairability", "Are likely replacement items, repair time, tools, spares and repair-vs-replace logic understood?"),
    ("Field repairability", "Does field feedback return to engineering/manufacturing and drive controlled changes?"),
    ("Scale-up readiness", "Has the team identified what changes at 10, 50 and 100 units?"),
    ("Scale-up readiness", "Is there a 30/60/90-day readiness plan with owners and evidence-based exit criteria?"),
]

SAMPLE_STEPS = pd.DataFrame(
    [
        ["Mechanical preparation", 160, 0, 0, 0, 0.08, 35],
        ["Airframe assembly", 210, 0, 0, 0, 0.08, 35],
        ["Wiring / harness", 250, 0, 0, 0, 0.12, 45],
        ["Final integration", 330, 0, 0, 0, 0.12, 45],
        ["Configuration", 120, 0, 0, 0, 0.05, 25],
        ["Inspection", 0, 0, 90, 0, 0.03, 20],
        ["Functional test", 0, 0, 0, 180, 0.08, 60],
        ["Pack / release", 60, 0, 0, 0, 0.01, 15],
    ],
    columns=["Step", "Base cycle", "Setup/unit", "Inspection", "Test", "Rework rate", "Avg rework min"],
)


def readiness_band(score):
    if score < 40:
        return "Prototype Readiness"
    if score < 55:
        return "Production Concept Defined"
    if score < 70:
        return "Process Demonstrated"
    if score < 85:
        return "Low-Rate Production Ready"
    return "Scalable Production Ready"


def dimension_scores(responses):
    result = {}
    for dim in DIMENSIONS:
        vals = [responses[i] for i, (d, _) in enumerate(QUESTIONS) if d == dim]
        result[dim] = sum(vals) / len(vals)
    return result


def weighted_score(scores):
    return sum((scores[d] / 5.0) * weight for d, weight in DIMENSIONS.items())


def signal(score, scores):
    if any(scores[d] <= 2 for d in CRITICAL):
        return "RED"
    if score < 75:
        return "YELLOW"
    return "GREEN"


def capacity(df, demand, days, hours, shifts, availability, operators):
    df = df.copy()
    for col in ["Base cycle", "Setup/unit", "Inspection", "Test", "Rework rate", "Avg rework min"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df = df[df["Step"].astype(str).str.strip() != ""].copy()
    available = days * hours * 60 * shifts * availability
    takt = available / demand if demand else 0
    df["Effective min"] = df["Base cycle"] + df["Setup/unit"] + df["Inspection"] + df["Test"] + df["Rework rate"] * df["Avg rework min"]
    df["Parallel needed"] = df["Effective min"].apply(lambda x: max(1, math.ceil(x / takt)) if takt else 1)
    labor = float(df["Effective min"].sum())
    bottleneck = None
    bottleneck_time = 0.0
    if not df.empty:
        idx = df["Effective min"].idxmax()
        bottleneck = str(df.loc[idx, "Step"])
        bottleneck_time = float(df.loc[idx, "Effective min"])
    labor_output = (available * operators) / labor if labor else 0
    required_operators = math.ceil(labor / takt) if takt and labor else 0
    return {
        "df": df,
        "available": available,
        "takt": takt,
        "labor": labor,
        "bottleneck": bottleneck,
        "bottleneck_time": bottleneck_time,
        "labor_output": labor_output,
        "required_operators": required_operators,
    }


def recommendations(scores, cap):
    library = {
        "Product maturity": "Freeze a production-intent baseline for several consecutive builds and control BOM/configuration changes.",
        "DFM/DFA maturity": "Review expert-dependent steps, unique parts, fastening, connectors, access and modular replacement boundaries.",
        "Assembly readiness": "Map the build flow and measure cycle time, queues, WIP and rework by major step.",
        "Takt/capacity readiness": "Translate the target rate into takt and compare it with observed station times and labor content.",
        "Quality readiness": "Define CTQs, in-process gates, defect taxonomy and a closed corrective-action loop.",
        "Supply chain readiness": "Rank single-source, long-lead and constrained items and define mitigation for the highest risks.",
        "Tooling readiness": "Prioritize fixtures and production test aids that reduce variation at critical steps.",
        "Documentation readiness": "Create controlled build instructions, a traveler/build record, training requirements and change control.",
        "Field repairability": "Measure replacement time, required tools, recurring failures and spares consumption.",
        "Scale-up readiness": "Write explicit assumptions for 10/50/100 units across people, process, quality, supply and tooling.",
    }
    actions = [(dim, library[dim]) for dim, score in sorted(scores.items(), key=lambda x: x[1]) if score < 3]
    over = cap["df"][cap["df"]["Effective min"] > cap["takt"]]
    for _, row in over.sort_values("Effective min", ascending=False).head(3).iterrows():
        actions.append((str(row["Step"]), f"Effective time {row['Effective min']:.1f} min exceeds takt {cap['takt']:.1f}; reduce, split, fixture or parallelize the work."))
    return actions[:8]
