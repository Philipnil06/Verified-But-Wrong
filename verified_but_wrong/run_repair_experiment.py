from spec_repair import run_repair_experiment

if __name__ == "__main__":
    result = run_repair_experiment()
    print(result["summaries"])
