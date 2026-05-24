"""Metric definitions for Verified but Wrong reports.

VBW = Pass(public_spec, selected_impl) AND Fail(hidden_oracle, selected_impl)
VBW rate = verified_but_wrong selections / total selections
Dangerous escape rate = dangerous specs with pre_selection_decision == ALLOW / dangerous specs
Safe allow rate = safe specs with pre_selection_decision == ALLOW / safe specs
Review burden = specs escalated to REVIEW or BLOCK, reported separately for safe and dangerous specs
Repair success rate = (VBW before repair - VBW after repair) / VBW before repair
High/critical catch rate = high_or_critical_dangerous_caught / high_or_critical_dangerous_total
Policy coverage rate = covered policy cards / total relevant policy cards
Critical coverage rate = covered high/critical policy cards / total high/critical policy cards
"""

from __future__ import annotations


def rate(numerator: int, denominator: int, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default
