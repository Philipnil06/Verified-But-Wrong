from audit_gate_ablation import run_audit_gate_ablation

if __name__ == "__main__":
    result = run_audit_gate_ablation()
    print(result["variants"])
