import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from sklearn.model_selection import train_test_split
from motordoc.features import FEATURE_NAMES, extract_features, mfcc
from motordoc.model import diagnose, health_status, train
from motordoc.simulate import make_dataset, simulate_reading


def test_mfcc_shape():
    assert mfcc(np.random.randn(8000)).shape == (13,)


def test_feature_vector_length():
    r = simulate_reading("healthy", np.random.default_rng(0))
    assert len(extract_features(*r)) == len(FEATURE_NAMES)


def test_health_status_thresholds():
    assert health_status(95) == "GOOD"
    assert health_status(65) == "WARNING"
    assert health_status(20) == "CRITICAL"


def test_model_separates_simulated_faults():
    X, y = make_dataset(n_per_class=40, seed=1)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
    clf = train(Xtr, ytr)
    assert (clf.predict(Xte) == yte).mean() > 0.9


def test_healthy_scores_higher_than_faulty():
    X, y = make_dataset(n_per_class=40, seed=2)
    clf = train(X, y)
    rng = np.random.default_rng(5)
    h = diagnose(clf, extract_features(*simulate_reading("healthy", rng)))
    b = diagnose(clf, extract_features(*simulate_reading("bearing_fault", rng)))
    assert h["motor_health"] > b["motor_health"]
    assert b["likely_condition"] == "bearing_fault"
