# Firmware notes

`esp32_motordoc/esp32_motordoc.ino` is a **reference sketch**. Open it in the Arduino IDE (ESP32 board package installed),
install the libraries listed at the top of the file, set the calibration constants for your sensors, and upload.

It prints one JSON line per second over Serial (115200 baud) in the format shown in `data/sample/sample_reading.json`.
A host script can read those lines, call `extract_features(...)` and `diagnose(...)` from `src/motordoc/`.

Status: not yet field-tested. Treat pins and scaling as starting points.
