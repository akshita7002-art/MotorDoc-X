# Collecting Real Data (next milestone)

The model currently trains on simulated data. To make it real:

1. **Pick machines**: start with 1-2 motors (for example a water pump and a workshop motor) in known-good condition.
2. **Record healthy baseline**: at least 100 one-second readings per machine, at normal load.
3. **Record fault conditions safely** (with supervision): for example added load (overload), a small weight on the rotor (imbalance),
   or a known worn bearing from a workshop (bearing fault). Never damage equipment or compromise safety.
4. **Vary conditions**: different loads, times of day and background noise levels.
5. **Log each reading** as one CSV row: the 19 feature columns in `src/motordoc/features.py` (`FEATURE_NAMES`) plus a `label` column.
6. **Train and evaluate**: `python scripts/train.py --csv your_data.csv`. Always test on a machine or session the model has not seen.
7. **Report honestly**: record accuracy per motor type and noise level.
