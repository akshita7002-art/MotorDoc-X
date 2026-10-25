"""Run a diagnosis. Without arguments it simulates a bearing-fault reading.

Usage:
  python scripts/predict.py                    # demo with simulated reading
  python scripts/predict.py --fault healthy    # healthy | bearing_fault | imbalance | overload
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from motordoc.features import extract_features
from motordoc.model import diagnose, load
from motordoc.simulate import CLASSES, simulate_reading

ap = argparse.ArgumentParser()
ap.add_argument("--fault", default="bearing_fault", choices=CLASSES)
ap.add_argument("--model", default="models/motordoc_rf.joblib")
args = ap.parse_args()

clf = load(args.model)
reading = simulate_reading(args.fault, np.random.default_rng(123))
result = diagnose(clf, extract_features(*reading))
print(json.dumps(result, indent=2))
print(f"\nMotor Health: {result['motor_health']}% | Status: {result['status']} | "
      f"Possible Fault: {result['likely_condition']} | Confidence: {result['confidence']}%")
