from spec_audit_calibration import run_policy_gate_calibration

if __name__ == "__main__":
    result = run_policy_gate_calibration()
    print(result["metrics"])
