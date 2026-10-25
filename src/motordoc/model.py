"""Fault classifier (Random Forest) + Motor Health Score + recommendations."""
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# How much each fault reduces the health score (0 = none, 1 = maximum)
SEVERITY = {"healthy": 0.0, "bearing_fault": 0.85, "imbalance": 0.6, "overload": 0.7}

RECOMMENDATION = {
    "healthy": "Motor is running normally. Continue routine checks.",
    "bearing_fault": "Possible bearing abnormality. Inspect/lubricate or replace bearing soon.",
    "imbalance": "Possible shaft/rotor imbalance. Check coupling, mounting and balance.",
    "overload": "Motor appears overloaded or overheating. Reduce load and check ventilation.",
}


def train(X, y, seed=42):
    clf = RandomForestClassifier(n_estimators=200, random_state=seed)
    clf.fit(X, y)
    return clf


def health_status(score):
    if score >= 80:
        return "GOOD"
    if score >= 50:
        return "WARNING"
    return "CRITICAL"


def diagnose(clf, features):
    """Return dict: health score (0-100), status, likely fault, confidence, advice."""
    proba = clf.predict_proba(np.asarray(features).reshape(1, -1))[0]
    classes = list(clf.classes_)
    top = int(np.argmax(proba))
    expected_penalty = sum(p * SEVERITY.get(c, 0.5) for c, p in zip(classes, proba))
    score = round(100 * (1 - expected_penalty))
    fault = classes[top]
    return {
        "motor_health": score,
        "status": health_status(score),
        "likely_condition": fault,
        "confidence": round(float(proba[top]) * 100),
        "recommendation": RECOMMENDATION.get(fault, "Inspect the machine."),
    }


def save(clf, path):
    joblib.dump(clf, path)


def load(path):
    return joblib.load(path)
