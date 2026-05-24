#!/usr/bin/env python3
"""Write a small contextual report about public vericoding issue #314."""
from __future__ import annotations

from common import REPORTS, write_text


def main() -> int:
    text = """# External Vericoding Known-Issue Context

This report is non-core supporting context. It should not be counted as a main Dafny result unless the related task is directly analyzed and validated.

## GitHub issue #314

- Title: Partial Verus specifications at Verina Advanced 77 allow cheating
- Source: https://github.com/Beneficial-AI-Foundation/vericoding/issues/314
- Summary: The public issue describes an over-relaxed Verus specification for a rain-water trapping task where the postcondition only requires a non-negative result.
- Weak-spec pattern: `ensures result >= 0`
- Relevance: This supports the plausibility that formal verification targets can be too weak relative to task intent, which is the target-validity failure mode audited here.
- Caveat: This is Verus, not Dafny. It is not part of the main validated Dafny audit unless the corresponding task is included in the external dataset and manually validated.

Suggested cautious discussion sentence:

> A similar over-relaxed-spec issue has been raised publicly in the vericoding repository, reinforcing that weak formal targets are a recognized benchmark concern.
"""
    write_text(REPORTS / "external_vericoding_known_issue_context.md", text)
    print(f"Wrote {REPORTS / 'external_vericoding_known_issue_context.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
