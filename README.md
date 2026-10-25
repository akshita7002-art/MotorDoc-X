# MotorDoc X: AI-Powered Predictive Maintenance

An affordable, portable, multi-sensor predictive maintenance system for **farmers, mechanics, workshops and small industries**.
MotorDoc X listens to and measures a motor (**sound, vibration, temperature, current**), uses AI/ML to detect abnormal conditions,
and reports a simple **Motor Health Score**, a **likely fault** and a **maintenance recommendation**.

> **Project status: working prototype (software pipeline) + reference firmware.**
> The AI pipeline runs end to end today on **simulated** motor data. Hardware firmware is provided as a reference
> template. Real-world motor data collection and validation are the next milestone (see [Roadmap](#roadmap)).
> We do **not** claim real-world accuracy yet.

We are not inventing motor fault detection. We are building an **affordable, portable, multi-sensor implementation** of it for accessible predictive maintenance.

## How it works

```
Machine -> Sensors -> ESP32 -> Data Processing -> AI Model -> Diagnosis
```

| Stage | What happens |
|---|---|
| Sensors | Microphone (sound), accelerometer (vibration), temperature sensor, current sensor |
| ESP32 | Samples the sensors and streams readings (serial / Wi-Fi) |
| Data processing | MFCC / Mel features from sound + RMS, kurtosis, dominant frequency from vibration + temperature + current |
| AI model | Random Forest classifier (CNN on Mel spectrograms planned) |
| Diagnosis | Health Score (0-100), status (GOOD / WARNING / CRITICAL), likely fault, confidence, advice |

Example output:

```
Motor Health: 72% | Status: WARNING | Possible Fault: bearing_fault | Confidence: 89%
```

(Example format only. The exact numbers depend on the reading and model.)

## Repository structure

```
MotorDocX/
├── src/motordoc/          # Core Python package
│   ├── features.py        # MFCC + vibration/temperature/current feature extraction
│   ├── simulate.py        # Simulated motor data generator (healthy + 3 fault types)
│   └── model.py           # Random Forest classifier, Health Score, recommendations
├── scripts/
│   ├── generate_sample_data.py   # Writes data/sample/sample_features.csv
│   ├── train.py                  # Trains and saves the model
│   └── predict.py                # Runs a diagnosis demo
├── firmware/esp32_motordoc/      # ESP32 (Arduino) reference sketch
├── data/sample/                  # Sample data (simulated)
├── tests/test_pipeline.py        # Automated test cases
├── docs/                         # Technical design + data collection guide
├── requirements.txt
└── LICENSE                       # MIT
```

## Setup and run

Requirements: **Python 3.9+**

```bash
# 1. Get the code
git clone https://github.com/YOUR-USERNAME/MotorDocX.git
cd MotorDocX

# 2. (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the model (uses simulated data by default)
python scripts/train.py

# 5. Run a diagnosis demo
python scripts/predict.py --fault bearing_fault
python scripts/predict.py --fault healthy
```

Environment variables: **none required.** (Wi-Fi credentials for the ESP32 are set at the top of the firmware file, never committed with real values.)

## Run the tests

```bash
python -m pytest -q
```

The test cases cover: MFCC output shape, feature-vector length, health-status thresholds, fault separation on simulated data,
and that a healthy motor scores higher than a faulty one.

## Fault classes

| Class | Typical signs the model looks for |
|---|---|
| `healthy` | Normal sound, low vibration, normal temperature/current |
| `bearing_fault` | Broadband/high-frequency sound, spiky vibration (high kurtosis), temperature rise |
| `imbalance` | Strong vibration at shaft frequency, mild temperature rise |
| `overload` | High current and temperature |

## Sample data

`data/sample/sample_features.csv` contains 40 **simulated** feature rows (columns: 13 MFCCs, spectral centroid, vibration RMS,
kurtosis, dominant frequency, temperature, current, `label`). Regenerate with `python scripts/generate_sample_data.py`.
To train on your own recordings, create a CSV with the same columns and run `python scripts/train.py --csv your_data.csv`.

## Important notes on honesty and limits

- All data in this repository is **simulated**. Perfect scores on simulated data do **not** indicate real-world accuracy.
- Acoustic diagnosis can be affected by background noise; real-world validation across multiple motor types is still needed.
- The ESP32 firmware is a reference template and must be calibrated and tested on real hardware.
- MotorDoc X is a decision-support tool. It does not replace a qualified technician's inspection.

## Hardware (target prototype cost: about ₹1,500, estimate)

ESP32 board, microphone module, MPU6050 accelerometer, DS18B20 temperature sensor, current sensor module (e.g. ACS712), SSD1306 OLED display.
See [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md) for wiring and architecture.

## Roadmap

- [x] Feature extraction, classifier, health score and recommendation engine
- [x] Simulated data generator and automated tests
- [x] ESP32 reference firmware
- [ ] Collect real data from pumps and motors (healthy and faulty)
- [ ] Noise-robust model and CNN on Mel spectrograms
- [ ] Mobile app and cloud monitoring
- [ ] Regional-language voice alerts
- [ ] Remaining Useful Life prediction, maintenance history, offline AI on device
- [ ] Support for more machine types

## SDG alignment

SDG 9 (Industry, Innovation and Infrastructure), SDG 12 (Responsible Consumption and Production), SDG 8 (Decent Work and Economic Growth).

## License

Released under the [MIT License](LICENSE).
