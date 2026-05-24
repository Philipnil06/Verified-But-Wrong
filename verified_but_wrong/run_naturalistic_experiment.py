from naturalistic_experiment import run_naturalistic_experiment

if __name__ == "__main__":
    result = run_naturalistic_experiment()
    print({k: result[k] for k in ["naturalistic_docs_evaluated", "vbw_before", "vbw_after_repair", "dangerous_docs_allowed"]})
