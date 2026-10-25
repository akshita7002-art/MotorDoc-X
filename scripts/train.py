"""Train the fault classifier and save it to models/motordoc_rf.joblib.

Usage:
  python scripts/train.py                      # uses simulated data
  python scripts/train.py --csv my_data.csv    # uses your real data (same columns + 'label')
"""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from motordoc.features import FEATURE_NAMES
from motordoc.model import save, train
from motordoc.simulate import make_dataset

ap = argparse.ArgumentParser()
ap.add_argument("--csv", help="CSV with feature columns + 'label'")
args = ap.parse_args()

if args.csv:
    df = pd.read_csv(args.csv)
    X, y = df[FEATURE_NAMES].values, df["label"].values
    print("Using real/user data:", args.csv)
else:
    X, y = make_dataset(n_per_class=60)
    print("Using SIMULATED data (not real motor recordings).")

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=1)
clf = train(Xtr, ytr)
print(classification_report(yte, clf.predict(Xte)))
os.makedirs("models", exist_ok=True)
save(clf, "models/motordoc_rf.joblib")
print("Model saved to models/motordoc_rf.joblib")
