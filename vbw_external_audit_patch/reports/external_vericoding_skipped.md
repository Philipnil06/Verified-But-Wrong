# External Vericoding Audit Skipped

External vericoding data unavailable after local, git, and raw fallback attempts.

This skip is intentionally soft-failing: unrelated internal reproduction steps should still run.

## Supported local data paths

- `/mnt/data/vbw_external_audit_patch/external_data/vericoding-benchmark/jsonl/dafny_tasks.jsonl`
- `/mnt/data/vbw_external_audit_patch/external_data/vericoding/benchmarks/dafny_tasks.jsonl`

## Metadata

```json
{
  "status": "skipped",
  "reason": "External vericoding data unavailable after local, git, and raw fallback attempts.",
  "dataset": {
    "status": "skipped",
    "reason": "External vericoding data unavailable after local, git, and raw fallback attempts.",
    "attempts": [
      {
        "repo_name": "vericoding-benchmark",
        "method": "git",
        "ok": false,
        "message": "Cloning into '/mnt/data/vbw_external_audit_patch/external_data/vericoding-benchmark'...\nfatal: unable to access 'https://github.com/Beneficial-AI-Foundation/vericoding-benchmark/': Could not resolve host: github.com\n"
      },
      {
        "repo_name": "vericoding",
        "method": "git",
        "ok": false,
        "message": "Cloning into '/mnt/data/vbw_external_audit_patch/external_data/vericoding'...\nfatal: unable to access 'https://github.com/Beneficial-AI-Foundation/vericoding/': Could not resolve host: github.com\n"
      },
      {
        "repo_name": "vericoding-benchmark",
        "method": "raw",
        "ok": false,
        "message": "<urlopen error [Errno -3] Temporary failure in name resolution>"
      },
      {
        "repo_name": "vericoding",
        "method": "raw",
        "ok": false,
        "message": "<urlopen error [Errno -3] Temporary failure in name resolution>"
      }
    ]
  }
}
```
