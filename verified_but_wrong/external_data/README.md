# External benchmark data

This project expects a local checkout of:

https://github.com/Beneficial-AI-Foundation/vericoding-benchmark

Pinned commit:

349ee510deeb6e15e1eb0d98174914e7093252fd

Setup:

```bash
git clone https://github.com/Beneficial-AI-Foundation/vericoding-benchmark verified_but_wrong/external_data/vericoding-benchmark
cd verified_but_wrong/external_data/vericoding-benchmark
git checkout 349ee510deeb6e15e1eb0d98174914e7093252fd
```

The main required file for the external audit is:

`jsonl/dafny_tasks.jsonl`

The external benchmark is not vendored to keep this repository small and avoid broken embedded git repositories.
