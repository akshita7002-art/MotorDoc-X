/*
 * MotorDoc X - ESP32 reference firmware (Arduino IDE)
 *
 * STATUS: reference template. Not yet calibrated or field-tested. Verify pins,
 * sensor scaling and safety before use on a real machine.
 *
 * Reads: microphone (ADC), MPU6050 (I2C), DS18B20 (1-Wire), current sensor (ADC)
 * Sends: one JSON line per ~1 s reading over Serial (115200 baud)
 * Shows: temperature and current on an SSD1306 OLED
 *
 * Libraries (Arduino Library Manager):
 *   OneWire, DallasTemperature, Adafruit SSD1306, Adafruit GFX
 */
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ---------- Pins ----------
#define MIC_PIN      34   // analog microphone module output
#define CURRENT_PIN  35   // current sensor analog output
#define ONE_WIRE_PIN 4    // DS18B20 data

// ---------- Sampling ----------
const int AUDIO_FS = 8000;        // Hz
const int VIB_FS   = 1000;        // Hz
const int AUDIO_N  = 8000;        // 1 second
const int VIB_N    = 1000;        // 1 second

// ---------- Calibration (adjust for your sensors) ----------
const float ADC_VREF       = 3.3;
const float CURRENT_ZERO_V = 1.65;   // sensor output at 0 A
const float CURRENT_V_PER_A = 0.100; // e.g. ACS712-20A = 100 mV/A (after any divider)

const uint8_t MPU_ADDR = 0x68;

OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature tempSensor(&oneWire);
Adafruit_SSD1306 display(128, 64, &Wire, -1);

static int16_t vibBuf[VIB_N];
static uint16_t audioBuf[AUDIO_N];

int16_t readMpuAccelZ() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3F);                       // ACCEL_ZOUT_H
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, (uint8_t)2);
  int16_t hi = Wire.read();
  int16_t lo = Wire.read();
  return (hi << 8) | lo;
}

float readCurrentA() {
  // RMS of AC current over ~100 ms (50 Hz mains -> 5 cycles)
  const int N = 500;
  double sumSq = 0;
  for (int i = 0; i < N; i++) {
    float v = analogRead(CURRENT_PIN) * ADC_VREF / 4095.0;
    float a = (v - CURRENT_ZERO_V) / CURRENT_V_PER_A;
    sumSq += a * a;
    delayMicroseconds(200);
  }
  return sqrt(sumSq / N);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  Wire.beginTransmission(MPU_ADDR);       // wake MPU6050
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  tempSensor.begin();
  display.begin(SSD1306_SWITCHCAPACITANCE_CHARGEPUMP, 0x3C);
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("MotorDoc X");
  display.display();
}

void loop() {
  // 1) Sound: 8 kHz for 1 s
  unsigned long t0 = micros();
  for (int i = 0; i < AUDIO_N; i++) {
    audioBuf[i] = analogRead(MIC_PIN);
    while (micros() - t0 < (unsigned long)(i + 1) * (1000000UL / AUDIO_FS)) {}
  }

  // 2) Vibration: 1 kHz for 1 s
  t0 = micros();
  for (int i = 0; i < VIB_N; i++) {
    vibBuf[i] = readMpuAccelZ();
    while (micros() - t0 < (unsigned long)(i + 1) * (1000000UL / VIB_FS)) {}
  }

  // 3) Temperature and current
  tempSensor.requestTemperatures();
  float tempC = tempSensor.getTempCByIndex(0);
  float currentA = readCurrentA();

  // 4) Send as one JSON line (convert ADC counts to centred values on the host)
  Serial.print("{\"audio_fs\":8000,\"vib_fs\":1000,\"audio\":[");
  for (int i = 0; i < AUDIO_N; i++) { Serial.print((audioBuf[i] - 2048) / 2048.0, 4); if (i < AUDIO_N - 1) Serial.print(','); }
  Serial.print("],\"vibration\":[");
  for (int i = 0; i < VIB_N; i++) { Serial.print(vibBuf[i] / 16384.0, 4); if (i < VIB_N - 1) Serial.print(','); }
  Serial.print("],\"temperature_c\":"); Serial.print(tempC, 1);
  Serial.print(",\"current_a\":"); Serial.print(currentA, 2);
  Serial.println("}");

  // 5) OLED
  display.clearDisplay();
  display.setCursor(0, 0);  display.println("MotorDoc X");
  display.setCursor(0, 20); display.print("Temp: ");  display.print(tempC, 1);    display.println(" C");
  display.setCursor(0, 34); display.print("Curr: ");  display.print(currentA, 2); display.println(" A");
  display.display();
}
