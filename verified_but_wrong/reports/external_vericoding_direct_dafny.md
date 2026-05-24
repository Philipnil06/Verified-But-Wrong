# External Vericoding Direct Dafny Attempts

- dataset: `C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_data\vericoding-benchmark\jsonl\dafny_tasks.jsonl`

| Case | Status | Verify command | Return code | Intended examples all pass |
|---|---|---|---:|---|
| DA0003 | direct_dafny_verified_and_intent_failed | `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0003\dafny_direct\bad_candidate.dfy` | 0 | False |
| DA0208 | direct_dafny_verified_and_intent_failed | `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0208\dafny_direct\bad_candidate.dfy` | 0 | False |

Caveat: this report does not claim benchmark bugs, vulnerabilities, or prevalence.
Direct-Dafny claims are emitted only when Dafny verification actually succeeds.
