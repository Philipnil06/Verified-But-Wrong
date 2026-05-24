# Payment Webhook Hard-Mode Report

## Deterministic Payment Result

- Naive public spec selects `impl_1_happy_path_only.py` and is verified-but-wrong.
- Critic public spec selects `impl_2_correct.py` and passes the hidden oracle.

## LLM Generated Spec Coverage for Payment

| model | valid specs | exact missing idempotency | unclear idempotency | did not clearly mention idempotency |
|---|---:|---:|---:|---:|
| `gpt-5.4-mini` | 5 | 0 | 0 | 0 |
| `gpt-5-nano` | 5 | 0 | 0 | 0 |

## LLM Spec -> Selection Result

| model | verified_but_wrong_count | hidden_oracle_pass_rate | selected candidates |
|---|---:|---:|---|
| `gpt-5.4-mini` | 0 | 1.0000 | {'impl_2_correct.py': 5} |
| `gpt-5-nano` | 0 | 1.0000 | {'impl_2_correct.py': 5} |

## Verified-But-Wrong Examples

No live verified-but-wrong examples were found for the saved payment LLM specs. The generated specs selected candidates that passed the hidden oracle in this harness.

## Interesting Generated Spec Excerpts

### gpt-5.4-mini sample 1
- idempotency coverage status: `covered`
- evidence: idempotent, idempotency, already processed

```text
Implement `process_payment_event` to handle a payment webhook event exactly once per unique event identifier. The function accepts a payment event containing at minimum: an event ID, merchant ID, payment status, and amount. If the event indicates a successful payment, the merchant’s balance must be increased by the event amount. If the event indicates a failed payment, the merchant’s balance must not be increased. The function must be idempotent: reprocessing the same successful or failed event ID must not change balances more than once and must return a result indicating the event was already processed or otherwise ignored. The function must validate input before applying any state change. ...
```

### gpt-5-nano sample 1
- idempotency coverage status: `covered`
- evidence: idempotent, idempotency

```text
Spec: Payment webhook idempotency for process_payment_event Description A function process_payment_event(event) processes payment webhook events to update merchant balances. On a successful payment event, the merchant balance is increased by the event amount. On a failed payment event, the balance is not changed. The function must be idempotent for retry-safe webhook delivery. Inputs - event: PaymentEvent - id: string — unique webhook event identifier (per source) used for idempotency - merchant_id: string — target merchant - amount: number (positive, in minor currency unit, e.g., cents) - status: string ('succeeded' | 'failed' | 'pending' | other) where 'succeeded' indicates a successful pa...
```

## Limitations

- The LLM-visible payment intent intentionally omits idempotency and duplicate-event terminology.
- Coverage classification is rule-based.
- Requirement-to-test mapping is manually curated.
- This is a controlled harness, not an automatic spec compiler.
- No LLM-generated text is executed as code.