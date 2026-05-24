from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from llm_specs import load_latest_llm_spec_experiment, run_llm_spec_experiment
from llm_specs import build_llm_model_comparison, load_llm_model_comparison
from llm_selection import load_latest_llm_selection_experiment, run_saved_llm_spec_selection_experiment
from manual_audit import generate_manual_coverage_audit
from audit_gate_ablation import run_audit_gate_ablation
from defense_baselines import run_defense_baselines
from naturalistic_experiment import run_naturalistic_experiment
from runner import (
    DEFAULT_TASK_ID,
    list_tasks,
    load_latest_benchmark,
    load_latest_result,
    load_results_log,
    load_task,
    run_comparison,
    run_mini_benchmark,
    run_task,
)
from spec_audit_calibration import (
    load_controlled_audit_calibration,
    load_latest_llm_audit_calibration,
    load_policy_gate_calibration,
    run_controlled_audit_calibration,
    run_policy_gate_calibration,
    run_saved_llm_audit_calibration,
)
from spec_audit_gate import load_latest_spec_audit_gate, run_spec_audit_gate_on_saved_llm_specs
from spec_repair import load_spec_repair_experiment, run_repair_experiment
from stats_summary import build_stats_summary


st.set_page_config(page_title="Verified but Wrong", page_icon="!", layout="wide")


def initialize_state() -> None:
    if "displayed_result" not in st.session_state:
        st.session_state.displayed_result = None
    if "selected_task_id" not in st.session_state:
        st.session_state.selected_task_id = DEFAULT_TASK_ID
    if "llm_spec_model" not in st.session_state:
        st.session_state.llm_spec_model = os.environ.get("OPENAI_SPEC_MODEL", "gpt-5.4-nano")
    if "llm_num_samples" not in st.session_state:
        st.session_state.llm_num_samples = 5


def selected_task_id() -> str:
    return st.session_state.get("selected_task_id", DEFAULT_TASK_ID)


def run_and_store(mode: str) -> None:
    st.session_state.displayed_result = run_task(selected_task_id(), mode)


def run_comparison_and_store() -> None:
    st.session_state.displayed_result = run_comparison(selected_task_id())


def run_benchmark_and_store() -> None:
    st.session_state.displayed_result = run_mini_benchmark()


def load_latest_and_store() -> None:
    st.session_state.displayed_result = load_latest_result()


def clear_displayed_result() -> None:
    st.session_state.displayed_result = None


def run_llm_experiment_and_store() -> None:
    st.session_state.displayed_result = run_llm_spec_experiment(
        num_samples_per_task=int(st.session_state.llm_num_samples),
        model=st.session_state.llm_spec_model,
    )


def load_latest_llm_experiment_and_store() -> None:
    st.session_state.displayed_result = load_latest_llm_spec_experiment()


def build_llm_model_comparison_and_store() -> None:
    st.session_state.displayed_result = build_llm_model_comparison()


def load_llm_model_comparison_and_store() -> None:
    st.session_state.displayed_result = load_llm_model_comparison()


def run_llm_selection_and_store() -> None:
    st.session_state.displayed_result = run_saved_llm_spec_selection_experiment()


def load_llm_selection_and_store() -> None:
    st.session_state.displayed_result = load_latest_llm_selection_experiment()


def run_audit_gate_and_store() -> None:
    st.session_state.displayed_result = run_spec_audit_gate_on_saved_llm_specs()


def load_audit_gate_and_store() -> None:
    st.session_state.displayed_result = load_latest_spec_audit_gate()


def generate_manual_audit_and_store() -> None:
    st.session_state.displayed_result = generate_manual_coverage_audit()


def run_controlled_calibration_and_store() -> None:
    st.session_state.displayed_result = run_controlled_audit_calibration()


def load_controlled_calibration_and_store() -> None:
    st.session_state.displayed_result = load_controlled_audit_calibration()


def run_llm_calibration_and_store() -> None:
    st.session_state.displayed_result = run_saved_llm_audit_calibration()


def load_llm_calibration_and_store() -> None:
    st.session_state.displayed_result = load_latest_llm_audit_calibration()


def run_research_artifact(name: str) -> None:
    actions = {
        "policy_gate": run_policy_gate_calibration,
        "repair": run_repair_experiment,
        "baselines": run_defense_baselines,
        "ablation": run_audit_gate_ablation,
        "naturalistic": run_naturalistic_experiment,
        "stats": build_stats_summary,
    }
    st.session_state.displayed_result = actions[name]()


def bool_label(value: bool) -> str:
    return "YES" if value else "NO"


def render_styles() -> None:
    st.markdown(
        """
        <style>
          .block-container { padding-top: 2.2rem; }
          .hero {
            border: 1px solid #d9e2d0;
            border-radius: 18px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            background:
              radial-gradient(circle at top left, rgba(219, 245, 173, 0.75), transparent 34%),
              linear-gradient(135deg, #fbfaf3 0%, #edf4e4 100%);
          }
          .hero h1 { margin-bottom: 0.2rem; color: #17210f; }
          .hero p { color: #34422a; font-size: 1.05rem; }
          .pipeline {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            align-items: center;
            margin: 0.5rem 0 1.2rem 0;
          }
          .pipeline div {
            border: 1px solid #c9d7bd;
            background: #fbfff6;
            border-radius: 12px;
            padding: 0.65rem 0.8rem;
            font-weight: 650;
          }
          .pipeline span { color: #607052; font-weight: 800; }
          .impact-box {
            border-left: 6px solid #405a25;
            background: #f6faef;
            padding: 0.9rem 1rem;
            border-radius: 12px;
            margin: 0.8rem 0 1.1rem 0;
            color: #223019;
          }
          .safety-diagram {
            border: 1px dashed #9caf88;
            border-radius: 14px;
            background: #fffdf5;
            padding: 0.9rem 1rem;
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            white-space: pre-line;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_task_overview(task: dict) -> None:
    st.subheader("1. Task overview")
    st.markdown(f"**Selected task:** {task['title']} (`{task['id']}`)")

    st.markdown("**Natural language intent**")
    st.info(task["intent"])

    st.markdown("**AI-generated incomplete public spec**")
    st.warning(task["ai_generated_spec"])

    st.markdown("**Critic improved spec**")
    st.success(task["critic_improved_spec"])

    if task.get("full_oracle_spec"):
        st.markdown("**Full oracle spec**")
        st.info(task["full_oracle_spec"])

    left, right = st.columns(2)
    with left:
        st.markdown("**Missing requirements**")
        for requirement in task["missing_requirements"]:
            st.markdown(f"- {requirement}")
    with right:
        st.markdown("**Spec hole categories**")
        for category in task["spec_hole_categories"]:
            st.markdown(f"- `{category}`")


def render_pipeline_diagram() -> None:
    st.subheader("2. Pipeline")
    st.markdown(
        """
        <div class="pipeline">
          <div>Intent</div><span>-></span>
          <div>AI-generated spec</div><span>-></span>
          <div>Candidate implementations</div><span>-></span>
          <div>Spec ranking</div><span>-></span>
          <div>Hidden intent oracle</div><span>-></span>
          <div>Spec hole report</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def candidate_table(result: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate": candidate["name"],
                "public passed": candidate["public_passed"],
                "public passed count": candidate["public"]["passed_count"],
                "hidden passed": candidate["hidden_passed"],
                "hidden passed count": candidate["hidden"]["passed_count"],
                "selected": candidate["selected"],
                "verified but wrong": candidate["verified_but_wrong"],
            }
            for candidate in result["candidates"]
        ]
    )


def render_result_cards(result: dict) -> None:
    st.subheader("4. Result cards")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Selected candidate", result["selected_candidate"])
    col2.metric("Public spec result", "PASS" if result["public_spec_passed"] else "FAIL")
    col3.metric("Hidden intent oracle", "PASS" if result["hidden_oracle_passed"] else "FAIL")
    col4.metric("Verified but wrong", bool_label(result["verified_but_wrong"]))

    if result["verified_but_wrong"]:
        st.error(
            "VERIFIED BUT WRONG\n\n"
            "The selected implementation passed the public spec but failed the hidden intent oracle."
        )
        report = result["spec_hole_report"]
        st.markdown(f"**Missing requirement:** {report['missing_requirement']}")
        st.markdown(f"**Counterexample:** {report['counterexample']}")
        st.markdown("**Categories:** " + ", ".join(f"`{item}`" for item in report["categories"]))
    elif result["mode"] == "critic" and result["public_spec_passed"] and result["hidden_oracle_passed"]:
        st.success(
            "DEFENSE SUCCESS\n\n"
            "The omission aware critic spec selected an implementation that passes both the public spec and the hidden intent oracle."
        )
    elif result["mode"] == "oracle" and result["public_spec_passed"] and result["hidden_oracle_passed"]:
        st.success(
            "ORACLE SPEC SUCCESS\n\n"
            "The full intended spec selected an implementation that passes both public checks and the hidden intent oracle."
        )
    elif result["public_spec_passed"] and result["hidden_oracle_passed"]:
        st.success("The selected implementation passes both the public spec and hidden intent oracle.")
    else:
        st.warning("The selected implementation did not pass the public ranking spec.")


def render_candidate_table(result: dict) -> None:
    st.subheader("5. Candidate table")
    st.dataframe(candidate_table(result), use_container_width=True, hide_index=True)


def render_tests(label: str, test_result: dict) -> None:
    st.markdown(f"**{label}**")
    for test in test_result["tests"]:
        icon = "PASS" if test["passed"] else "FAIL"
        st.markdown(
            f"- `{icon}` **{test['name']}** | expected: `{test['expected']}` | actual: `{test['actual']}`"
        )


def render_test_details(result: dict) -> None:
    st.subheader("6. Test details")
    for candidate in result["candidates"]:
        selected = " selected" if candidate["selected"] else ""
        with st.expander(f"{candidate['name']}{selected}"):
            left, right = st.columns(2)
            with left:
                render_tests("Public spec test results", candidate["public"])
            with right:
                render_tests("Hidden intent oracle test results", candidate["hidden"])


def render_single_result(result: dict) -> None:
    render_result_cards(result)
    render_candidate_table(result)
    render_test_details(result)


def render_comparison_card(title: str, result: dict) -> None:
    st.markdown(f"### {title}")
    st.write(f"Mode: `{result['mode']}`")
    st.metric("Selected candidate", result["selected_candidate"])
    st.write(f"Public spec result: `{'PASS' if result['public_spec_passed'] else 'FAIL'}`")
    st.write(f"Hidden oracle result: `{'PASS' if result['hidden_oracle_passed'] else 'FAIL'}`")
    st.write(f"Verified but wrong: `{result['verified_but_wrong']}`")
    if result["verified_but_wrong"]:
        st.error("Verified but wrong")
    else:
        st.success("Not verified but wrong")


def render_comparison(result: dict) -> None:
    st.subheader("7. Comparison view")
    left, middle, right = st.columns(3)
    with left:
        render_comparison_card("Naive AI Spec", result["naive"])
    with middle:
        render_comparison_card("Omission-aware Critic Spec", result["critic"])
    with right:
        render_comparison_card("Full Oracle Spec", result["oracle"])

    summary = result["summary"]
    st.markdown("### Summary")
    st.write(f"Naive wrong selection: `{summary['naive_verified_but_wrong']}`")
    st.write(f"Critic wrong selection: `{summary['critic_verified_but_wrong']}`")
    st.write(f"Oracle wrong selection: `{summary['oracle_verified_but_wrong']}`")
    st.write(f"Defense reduced failure: `{summary['defense_reduced_failure']}`")
    st.write(f"Oracle reduced failure: `{summary['oracle_reduced_failure']}`")

    st.divider()
    st.markdown("### Naive candidate table")
    st.dataframe(candidate_table(result["naive"]), use_container_width=True, hide_index=True)
    st.markdown("### Critic candidate table")
    st.dataframe(candidate_table(result["critic"]), use_container_width=True, hide_index=True)
    st.markdown("### Oracle candidate table")
    st.dataframe(candidate_table(result["oracle"]), use_container_width=True, hide_index=True)


def render_benchmark(result: dict) -> None:
    st.subheader("Mini benchmark")
    naive = result["naive"]
    critic = result["critic"]
    oracle = result.get("oracle", critic)
    improvement = result["improvement"]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total tasks", naive["total_tasks"])
    c2.metric("Naive VBW rate", f"{naive['verified_but_wrong_rate']:.0%}")
    c3.metric("Critic VBW rate", f"{critic['verified_but_wrong_rate']:.0%}")
    c4.metric("Oracle VBW rate", f"{oracle['verified_but_wrong_rate']:.0%}")
    c5.metric("Critic reduction", improvement["wrong_selection_reduction"])
    c6.metric("Oracle reduction", improvement.get("oracle_wrong_selection_reduction", 0))

    st.markdown("### Benchmark table by task")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "task": row["task_title"],
                    "naive selected": row["naive_selected"],
                    "naive verified but wrong": row["naive_verified_but_wrong"],
                    "critic selected": row["critic_selected"],
                    "critic verified but wrong": row["critic_verified_but_wrong"],
                    "oracle selected": row.get("oracle_selected"),
                    "oracle verified but wrong": row.get("oracle_verified_but_wrong"),
                    "defense fixed": row["defense_fixed"],
                    "oracle fixed": row.get("oracle_fixed"),
                }
                for row in result["tasks"]
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Taxonomy counts")
    taxonomy_rows = [
        {"spec hole category": category, "count": count}
        for category, count in result["taxonomy_counts"].items()
    ]
    st.dataframe(pd.DataFrame(taxonomy_rows), use_container_width=True, hide_index=True)

    st.info(
        "Naive AI specs produced verified but wrong selections across multiple task types. "
        "The omission aware critic reduces wrong selections, while oracle specs represent the full intended upper-bound behavior."
    )


def _flatten_llm_samples(result: dict) -> list[dict]:
    rows = []
    for task_result in result.get("task_results", []):
        for sample in task_result.get("samples", []):
            analysis = sample["analysis"]
            rows.append(
                {
                    "task_id": sample["task_id"],
                    "sample_id": sample["sample_id"],
                    "coverage_rate": analysis["coverage_rate"],
                    "covered_count": analysis["covered_count"],
                    "missing_count": analysis["missing_count"],
                    "unclear_count": analysis["unclear_count"],
                    "not_clearly_covered_count": analysis.get(
                        "not_clearly_covered_count",
                        analysis["missing_count"] + analysis["unclear_count"],
                    ),
                    "not_clearly_covered_categories": ", ".join(
                        analysis.get("not_clearly_covered_categories")
                        or analysis.get("missing_categories", [])
                    ),
                    "sample": sample,
                    "intent": task_result.get("intent", ""),
                }
            )
    return rows


def render_llm_spec_experiment(result: dict | None) -> None:
    st.subheader("LLM Spec Experiment")
    st.write(
        "The deterministic benchmark shows the mechanism. This experiment tests whether real "
        "model-generated specs omit the same intent-critical requirements."
    )

    if result is None:
        st.warning("No saved LLM spec experiment found.")
        return

    if result.get("provider_configured") is False:
        st.warning(f"LLM provider is not configured: {result.get('error', 'unknown error')}")
        st.caption("Set OPENAI_API_KEY to run live generation, or load latest saved results if available.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Model", result["model"])
    c2.metric("Total generated specs", result["total_specs"])
    c3.metric(
        "Average clear coverage",
        f"{result.get('average_clear_coverage_rate', result.get('average_coverage_rate', 0.0)):.0%}",
    )
    c4.metric("Exact missing requirements", result.get("exact_missing_requirements", result.get("total_missing_requirements", 0)))
    c5.metric(
        "Unclear requirements",
        result.get(
            "unclear_requirements",
            result.get("not_clearly_covered_requirements", 0)
            - result.get("exact_missing_requirements", result.get("total_missing_requirements", 0)),
        ),
    )
    st.metric(
        "Not clearly covered requirements",
        result.get("not_clearly_covered_requirements", result.get("total_missing_requirements", 0)),
    )

    st.markdown("### Most common not-clearly-covered categories")
    category_counts = result.get("most_common_not_clearly_covered_categories") or result.get(
        "most_common_missing_categories"
    )
    if category_counts:
        st.dataframe(
            pd.DataFrame(
                [
                    {"category": category, "count": count}
                    for category, count in category_counts.items()
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No not-clearly-covered categories detected.")

    rows = _flatten_llm_samples(result)
    st.markdown("### Generated spec coverage")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "task_id": row["task_id"],
                    "sample_id": row["sample_id"],
                    "coverage_rate": row["coverage_rate"],
                    "covered_count": row["covered_count"],
                    "exact missing": row["missing_count"],
                    "unclear": row["unclear_count"],
                    "not clearly covered": row["not_clearly_covered_count"],
                    "not clearly covered categories": row["not_clearly_covered_categories"],
                }
                for row in rows
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Generated specs")
    for row in rows:
        sample = row["sample"]
        analysis = sample["analysis"]
        with st.expander(f"{sample['task_id']} sample {sample['sample_id']} coverage {analysis['coverage_rate']:.0%}"):
            st.markdown("**Intent**")
            st.info(row["intent"])

            st.markdown("**Generated public spec**")
            st.write(sample["public_spec"])

            left, middle, right = st.columns(3)
            with left:
                st.markdown("**Assumptions**")
                for item in sample.get("assumptions", []):
                    st.markdown(f"- {item}")
            with middle:
                st.markdown("**Properties**")
                for item in sample.get("properties", []):
                    st.markdown(f"- {item}")
            with right:
                st.markdown("**Edge cases**")
                for item in sample.get("edge_cases", []):
                    st.markdown(f"- {item}")

            covered = [item for item in analysis["coverage"] if item["status"] == "covered"]
            missing = [item for item in analysis["coverage"] if item["status"] == "missing"]
            unclear = [item for item in analysis["coverage"] if item["status"] == "unclear"]

            st.markdown("**Covered requirements**")
            for item in covered:
                st.markdown(f"- {item['requirement']} (`{item['evidence']}`)")

            st.markdown("**Missing requirements**")
            for item in missing:
                st.markdown(f"- {item['requirement']} (`{item['evidence']}`)")

            st.markdown("**Unclear requirements**")
            for item in unclear:
                st.markdown(f"- {item['requirement']} (`{item['evidence']}`)")

    st.info(
        "Real model-generated specs can be checked before vericoding uses them. "
        "Missing intent-critical requirements are spec holes that may cause verified-but-wrong implementation selection."
    )
    st.info(
        "In this run, unclear means the generated spec may have covered the requirement semantically, "
        "but did not match the stricter rule-based coverage patterns. These are review targets, not confirmed omissions."
    )


def render_llm_model_comparison(result: dict | None) -> None:
    st.subheader("LLM Model Comparison")
    st.write(
        "This comparison is built only from saved `results/llm_spec_runs.jsonl` rows. "
        "It does not make new API calls."
    )
    if result is None:
        st.warning("No saved LLM model comparison found.")
        return

    st.caption(f"Source: `{result.get('source')}`")
    st.metric("Models compared", result.get("total_models", 0))
    st.metric("Saved specs included", result.get("total_specs", 0))

    model_rows = result.get("models", [])
    st.markdown("### Summary by model")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "model": row["model"],
                    "valid_specs": row.get("valid_specs", row.get("total_specs")),
                    "invalid_generations": row.get("invalid_generations", 0),
                    "total_saved_rows": row.get("total_saved_rows", row.get("total_specs")),
                    "average_clear_coverage_rate": row["average_clear_coverage_rate"],
                    "average_possible_coverage_rate": row["average_possible_coverage_rate"],
                    "exact_missing_requirements": row["exact_missing_requirements"],
                    "unclear_requirements": row["unclear_requirements"],
                    "not_clearly_covered_requirements": row["not_clearly_covered_requirements"],
                }
                for row in model_rows
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Category counts per model")
    for row in model_rows:
        with st.expander(row["model"]):
            left, middle, right = st.columns(3)
            with left:
                st.markdown("**Not clearly covered**")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"category": category, "count": count}
                            for category, count in row.get(
                                "most_common_not_clearly_covered_categories", {}
                            ).items()
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            with middle:
                st.markdown("**Exact missing**")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"category": category, "count": count}
                            for category, count in row.get("most_common_exact_missing_categories", {}).items()
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            with right:
                st.markdown("**Unclear**")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"category": category, "count": count}
                            for category, count in row.get("most_common_unclear_categories", {}).items()
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )


def render_llm_selection_experiment(result: dict | None) -> None:
    st.subheader("LLM Spec -> Selection Experiment")
    st.write(
        "Saved LLM specs are mapped to curated executable requirement tests, then used to rank candidates. "
        "The generated text is never executed as code."
    )
    if result is None:
        st.warning("No saved LLM selection experiment found.")
        return

    st.markdown("### Model comparison")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "model": row["model"],
                    "valid_specs": row["valid_specs"],
                    "verified_but_wrong_count": row["verified_but_wrong_count"],
                    "verified_but_wrong_rate": row["verified_but_wrong_rate"],
                    "hidden_oracle_pass_rate": row["hidden_oracle_pass_rate"],
                    "average_selected_requirement_count": row["average_selected_requirement_count"],
                }
                for row in result.get("models", [])
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    problematic = [run for run in result.get("runs", []) if run["verified_but_wrong"]]
    st.markdown("### Problematic specs")
    if problematic:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "model": run["model"],
                        "task_id": run["task_id"],
                        "sample_id": run["sample_id"],
                        "selected_candidate": run["selected_candidate"],
                        "selected_requirement_count": run["selected_requirement_count"],
                        "verified_but_wrong": run["verified_but_wrong"],
                        "not clearly covered": len(run.get("not_clearly_covered_requirements", [])),
                    }
                    for run in problematic
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("No saved LLM specs selected a verified-but-wrong implementation.")

    st.markdown("### Selection details")
    for run in result.get("runs", []):
        label = f"{run['model']} / {run['task_id']} / sample {run['sample_id']} -> {run['selected_candidate']}"
        if run["verified_but_wrong"]:
            label += " / VERIFIED BUT WRONG"
        with st.expander(label):
            st.markdown("**Generated spec**")
            st.write(run.get("generated_public_spec", ""))

            st.markdown("**Selected requirements**")
            for requirement in run.get("selected_requirements", []):
                st.markdown(f"- {requirement}")

            st.markdown("**Candidate ranking table**")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "candidate": candidate["name"],
                            "public passed": candidate["public_passed"],
                            "public passed count": candidate["public"]["passed_count"],
                            "hidden passed": candidate["hidden_passed"],
                            "hidden passed count": candidate["hidden"]["passed_count"],
                            "selected": candidate["selected"],
                            "verified but wrong": candidate["verified_but_wrong"],
                        }
                        for candidate in run.get("candidate_results", [])
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

            selected = next(
                (candidate for candidate in run.get("candidate_results", []) if candidate.get("selected")),
                None,
            )
            if selected:
                st.markdown("**Hidden oracle failures for selected candidate**")
                failures = selected.get("hidden", {}).get("failures", [])
                if failures:
                    for failure in failures:
                        st.markdown(f"- {failure}")
                else:
                    st.markdown("- none")


def render_spec_audit_gate(result: dict | None) -> None:
    st.subheader("Spec Audit Gate")
    st.write(
        "The audit gate turns LLM spec coverage gaps into deployment-style decisions before a "
        "vericoding pipeline is allowed to select an implementation."
    )
    if result is None:
        st.warning("No saved Spec Audit Gate result found.")
        return

    audits = result.get("audits", [])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Valid specs audited", result.get("valid_specs", 0))
    c2.metric("Pre-selection ALLOW", sum(1 for audit in audits if audit.get("pre_selection_decision", audit.get("risk_level")) == "ALLOW"))
    c3.metric("Pre-selection REVIEW", sum(1 for audit in audits if audit.get("pre_selection_decision", audit.get("risk_level")) == "REVIEW"))
    c4.metric("Pre-selection BLOCK", sum(1 for audit in audits if audit.get("pre_selection_decision", audit.get("risk_level")) == "BLOCK"))

    st.markdown("### Summary by model")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "model": row["model"],
                    "valid_specs": row["valid_specs"],
                    "invalid_specs": row["invalid_specs"],
                    "ALLOW": row["allow_count"],
                    "REVIEW": row["review_count"],
                    "BLOCK": row["block_count"],
                    "top risk categories": row.get("most_common_risk_categories", {}),
                }
                for row in result.get("models", [])
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Audit decisions")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "model": audit["model"],
                    "task_id": audit["task_id"],
                    "sample_id": audit["sample_id"],
                    "pre-selection": audit.get("pre_selection_decision", audit.get("risk_level")),
                    "post-selection": audit.get("post_selection_decision"),
                    "coverage_rate": audit["coverage_rate"],
                    "selected_candidate": audit.get("selected_candidate"),
                    "verified_but_wrong": audit.get("verified_but_wrong"),
                    "critical missing": len(audit.get("critical_missing_requirements", [])),
                    "critical unclear": len(audit.get("critical_unclear_requirements", audit.get("unclear_requirements", []))),
                }
                for audit in audits
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    for audit in audits[:30]:
        decision = audit.get("pre_selection_decision", audit.get("risk_level"))
        with st.expander(f"{decision} / {audit['model']} / {audit['task_id']} / sample {audit['sample_id']}"):
            st.markdown(f"**Recommendation:** {audit['recommendation']}")
            st.markdown(f"**Pre-selection decision:** `{decision}`")
            st.markdown(f"**Post-selection decision:** `{audit.get('post_selection_decision')}`")
            st.markdown(f"**CI exit code:** `{audit['ci_exit_code']}`")
            st.markdown("**Generated spec excerpt**")
            st.write(audit.get("generated_spec_excerpt", ""))
            st.markdown("**Critical missing requirements**")
            for item in audit.get("critical_missing_requirements", []):
                st.markdown(f"- {item['requirement']} | {item['why_it_matters']} | {item['suggested_review_question']}")
            st.markdown("**Unclear requirements**")
            for item in audit.get("critical_unclear_requirements", audit.get("unclear_requirements", [])):
                st.markdown(f"- {item['requirement']} | {item['why_it_matters']} | {item['suggested_review_question']}")


def render_manual_audit(result: dict | None) -> None:
    st.subheader("Manual Coverage Audit Worksheet")
    if result is None:
        st.warning("No manual audit worksheet generated.")
        return
    st.write(
        "Because coverage classification is rule-based, this worksheet exports every missing/unclear "
        "case for manual review. It does not claim the manual audit is complete."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Exact missing", result.get("total_exact_missing_requirements", 0))
    c2.metric("Unclear", result.get("total_unclear_requirements", 0))
    c3.metric("Worksheet rows", len(result.get("worksheet_rows", [])))
    st.caption(result.get("path", "results/manual_coverage_audit.md"))


def render_audit_calibration(result: dict | None) -> None:
    st.subheader("Audit Gate Calibration")
    st.write(
        "The audit gate is useful only if it flags risky specs before implementation selection. "
        "This calibration compares pre-selection audit decisions against downstream verified-but-wrong outcomes."
    )
    if result is None:
        st.warning("No audit calibration result found.")
        return

    if result.get("result_type") == "controlled_audit_calibration":
        summary = result.get("summary", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Controlled specs audited", summary.get("total_controlled_specs_audited", 0))
        c2.metric("Verified-but-wrong specs", summary.get("verified_but_wrong_specs", 0))
        c3.metric("Allowed verified-but-wrong", summary.get("allowed_verified_but_wrong_count", 0))
        c4.metric("Wrong selection catch rate", f"{summary.get('wrong_selection_catch_rate', 0.0):.0%}")

        st.markdown("### Controlled audit by mode")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "mode": row["mode"],
                        "specs": row["specs_audited"],
                        "verified-but-wrong": row["verified_but_wrong_count"],
                        "ALLOW": row["pre_ALLOW"],
                        "REVIEW": row["pre_REVIEW"],
                        "BLOCK": row["pre_BLOCK"],
                        "allowed wrong": row["allowed_verified_but_wrong_count"],
                        "caught wrong": row["caught_verified_but_wrong_count"],
                    }
                    for row in result.get("by_mode", [])
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Examples")
        examples = [
            ("Naive spec caught before wrong selection", lambda row: row["mode"] == "naive" and row["verified_but_wrong"] and row["pre_selection_decision"] in {"REVIEW", "BLOCK"}),
            ("Loyalty critic caught before wrong selection", lambda row: row["task_id"] == "loyalty_refund_reversal" and row["mode"] == "critic"),
            ("Oracle spec allowed and correct", lambda row: row["mode"] == "oracle" and row["pre_selection_decision"] == "ALLOW" and not row["verified_but_wrong"]),
        ]
        for title, predicate in examples:
            row = next((item for item in result.get("runs", []) if predicate(item)), None)
            with st.expander(title):
                if row is None:
                    st.caption("No matching example available.")
                    continue
                st.write(f"Task: `{row['task_id']}`")
                st.write(f"Mode: `{row['mode']}`")
                st.write(f"Pre-selection decision: `{row['pre_selection_decision']}`")
                st.write(f"Selected candidate: `{row.get('selected_candidate')}`")
                st.write(f"Verified but wrong: `{row.get('verified_but_wrong')}`")
                st.write(row.get("spec_text", "")[:800])

    elif result.get("result_type") == "llm_audit_calibration":
        c1, c2, c3 = st.columns(3)
        c1.metric("Saved LLM specs audited", result.get("valid_specs", 0))
        c2.metric("Invalid specs excluded", result.get("invalid_specs", 0))
        c3.metric(
            "ALLOW + verified-but-wrong",
            sum(row.get("allow_verified_but_wrong_count", 0) for row in result.get("by_model", [])),
        )

        st.markdown("### Saved LLM audit by model")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "model": row["model"],
                        "valid specs": row["valid_specs"],
                        "ALLOW": row["ALLOW"],
                        "REVIEW": row["REVIEW"],
                        "BLOCK": row["BLOCK"],
                        "verified-but-wrong": row["verified_but_wrong_count"],
                        "ALLOW + verified-but-wrong": row["allow_verified_but_wrong_count"],
                    }
                    for row in result.get("by_model", [])
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

        review_example = next((row for row in result.get("runs", []) if row["pre_selection_decision"] in {"REVIEW", "BLOCK"}), None)
        with st.expander("LLM spec REVIEW/BLOCK example"):
            if review_example is None:
                st.caption("No REVIEW/BLOCK example available.")
            else:
                st.write(f"Model: `{review_example['model']}`")
                st.write(f"Task: `{review_example['task_id']}`")
                st.write(f"Decision: `{review_example['pre_selection_decision']}`")
                st.write(review_example.get("generated_public_spec", "")[:800])


def render_research_artifact(result: dict | None) -> None:
    st.subheader("Research Artifact")
    if result is None:
        st.warning("No result loaded.")
        return
    result_type = result.get("result_type", "stats_summary")
    st.write(f"Result type: `{result_type}`")
    if result_type == "policy_gate_calibration":
        metrics = result["metrics"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Dangerous catch rate", f"{metrics['dangerous_catch_rate']:.0%}")
        c2.metric("Dangerous allowed", metrics["dangerous_allowed"])
        c3.metric("Safe allow rate", f"{metrics['safe_allow_rate']:.0%}")
        c4.metric("Safe blocked", metrics["safe_blocked"])
        st.dataframe(pd.DataFrame(result["by_spec_class"]), use_container_width=True, hide_index=True)
    elif result_type == "spec_repair_experiment":
        st.dataframe(pd.DataFrame(result["summaries"]), use_container_width=True, hide_index=True)
    elif result_type == "defense_baselines":
        st.dataframe(pd.DataFrame(result["baselines"]), use_container_width=True, hide_index=True)
    elif result_type == "audit_gate_ablation":
        st.dataframe(pd.DataFrame(result["variants"]), use_container_width=True, hide_index=True)
    elif result_type == "naturalistic_experiment":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Docs", result["naturalistic_docs_evaluated"])
        c2.metric("VBW before", result["vbw_before"])
        c3.metric("VBW after repair", result["vbw_after_repair"])
        c4.metric("Dangerous docs allowed", result["dangerous_docs_allowed"])
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "task": row["task_id"],
                        "decision before": row["audit_decision_before"],
                        "VBW before": row["verified_but_wrong_before"],
                        "decision after": row["audit_decision_after"],
                        "VBW after": row["verified_but_wrong_after"],
                    }
                    for row in result["runs"]
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    elif "wilson_95_intervals" in result:
        st.dataframe(
            pd.DataFrame(
                [
                    {"metric": key, **value}
                    for key, value in result["wilson_95_intervals"].items()
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )


def render_results_log() -> None:
    st.subheader("Results log")
    rows = load_results_log(limit=10)
    if not rows:
        st.caption("No results saved yet.")
        return

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "timestamp": row["timestamp"],
                    "task_id": row["task_id"],
                    "mode": row["mode"],
                    "selected_candidate": row["selected_candidate"],
                    "verified_but_wrong": row["verified_but_wrong"],
                }
                for row in rows
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_sidebar(tasks: list[dict]) -> None:
    task_titles = {task["id"]: task["title"] for task in tasks}
    task_ids = [task["id"] for task in tasks]
    if st.session_state.selected_task_id not in task_ids and task_ids:
        st.session_state.selected_task_id = task_ids[0]

    with st.sidebar:
        st.markdown("## Project")
        st.write("Verified but Wrong")
        st.write("**Track:** Spec-Driven Development & Evaluation")
        st.selectbox(
            "Case",
            options=task_ids,
            format_func=lambda task_id: task_titles.get(task_id, task_id),
            key="selected_task_id",
        )
        st.write("**Status:** Mini benchmark demo")
        st.divider()
        st.button("Run naive AI spec", on_click=run_and_store, args=("naive",), use_container_width=True)
        st.button("Run omission-aware critic spec", on_click=run_and_store, args=("critic",), use_container_width=True)
        st.button("Run full oracle spec", on_click=run_and_store, args=("oracle",), use_container_width=True)
        st.button("Run comparison", on_click=run_comparison_and_store, use_container_width=True)
        st.button("Run mini benchmark", on_click=run_benchmark_and_store, use_container_width=True)
        st.divider()
        st.markdown("## LLM spec experiment")
        st.text_input("LLM spec model", key="llm_spec_model")
        st.number_input("Samples per task", min_value=1, max_value=20, step=1, key="llm_num_samples")
        st.button(
            "Run real LLM spec experiment",
            on_click=run_llm_experiment_and_store,
            use_container_width=True,
        )
        st.button(
            "Load latest LLM spec experiment",
            on_click=load_latest_llm_experiment_and_store,
            use_container_width=True,
        )
        st.button(
            "Build LLM model comparison from saved runs",
            on_click=build_llm_model_comparison_and_store,
            use_container_width=True,
        )
        st.button(
            "Load LLM model comparison",
            on_click=load_llm_model_comparison_and_store,
            use_container_width=True,
        )
        st.button(
            "Run saved LLM specs through selection pipeline",
            on_click=run_llm_selection_and_store,
            use_container_width=True,
        )
        st.button(
            "Load latest LLM selection experiment",
            on_click=load_llm_selection_and_store,
            use_container_width=True,
        )
        st.divider()
        st.markdown("## Spec audit gate")
        st.button(
            "Run Spec Audit Gate on saved LLM specs",
            on_click=run_audit_gate_and_store,
            use_container_width=True,
        )
        st.button(
            "Load latest Spec Audit Gate",
            on_click=load_audit_gate_and_store,
            use_container_width=True,
        )
        st.button(
            "Generate manual coverage audit worksheet",
            on_click=generate_manual_audit_and_store,
            use_container_width=True,
        )
        st.divider()
        st.markdown("## Audit calibration")
        st.button(
            "Run controlled audit calibration",
            on_click=run_controlled_calibration_and_store,
            use_container_width=True,
        )
        st.button(
            "Load controlled audit calibration",
            on_click=load_controlled_calibration_and_store,
            use_container_width=True,
        )
        st.button(
            "Run saved LLM audit calibration",
            on_click=run_llm_calibration_and_store,
            use_container_width=True,
        )
        st.button(
            "Load saved LLM audit calibration",
            on_click=load_llm_calibration_and_store,
            use_container_width=True,
        )
        st.divider()
        st.markdown("## Research artifacts")
        st.button("Run policy gate calibration", on_click=run_research_artifact, args=("policy_gate",), use_container_width=True)
        st.button("Run repair experiment", on_click=run_research_artifact, args=("repair",), use_container_width=True)
        st.button("Run defense baselines", on_click=run_research_artifact, args=("baselines",), use_container_width=True)
        st.button("Run ablation", on_click=run_research_artifact, args=("ablation",), use_container_width=True)
        st.button("Run naturalistic experiment", on_click=run_research_artifact, args=("naturalistic",), use_container_width=True)
        st.button("Build stats summary", on_click=run_research_artifact, args=("stats",), use_container_width=True)
        if not os.environ.get("OPENAI_API_KEY"):
            st.caption("OPENAI_API_KEY is not set. Live LLM generation will show a controlled warning.")
        st.divider()
        st.button("Load latest result", on_click=load_latest_and_store, use_container_width=True)
        st.button("Clear displayed result", on_click=clear_displayed_result, use_container_width=True)


def render_impact_header(tasks: list[dict]) -> None:
    latest_benchmark = load_latest_benchmark() or {}
    latest_audit = load_latest_spec_audit_gate() or {}
    audits = latest_audit.get("audits", [])
    naive_rate = latest_benchmark.get("naive", {}).get("verified_but_wrong_rate", 0.0)
    critic_rate = latest_benchmark.get("critic", {}).get("verified_but_wrong_rate", 0.0)
    oracle_rate = latest_benchmark.get("oracle", {}).get("verified_but_wrong_rate", 0.0)

    st.markdown(
        """
        <div class="hero">
          <h1>Verified but Wrong: Intent-Gap Auditing for Vericoding Pipelines</h1>
          <p><strong>A benchmark and pre-selection policy audit gate for specification omission failures.</strong></p>
          <p>Spec-driven code generation can only be as safe as the specification it trusts. This harness checks whether a generated spec omits intent-critical requirements before the pipeline selects an implementation.</p>
        </div>
        <div class="impact-box">
          Generated specs should not be trusted blindly. A Spec Audit Gate can block or escalate incomplete specs before they are used to select verified code.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Deployment Safety Layer")
    st.markdown(
        """
        <div class="safety-diagram">Requirements / LLM-generated spec
        ↓
Spec Audit Gate
        ↓
If ALLOW: implementation selection
If REVIEW/BLOCK: human review or spec repair
        ↓
Hidden oracle evaluation / CI result</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Current Safety Metrics")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total tasks", len(tasks))
    c2.metric("Naive VBW rate", f"{naive_rate:.0%}")
    c3.metric("Critic VBW rate", f"{critic_rate:.0%}")
    c4.metric("Oracle VBW rate", f"{oracle_rate:.0%}")
    c5.metric("Live LLM specs audited", latest_audit.get("valid_specs", 0))
    c6.metric(
        "BLOCK / REVIEW / ALLOW",
        f"{sum(1 for audit in audits if audit.get('risk_level') == 'BLOCK')} / "
        f"{sum(1 for audit in audits if audit.get('risk_level') == 'REVIEW')} / "
        f"{sum(1 for audit in audits if audit.get('risk_level') == 'ALLOW')}",
    )

    st.markdown("### Why the critic is not perfect")
    st.info(
        "`loyalty_refund_reversal` shows the deployment risk: a checklist critic can check refund amounts, "
        "remaining balance, status, and state updates, but still miss organization-specific loyalty point reversal."
    )

    st.markdown("### Live model result")
    st.write(
        "Live LLM-generated specs did not produce verified-but-wrong selections in the current pilot suite. "
        "The audit gate still surfaces missing or unclear requirements as review targets before specs are trusted."
    )

    st.markdown("### CI/CD use case")
    st.write(
        "BLOCK means a critical requirement is missing or selection is verified-but-wrong. REVIEW means a critical "
        "requirement is unclear. ALLOW means no critical gaps were detected by this harness."
    )


def main() -> None:
    initialize_state()
    render_styles()
    tasks = list_tasks()
    render_sidebar(tasks)
    task = load_task(selected_task_id())

    render_impact_header(tasks)

    render_task_overview(task)
    render_pipeline_diagram()

    st.subheader("3. Run demo")
    b1, b2, b3, b4, b5 = st.columns(5)
    b1.button("Run naive AI spec", on_click=run_and_store, args=("naive",), use_container_width=True)
    b2.button("Run critic defense", on_click=run_and_store, args=("critic",), use_container_width=True)
    b3.button("Run oracle spec", on_click=run_and_store, args=("oracle",), use_container_width=True)
    b4.button("Run modes and compare", on_click=run_comparison_and_store, use_container_width=True)
    b5.button("Run mini benchmark", on_click=run_benchmark_and_store, use_container_width=True)

    st.subheader("LLM Spec Experiment")
    st.write(
        "The deterministic benchmark shows the mechanism. This experiment tests whether real "
        "model-generated specs omit the same intent-critical requirements."
    )
    llm_left, llm_right = st.columns(2)
    if llm_left.button("Run real LLM spec experiment", key="main_run_llm", use_container_width=True):
        with st.spinner("Generating and analyzing model-written public specs..."):
            st.session_state.displayed_result = run_llm_spec_experiment(
                num_samples_per_task=int(st.session_state.llm_num_samples),
                model=st.session_state.llm_spec_model,
            )
    if llm_right.button("Load latest LLM spec experiment", key="main_load_llm", use_container_width=True):
        st.session_state.displayed_result = load_latest_llm_spec_experiment()

    compare_left, compare_right = st.columns(2)
    if compare_left.button(
        "Build LLM model comparison from saved runs",
        key="main_build_model_comparison",
        use_container_width=True,
    ):
        st.session_state.displayed_result = build_llm_model_comparison()
    if compare_right.button(
        "Load LLM model comparison",
        key="main_load_model_comparison",
        use_container_width=True,
    ):
        st.session_state.displayed_result = load_llm_model_comparison()

    selection_left, selection_right = st.columns(2)
    if selection_left.button(
        "Run saved LLM specs through selection pipeline",
        key="main_run_llm_selection",
        use_container_width=True,
    ):
        st.session_state.displayed_result = run_saved_llm_spec_selection_experiment()
    if selection_right.button(
        "Load latest LLM selection experiment",
        key="main_load_llm_selection",
        use_container_width=True,
    ):
        st.session_state.displayed_result = load_latest_llm_selection_experiment()

    st.subheader("Spec Audit Gate")
    audit_left, audit_mid, audit_right = st.columns(3)
    if audit_left.button("Run Spec Audit Gate on saved LLM specs", key="main_run_audit_gate", use_container_width=True):
        st.session_state.displayed_result = run_spec_audit_gate_on_saved_llm_specs()
    if audit_mid.button("Load latest Spec Audit Gate", key="main_load_audit_gate", use_container_width=True):
        st.session_state.displayed_result = load_latest_spec_audit_gate()
    if audit_right.button("Generate manual audit worksheet", key="main_manual_audit", use_container_width=True):
        st.session_state.displayed_result = generate_manual_coverage_audit()

    st.subheader("Audit Gate Calibration")
    st.write(
        "The audit gate is useful only if it flags risky specs before implementation selection. "
        "This calibration compares pre-selection audit decisions against downstream verified-but-wrong outcomes."
    )
    cal1, cal2, cal3, cal4 = st.columns(4)
    if cal1.button("Run controlled audit calibration", key="main_run_controlled_calibration", use_container_width=True):
        st.session_state.displayed_result = run_controlled_audit_calibration()
    if cal2.button("Load controlled audit calibration", key="main_load_controlled_calibration", use_container_width=True):
        st.session_state.displayed_result = load_controlled_audit_calibration()
    if cal3.button("Run saved LLM audit calibration", key="main_run_llm_calibration", use_container_width=True):
        st.session_state.displayed_result = run_saved_llm_audit_calibration()
    if cal4.button("Load saved LLM audit calibration", key="main_load_llm_calibration", use_container_width=True):
        st.session_state.displayed_result = load_latest_llm_audit_calibration()

    st.subheader("Research Package")
    r1, r2, r3, r4, r5, r6 = st.columns(6)
    if r1.button("Policy gate", key="main_policy_gate", use_container_width=True):
        st.session_state.displayed_result = run_policy_gate_calibration()
    if r2.button("Repair", key="main_repair", use_container_width=True):
        st.session_state.displayed_result = run_repair_experiment()
    if r3.button("Baselines", key="main_baselines", use_container_width=True):
        st.session_state.displayed_result = run_defense_baselines()
    if r4.button("Ablation", key="main_ablation", use_container_width=True):
        st.session_state.displayed_result = run_audit_gate_ablation()
    if r5.button("Naturalistic", key="main_naturalistic", use_container_width=True):
        st.session_state.displayed_result = run_naturalistic_experiment()
    if r6.button("Stats", key="main_stats", use_container_width=True):
        st.session_state.displayed_result = build_stats_summary()

    result = st.session_state.displayed_result
    if result is None:
        st.info("Run a spec mode, comparison, or mini benchmark to display results.")
    elif result.get("result_type") == "spec_audit_gate":
        render_spec_audit_gate(result)
    elif result.get("result_type") == "manual_coverage_audit":
        render_manual_audit(result)
    elif result.get("result_type") in {"controlled_audit_calibration", "llm_audit_calibration"}:
        render_audit_calibration(result)
    elif result.get("result_type") in {"policy_gate_calibration", "spec_repair_experiment", "defense_baselines", "audit_gate_ablation", "naturalistic_experiment"} or "wilson_95_intervals" in result:
        render_research_artifact(result)
    elif "runs" in result and "verified_but_wrong_count" in str(result.get("models", [])):
        render_llm_selection_experiment(result)
    elif "models" in result and "total_models" in result:
        render_llm_model_comparison(result)
    elif "total_specs" in result or result.get("provider_configured") is False:
        render_llm_spec_experiment(result)
    elif "taxonomy_counts" in result:
        render_benchmark(result)
    elif "naive" in result and "critic" in result:
        render_comparison(result)
    else:
        render_single_result(result)

    render_results_log()


if __name__ == "__main__":
    main()
