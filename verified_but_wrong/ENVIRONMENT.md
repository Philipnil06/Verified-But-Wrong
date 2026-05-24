# Environment

- Python: use the Windows launcher command `py`.
- UI: Streamlit.
- Optional LLM: OpenAI API via `.env`, not required for deterministic reproduction.
- Default reproducibility command: `py run_all_repro.py`.

The deterministic benchmark, policy gate, repair loop, baselines, ablations, naturalistic experiment, and final reports do not make API calls.
