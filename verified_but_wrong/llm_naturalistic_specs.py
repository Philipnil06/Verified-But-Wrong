from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Optional LLM naturalistic spec experiment.")
    parser.add_argument("--run-api", default="false", choices=["true", "false"])
    args = parser.parse_args()
    if args.run_api != "true":
        print("No API calls made. Re-run with --run-api true to enable optional live generation.")
        return
    raise SystemExit("Live naturalistic LLM generation is intentionally not enabled by default in this prototype.")


if __name__ == "__main__":
    main()
