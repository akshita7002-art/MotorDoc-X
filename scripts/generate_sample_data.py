"""Create data/sample/sample_features.csv from SIMULATED readings."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from motordoc.features import FEATURE_NAMES
from motordoc.simulate import make_dataset

X, y = make_dataset(n_per_class=10, seed=7)
df = pd.DataFrame(X, columns=FEATURE_NAMES).round(4)
df["label"] = y
out = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "sample_features.csv")
df.to_csv(out, index=False)
print(f"Wrote {len(df)} rows to {out}")
