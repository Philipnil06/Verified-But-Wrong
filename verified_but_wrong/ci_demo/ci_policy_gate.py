from __future__ import annotations

import argparse
import json
from pathlib import Path


def audit(spec_path: Path, policy_path: Path) -> int:
    spec = spec_path.read_text(encoding="utf-8").lower()
    pack = json.loads(policy_path.read_text(encoding="utf-8"))
    missing = []
    for card in pack.get("policy_cards", []):
        if not any(keyword.lower() in spec for keyword in card.get("keywords", [])):
            missing.append(card)
    if missing:
        print("BLOCK: missing critical policy requirement")
        for card in missing:
            print(f"policy_id: {card['id']}")
            print(f"severity: {card['severity']}")
            print("reason: public spec does not mention reversal of dependent loyalty points")
            print(f"suggested_patch: {card['suggested_spec_patch']}")
        return 1
    print("ALLOW")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--policy", required=True)
    args = parser.parse_args()
    return audit(Path(args.spec), Path(args.policy))


if __name__ == "__main__":
    raise SystemExit(main())
