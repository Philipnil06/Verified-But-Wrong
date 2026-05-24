#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "external_replication"
ASSETS = ROOT / "paper_assets"


def load_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    inv = load_jsonl(OUT / "high_confidence_inventory.jsonl")
    adj = load_jsonl(OUT / "adjudication.jsonl")
    dd = load_jsonl(OUT / "dafny_direct_summary.jsonl")
    rr = load_jsonl(OUT / "repaired_target_summary.jsonl")

    c = Counter(r["label"] for r in adj)
    tier1 = c["tier1_direct_dafny"] + c["tier1_direct_dafny_repaired_blocks"]
    repair_blocks = sum(1 for r in rr if r.get("repaired_target_status") == "blocks_bad_candidate")

    summary_md = [
        "# External Replication Summary",
        "",
        "| Candidate set | Count | Notes |",
        "|---|---:|---|",
        "| Useful-description Dafny tasks | 1448 | from existing inspection report |",
        "| Scanner candidates | 128 | scanner-ranked external candidate set |",
        f"| High-confidence candidates | {len(inv)} | scanner-ranked external replication suite |",
        f"| High-confidence inspected | {len(adj)} | includes deferred/reject labels |",
        f"| Validated demonstrations | {c['tier1_direct_dafny'] + c['tier1_direct_dafny_repaired_blocks'] + c['tier2_adapted_demo']} | demonstration evidence, not prevalence evidence |",
        f"| Tier 1 direct-Dafny | {tier1} | direct-Dafny verification against reconstructed original benchmark targets |",
        f"| Tier 1 repaired-target blocks | {repair_blocks} | repaired-target check |",
        f"| Tier 2 adapted demos | {c['tier2_adapted_demo']} | adapted executable demonstration |",
        f"| Rejected | {c['reject_spec_stronger'] + c['reject_nl_ambiguous'] + c['reject_bad_candidate_not_defensible']} | labeled rejects only |",
        f"| Deferred | {c['deferred']} | not counted as findings |",
    ]
    (ASSETS / "external_replication_summary_table.md").write_text("\n".join(summary_md) + "\n", encoding="utf-8")

    cases_interest = ["DA0003", "DA0208", "DA0157", "DA0010", "DA0244", "DA0293", "DA0306"]
    adj_map = {r["case_id"]: r for r in adj}
    dd_map = {r["case_id"]: r for r in dd}
    rr_map = {r["case_id"]: r for r in rr}
    lines = ["# External Cases by Evidence Tier", "", "| Case | Gap class | Evidence tier | Original target accepts bad candidate | Intended examples fail | Repaired target rejects bad candidate | Notes |", "|---|---|---|---|---|---|---|"]
    for cid in cases_interest:
        a = adj_map.get(cid, {})
        lines.append(
            f"| {cid} | {a.get('gap_class','')} | {a.get('label','')} | {'yes' if dd_map.get(cid,{}).get('success') else 'no'} | {'yes' if a.get('intended_examples_status')=='fail' else 'no'} | {'yes' if rr_map.get(cid,{}).get('repaired_target_status')=='blocks_bad_candidate' else 'no'} | {a.get('why_counted_or_rejected','')} |"
        )
    (ASSETS / "external_replication_cases_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    claim = [
        "# Claim Boundary",
        "",
        "| We claim | We do not claim |",
        "|---|---|",
        "| external demonstration of target-validity failures | prevalence estimate |",
        "| direct-Dafny evidence for Tier 1 cases | all validated cases are direct original-target Dafny proofs |",
        "| repaired-target checks can block same bad candidate in tested cases | full general repaired spec for all benchmark tasks |",
    ]
    (ASSETS / "external_replication_repair_table.md").write_text("\n".join(claim) + "\n", encoding="utf-8")

    fig = {
        "panel_a": {"useful_tasks": 1448, "scanner_candidates": 128, "high_confidence": 41, "inspected_high_confidence": len(adj), "validated": c['tier1_direct_dafny'] + c['tier1_direct_dafny_repaired_blocks'] + c['tier2_adapted_demo'], "direct_dafny": tier1, "repaired_blocks": repair_blocks},
        "panel_b": {"naive_selected_vbw": 12, "critic_selected_vbw": 5, "oracle_selected_vbw": 0},
        "panel_c": {"naive_hidden_failing_public_passing": "34/46", "critic_hidden_failing_public_passing": "12/24", "oracle_hidden_failing": "0"},
        "panel_d": {"dangerous_caught": "17/17", "dangerous_allowed": "0/17", "safe_allowed": "15/19", "safe_allow_rate": 78.95},
    }
    (ASSETS / "evidence_stack_figure_data.json").write_text(json.dumps(fig, indent=2), encoding="utf-8")
    (ASSETS / "evidence_stack_figure.md").write_text("# Evidence Stack Figure\n\nUse `evidence_stack_figure_data.json` for plotting.\n", encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        fig_obj, axs = plt.subplots(2, 2, figsize=(10, 7))
        axs[0,0].bar(["useful", "candidates", "high", "inspected", "validated", "direct", "repaired"], [1448, 128, 41, len(adj), fig['panel_a']['validated'], tier1, repair_blocks])
        axs[0,0].set_title("Panel A")
        axs[0,1].bar(["naive", "critic", "oracle"], [12, 5, 0]); axs[0,1].set_title("Panel B")
        axs[1,0].bar(["naive", "critic", "oracle"], [34/46, 12/24, 0]); axs[1,0].set_ylim(0,1); axs[1,0].set_title("Panel C")
        axs[1,1].bar(["dangerous caught", "dangerous allowed", "safe allowed"], [17/17, 0/17, 15/19]); axs[1,1].set_ylim(0,1); axs[1,1].set_title("Panel D")
        fig_obj.tight_layout()
        fig_obj.savefig(ASSETS / "evidence_stack_figure.png", dpi=200)
        fig_obj.savefig(ASSETS / "evidence_stack_figure.svg")
    except Exception:
        (ASSETS / "evidence_stack_figure.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg' width='800' height='400'><text x='20' y='40'>See evidence_stack_figure_data.json</text></svg>", encoding="utf-8")

    print("wrote paper assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
