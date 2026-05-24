# Verified But Wrong

Vericoding can prove that code satisfies a formal specification. But it cannot prove that the specification was the right target.

GitHub repository: https://github.com/Philipnil06/Verified-But-Wrong

Paper draft: `verified_but_wrong/results/final_submission_paper.md` (replace with PDF path once exported)

Demo source: `demo/`

Live demo: [INSERT VERCEL URL AFTER DEPLOYMENT]

## Key Counts

- 11 validated demonstrations
- 3 Tier 1 direct-Dafny cases
- 8 Tier 2 adapted demonstrations
- 3 repaired-target blocks

## Quick Reproduction

```bash
python run_all_repro.py
python run_external_replication.py
```

External benchmark data is not vendored. To reproduce the external scan/inventory steps, clone the benchmark at the pinned commit using the commands in `verified_but_wrong/external_data/README.md`.

## Try The Demo Locally

```bash
cd demo
npm install
npm run dev
```

## Deploy Demo On Vercel

- Root Directory: `demo`
- Framework Preset: `Vite`
- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: `dist`

## Large Generated Artifacts

Very large generated artifacts such as full raw JSONL files, local tool binaries, and large noisy-policy evaluation JSON files are excluded from the latest repository state to keep cloning fast and avoid GitHub size warnings. Reported metrics are preserved in summary artifacts and can be regenerated with the reproduction scripts.
