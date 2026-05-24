# Final Paper Rewrite Inputs

## 1. Dafny installation

- install method: local .NET SDK bootstrap (`.tools/dotnet-install.ps1`) to `C:\vbw-dotnet-sdk`, then local .NET tool manifest in repo (`.config/dotnet-tools.json`) with Dafny local tool.
- exact Dafny version: `4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2`
- commands run:
  - `dotnet --version`
  - `dotnet --info`
  - `dafny --version`
  - `dotnet tool run dafny --version`
  - `powershell -ExecutionPolicy Bypass -File .tools/dotnet-install.ps1 -Channel 8.0 -InstallDir C:\vbw-dotnet-sdk -NoPath`
  - `C:\vbw-dotnet-sdk\dotnet.exe new tool-manifest`
  - `C:\vbw-dotnet-sdk\dotnet.exe tool install Dafny --version 4.11.0`
  - `C:\vbw-dotnet-sdk\dotnet.exe tool restore`
  - `C:\vbw-dotnet-sdk\dotnet.exe tool run dafny --version`
  - solver dependency for verification: downloaded local `z3-4.12.1-x64-win` into `.tools/z3/.../bin`
- success/failure: success (Dafny local tool installed and callable).

Reference:
- `reports/dafny_install_attempt.md`
- `reports/dafny_install_attempt.json`

## 2. Direct Dafny status

- DA0003: `direct_dafny_verified_and_intent_failed`
  - verify command: `dotnet tool run dafny verify external_vericoding_cases/candidate_DA0003/dafny_direct/bad_candidate.dfy`
  - verify return code: `0`
  - verifier summary: `Dafny program verifier finished with 2 verified, 0 errors`
- DA0208: `direct_dafny_verified_and_intent_failed`
  - verify command: `dotnet tool run dafny verify external_vericoding_cases/candidate_DA0208/dafny_direct/bad_candidate.dfy`
  - verify return code: `0`
  - verifier summary: `Dafny program verifier finished with 5 verified, 0 errors`
- direct_dafny_verified_count: `2`

References:
- `reports/external_vericoding_direct_dafny.json`
- `reports/external_vericoding_direct_dafny.md`

## 3. Allowed paper claims

- allowed abstract/conclusion sentence (DA0003):
  - “For DA0003, we additionally implemented a trivially wrong Dafny candidate that verifies directly against the original benchmark target while failing intended-behavior examples.”
- allowed sentence (DA0208):
  - “DA0208 provides a second direct-Dafny case: a return-0 implementation verifies against the original target but fails minimum-box-size examples.”
- limitation sentence (if needed globally):
  - “These direct-Dafny results are case studies and should not be interpreted as a prevalence estimate across the full benchmark.”

## 4. Updated caveats

- no prevalence estimate.
- not a benchmark-bug claim.
- direct-Dafny wording is used only for cases with successful Dafny verification runs.
- other external cases remain adapted executable demonstrations.
