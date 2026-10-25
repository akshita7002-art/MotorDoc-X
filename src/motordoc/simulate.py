"""Synthetic motor data generator.

IMPORTANT: this data is SIMULATED to let the pipeline be developed and tested
without hardware. Replace/extend it with real recordings from MotorDoc X
(see docs/DATA_COLLECTION.md) before making any accuracy claims.
"""
import numpy as np
from .features import AUDIO_FS, VIB_FS, extract_features

CLASSES = ["healthy", "bearing_fault", "imbalance", "overload"]
DURATION = 1.0  # seconds per sample


def simulate_reading(fault, rng):
    """Return (audio, vib, temp_c, current_a) for one 1-second reading."""
    ta = np.arange(int(AUDIO_FS * DURATION)) / AUDIO_FS
    tv = np.arange(int(VIB_FS * DURATION)) / VIB_FS
    rot = rng.uniform(24, 26)  # shaft frequency (~1500 rpm)

    audio = 0.5 * np.sin(2 * np.pi * 100 * ta) + 0.2 * np.sin(2 * np.pi * 200 * ta)
    audio += 0.05 * rng.standard_normal(len(ta))
    vib = 0.3 * np.sin(2 * np.pi * rot * tv) + 0.05 * rng.standard_normal(len(tv))
    temp, cur = rng.normal(45, 2), rng.normal(3.0, 0.15)

    if fault == "bearing_fault":
        # periodic high-frequency impacts -> broadband sound + spiky vibration
        for t0 in np.arange(0, DURATION, 1 / (3.5 * rot)):
            i = int(t0 * AUDIO_FS)
            n = min(60, len(audio) - i)
            audio[i:i + n] += 0.8 * rng.standard_normal(n) * np.exp(-np.arange(n) / 15)
            j = int(t0 * VIB_FS)
            if j < len(vib):
                vib[j] += rng.uniform(1.0, 1.8)
        audio += 0.2 * np.sin(2 * np.pi * 2500 * ta)
        temp += rng.normal(10, 2)
        cur += rng.normal(0.4, 0.1)
    elif fault == "imbalance":
        vib += 1.2 * np.sin(2 * np.pi * rot * tv)          # strong 1x component
        audio += 0.3 * np.sin(2 * np.pi * rot * 4 * ta)
        temp += rng.normal(4, 1.5)
    elif fault == "overload":
        cur += rng.normal(2.0, 0.3)
        temp += rng.normal(18, 3)
        audio += 0.3 * rng.standard_normal(len(ta))
        vib += 0.2 * rng.standard_normal(len(tv))
    return audio, vib, float(temp), float(cur)


def make_dataset(n_per_class=60, seed=42):
    rng = np.random.default_rng(seed)
    X, y = [], []
    for label in CLASSES:
        for _ in range(n_per_class):
            X.append(extract_features(*simulate_reading(label, rng)))
            y.append(label)
    return np.array(X), np.array(y)
