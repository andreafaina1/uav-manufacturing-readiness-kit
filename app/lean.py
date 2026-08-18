import pandas as pd

SIX_S = {
    "Sort": "Only necessary tools, materials and references are present at the workstation.",
    "Set in Order": "Items have clear point-of-use locations, labels and replenishment positions.",
    "Shine": "The cell is clean enough that abnormalities, damage and leaks are easy to see.",
    "Standardize": "Layout, tooling, visual standards and routines are defined and repeatable.",
    "Sustain": "The team has ownership, audit cadence and routines that keep standards from decaying.",
    "Safety": "Ergonomics, lifting, electrical, battery, trip and workstation hazards are controlled for the work being done.",
    "Security & information control": "Access, configuration records, controlled documents and sensitive information are handled deliberately.",
}

WASTE_LENSES = {
    "Defects": "Scrap, rework, escapes, failed tests or repeated corrections.",
    "Overproduction": "Building earlier or in larger quantities than the downstream need.",
    "Waiting": "People or units idle for parts, tools, decisions, test capacity or approvals.",
    "Non-utilized talent": "Skilled people doing avoidable clerical/search work or improvement ideas not used.",
    "Transportation": "Unnecessary movement of parts, kits, units or documents between locations.",
    "Inventory": "Excess raw material, WIP, finished units, spares or uncontrolled buffers.",
    "Motion": "Unnecessary walking, reaching, searching, bending or repeated tool movement.",
    "Extra-processing": "Work, checks, documentation or precision beyond what is required for the defined output.",
    "Safety & ergonomics exposure": "Unsafe or fatigue-inducing work that can create injury, delay, variation or quality loss.",
    "Information / configuration loss": "Uncontrolled revisions, tribal knowledge, missing build records or information trapped in chats and laptops.",
}

MVPS_GATES = {
    "Product": "A production-intent configuration is stable enough for a controlled batch.",
    "People": "Required skills, training, ownership and cross-training are explicit.",
    "Process": "The build sequence, standard work, handoffs and rework loops are visible.",
    "Place": "A minimum viable cell supports flow, 6S, point-of-use work and controlled WIP.",
    "Parts": "BOM, kitting, shortages, long-lead items and replenishment are controlled.",
    "Tools": "Production-intent tools, fixtures and test aids are available and controlled.",
    "Quality": "CTQs, in-process checks, final release and nonconformance handling are defined.",
    "Performance": "Takt, cycle time, WIP, defects, shortages and actions are reviewed visibly.",
}

LEAN_ACTIONS = {
    "Sort": "Run a red-tag pass and remove nonessential material/tools from the cell.",
    "Set in Order": "Create point-of-use locations and labelled homes for tools, kits and consumables.",
    "Shine": "Define a short daily clean-and-inspect routine that makes abnormalities visible.",
    "Standardize": "Freeze a visual baseline for layout, tool positions, standard work and replenishment.",
    "Sustain": "Assign cell ownership and a lightweight recurring 6S review with action closure.",
    "Safety": "Complete a task-level safety/ergonomics review and remove the highest exposure first.",
    "Security & information control": "Define controlled storage, access and revision rules for build/configuration information.",
    "Defects": "Pareto the top defects and introduce quality-at-source checks or error-proofing at the originating step.",
    "Overproduction": "Build to an explicit pull signal or near-term requirement instead of speculative batch size.",
    "Waiting": "Measure the largest queues and waiting causes, then attack the dominant constraint first.",
    "Non-utilized talent": "Move low-value admin/search work away from scarce technical specialists and capture operator improvement ideas.",
    "Transportation": "Re-layout high-frequency material moves and bring recurring parts closer to point of use.",
    "Inventory": "Define explicit WIP/min-max limits and make abnormal buffers visible.",
    "Motion": "Run a spaghetti/motion walk and relocate high-frequency tools/materials into the operator reach zone.",
    "Extra-processing": "Challenge every repeated check, duplicate record and precision step against a defined requirement.",
    "Safety & ergonomics exposure": "Redesign the highest-risk task before increasing rate; avoid scaling an unsafe method.",
    "Information / configuration loss": "Create one controlled build traveler and revision source of truth before the next batch.",
    "Product": "Freeze a production-intent baseline for a defined batch and control deviations explicitly.",
    "People": "Create a simple skills matrix and cross-train the most capacity-critical operations.",
    "Process": "Define standard work with takt/cycle expectations, work sequence and standard WIP.",
    "Place": "Design one minimum viable production cell around flow, point-of-use material and visual control.",
    "Parts": "Introduce pre-kitting and a shortage board for critical/long-lead items.",
    "Tools": "Prioritize fixtures/test aids that remove expert judgment and reduce variation.",
    "Quality": "Move critical checks upstream and close defects through root cause, countermeasure and effectiveness review.",
    "Performance": "Use a simple SQDCP board: Safety, Quality, Delivery, Cost and People/Problems, with plan-vs-actual and owners.",
}


def lean_readiness(six_s_scores, waste_scores, mvps_scores):
    six_s = sum(six_s_scores.values()) / (5 * len(six_s_scores)) * 100 if six_s_scores else 0
    waste = (1 - (sum(waste_scores.values()) / (3 * len(waste_scores)))) * 100 if waste_scores else 0
    mvps = sum(mvps_scores.values()) / (5 * len(mvps_scores)) * 100 if mvps_scores else 0
    overall = 0.35 * six_s + 0.30 * waste + 0.35 * mvps
    return {"overall": overall, "six_s": six_s, "waste": waste, "mvps": mvps}


def lean_actions(six_s_scores, waste_scores, mvps_scores, limit=8):
    candidates = []
    for name, score in six_s_scores.items():
        if score <= 2:
            candidates.append((100 - score * 20, name, LEAN_ACTIONS[name]))
    for name, severity in waste_scores.items():
        if severity >= 2:
            candidates.append((60 + severity * 10, name, LEAN_ACTIONS[name]))
    for name, score in mvps_scores.items():
        if score <= 2:
            candidates.append((100 - score * 20, name, LEAN_ACTIONS[name]))
    candidates.sort(reverse=True, key=lambda x: x[0])
    return [(name, action) for _, name, action in candidates[:limit]]


def top_wastes(waste_scores, limit=5):
    items = sorted(waste_scores.items(), key=lambda x: x[1], reverse=True)
    return [(name, severity) for name, severity in items if severity > 0][:limit]
