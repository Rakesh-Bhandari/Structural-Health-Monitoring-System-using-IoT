/* ============================================================
   ESP32 Bridge Health Monitoring System
   - MPU6050 Accelerometer for vibration detection
   - High-frequency sampling for crack detection
   - CSV output format for data logging
   ============================================================ */

#include <Wire.h>
#include "MPU6050_light.h"

MPU6050 mpu(Wire);

// ========== PIN CONFIGURATION ==========
const int SDA_PIN = 21;
const int SCL_PIN = 22;
const int LED_PIN = 2;  // Built-in LED for status

// ========== SAMPLING CONFIGURATION ==========
const unsigned long SAMPLE_HZ = 500;        // 500 Hz sampling
const int RMS_WINDOW = 10;                  // Rolling RMS window
const float VIBRATION_THRESHOLD = 0.15;     // Alert threshold

// ========== STATE VARIABLES ==========
float sqBuf[RMS_WINDOW] = {0};
int bufIndex = 0;
int filledSamples = 0;
unsigned long lastBlinkTime = 0;
bool ledState = false;

// Statistics
unsigned long totalSamples = 0;
unsigned long alertCount = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  delay(100);

  // Initialize I2C
  Wire.begin(SDA_PIN, SCL_PIN, 400000); // 400 kHz for faster communication
  delay(50);

  // Initialize MPU6050
  byte status = mpu.begin();
  if (status != 0) {
    Serial.println("ERROR: MPU6050 connection failed!");
    while (1) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      delay(200);
    }
  }

  // Calibrate MPU6050
  Serial.println("=== Bridge Health Monitoring System ===");
  Serial.println("Calibrating MPU6050... Keep sensor stable!");
  delay(1000);
  mpu.calcOffsets();
  Serial.println("Calibration complete!");
  
  // Configure MPU6050 for high sensitivity
  mpu.setFilterGyroCoef(0.98); // Optimize for vibration detection
  
  delay(500);
  Serial.println("\n--- CSV DATA START ---");
  Serial.println("timestamp_ms,RMS,accel_magnitude,status");
  
  // Blink LED to indicate ready
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}

void loop() {
  static unsigned long nextSampleUs = 0;
  unsigned long nowUs = micros();
  
  if (nextSampleUs == 0) nextSampleUs = nowUs;

  // Precise timing for consistent sampling
  if ((long)(nowUs - nextSampleUs) >= 0) {
    // Read accelerometer data
    mpu.update();
    float ax = mpu.getAccX();
    float ay = mpu.getAccY();
    float az = mpu.getAccZ();

    // Calculate total acceleration magnitude
    float mag = sqrt(ax*ax + ay*ay + az*az);
    
    // Remove gravity component (dynamic acceleration)
    float magDyn = fabs(mag - 1.0f);

    // Update rolling RMS buffer
    sqBuf[bufIndex] = magDyn * magDyn;
    bufIndex = (bufIndex + 1) % RMS_WINDOW;
    if (filledSamples < RMS_WINDOW) filledSamples++;

    // Calculate RMS value
    float sumSq = 0.0f;
    for (int i = 0; i < filledSamples; i++) {
      sumSq += sqBuf[i];
    }
    float rms = sqrt(sumSq / (float)filledSamples);

    // Determine status
    String status = "NORMAL";
    if (rms > VIBRATION_THRESHOLD) {
      status = "ALERT";
      alertCount++;
      
      // Blink LED on alert
      if (millis() - lastBlinkTime > 200) {
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
        lastBlinkTime = millis();
      }
    } else {
      digitalWrite(LED_PIN, LOW);
      ledState = false;
    }

    // Output CSV format: timestamp, RMS, magnitude, status
    Serial.printf("%lu,%.5f,%.5f,%s\n", 
                  millis(), 
                  rms, 
                  mag,
                  status.c_str());

    totalSamples++;

    // Schedule next sample (precise timing)
    nextSampleUs += 1000000UL / SAMPLE_HZ;
    
    // Prevent drift if we missed a sample
    if ((long)(micros() - nextSampleUs) > (long)(1000000UL / SAMPLE_HZ)) {
      nextSampleUs = micros();
    }
    
  } else {
    // Minimal delay to prevent watchdog reset
    delayMicroseconds(10);
  }

  // Optional: Print statistics every 10 seconds
  static unsigned long lastStatsTime = 0;
  if (millis() - lastStatsTime > 10000) {
    Serial.printf("# STATS: Samples=%lu, Alerts=%lu, Runtime=%lus\n",
                  totalSamples, alertCount, millis()/1000);
    lastStatsTime = millis();
  }
}