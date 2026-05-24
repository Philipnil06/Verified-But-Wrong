# Evidence Pack

## Main Benchmark
- executable tasks: 12
- naive VBW: 12/12
- critic VBW: 5/12
- oracle VBW: 0/12

## Candidate-Set Underconstraint
- naive: mean risk=0.74, existence risk tasks=12/12, selected VBW=12/12
- critic: mean risk=0.29, existence risk tasks=5/12, selected VBW=5/12
- oracle: mean risk=0.00, existence risk tasks=0/12, selected VBW=0/12
- repaired_naive: mean risk=0.25, existence risk tasks=6/12, selected VBW=0/12
- repaired_critic: mean risk=0.25, existence risk tasks=6/12, selected VBW=0/12

## Gate Calibration
- dangerous caught: 17
- dangerous allowed: 0
- safe allow rate: 0.7894736842105263

## Noisy Policy-Pack Robustness
- clean: dangerous allowed=0, safe allow rate=78.95%, causal@1=6
- noisy_5x: dangerous allowed=0, safe allow rate=78.95%, causal@1=6
- noisy_10x: dangerous allowed=0, safe allow rate=78.95%, causal@1=6
- noisy_50x: dangerous allowed=0, safe allow rate=78.95%, causal@1=6
- incomplete_25: dangerous allowed=0, safe allow rate=78.95%, causal@1=5
- incomplete_50: dangerous allowed=2, safe allow rate=78.95%, causal@1=3
- outdated_wording: dangerous allowed=0, safe allow rate=0.00%, causal@1=9
- noisy_10x_plus_outdated: dangerous allowed=0, safe allow rate=0.00%, causal@1=9

## Repair Baselines
- no_repair: naive after=12, critic after=5
- generic_repair: naive after=11, critic after=5
- checklist_repair: naive after=10, critic after=5
- policy_targeted_repair: naive after=0, critic after=0
- oracle_repair: naive after=0, critic after=0

## LLM Policy-Split
- status: partial_cached_coverage
- ticket_only: valid=12, omitted causal=0, selected VBW=0
- ticket_plus_generic_checklist: valid=12, omitted causal=0, selected VBW=0
- ticket_plus_retrieved_policy: valid=12, omitted causal=0, selected VBW=0
- oracle_full: valid=12, omitted causal=0, selected VBW=0

## External Issue Suite
- kibana_role_downgrade_session_invalidation: before repair VBW=True, gate=BLOCK, after repair VBW=False
- prisma_tenant_isolation_export: before repair VBW=True, gate=REVIEW, after repair VBW=False
- vendure_invoice_cancellation_stock_restore: before repair VBW=True, gate=REVIEW, after repair VBW=False
- woocommerce_payment_webhook_idempotency: before repair VBW=True, gate=REVIEW, after repair VBW=False

## Formal Demo
- status: skipped_dafny_not_installed

## External Vericoding Benchmark Audit
- data status: available
- dataset schema/path: C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_data\vericoding-benchmark\jsonl\dafny_tasks.jsonl
- commit/hash: 349ee510deeb6e15e1eb0d98174914e7093252fd
- records inspected: 2334
- useful NL descriptions: 1448
- candidate gaps: 128
- validated cases: 7
- paper-ready: True
- caveat: candidate scan is not validation and not a prevalence estimate.