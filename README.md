# 🚧 Advanced Structural Health Monitoring System using Modal Analysis

> An IoT-based Structural Health Monitoring (SHM) system that uses vibration analysis, modal analysis, and signal processing to detect structural damage in bridges and civil infrastructure.

![Dashboard](Advanced_Structural_Health_Monitoring.png)

---

## 📖 Overview

Structural Health Monitoring (SHM) is an essential technique for ensuring the safety and reliability of bridges and other civil structures.

This project uses an **ESP32** with an **MPU6050 accelerometer** to collect vibration data from a structure. The collected data is analyzed in **Python** using **Fast Fourier Transform (FFT)** and modal analysis techniques to estimate:

- Natural Frequency
- Frequency Shift
- Energy Distribution
- Damage Index

The system compares the current structural response with a healthy baseline to detect possible structural damage.

---

## ⭐ Repository Highlights

- Real-time Structural Health Monitoring
- Modal Analysis based Damage Detection
- FFT Signal Processing
- React Web Dashboard
- Python Backend
- Computer Vision Crack Detection
- MySQL Data Logging
- ESP32 Firmware

---

## 🛠 Hardware Used

- ESP32 Development Board
- MPU6050 Accelerometer
- Bridge Prototype
- USB Cable
- Computer running Python backend

---

## 💻 Software Used

### Embedded

- Arduino IDE
- ESP32 Board Package

### Backend

- Python 3.x
- NumPy
- SciPy
- Matplotlib
- PySerial
- Flask
- MySQL

### Frontend

- React.js
- Vite
- JavaScript
- HTML5
- CSS3
  
---

## 📂 Project Structure

```text
.
├── Advanced_Structural_Health_Monitoring.png
├── bridge_monitoring_system
│   ├── bridge_data/                 # Generated vibration analysis CSV files
│   ├── bridge_monitor.py            # Main monitoring application
│   ├── SHM_plot.py                  # Plotting utilities
│   ├── ESP32/
│   │   └── SHM_ESP32.ino            # ESP32 firmware
│   ├── server/
│   │   ├── main.py                  # Backend server
│   │   ├── monitor_matplotlib.py    # Real-time monitoring
│   │   ├── database.sql             # Database schema
│   │   ├── requirements.txt         # Python dependencies
│   │   └── test_serial.py           # Serial communication test
│   └── webapp/
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── vite.config.js
│
├── computer_vision_crack_detector/
│   ├── input_images/
│   └── your_script.py
│
├── Screenshots/
│
├── Circuit_Diagram.jpg
└── README.md
```

---

## ⚙️ Working Principle

ESP32 + MPU6050
        │
        ▼
Serial Communication
        │
        ▼
Python Backend
        │
 ┌──────┼────────┐
 │      │        │
 ▼      ▼        ▼
FFT  Modal Analysis CSV Logging
 │
 ▼
Damage Index
 │
 ▼
Flask API
 │
 ▼
React Dashboard
 │
 ▼
Computer Vision

---

# 📊 Dashboard

The monitoring dashboard provides six real-time plots:

- Raw Vibration Signal
- Frequency Spectrum Comparison
- Natural Frequency Shift
- Damage Detection Index
- Energy Distribution
- Structural Health Summary

---

## 📈 Damage Detection Logic

The system detects damage using modal parameters.

### Frequency Shift

Damage generally causes:

- Reduction in stiffness
- Reduction in natural frequency

The greater the frequency shift, the higher the damage probability.

### Energy Distribution

The FFT spectrum is divided into frequency bands:

- 0–5 Hz
- 5–15 Hz
- 15–30 Hz
- 30–60 Hz
- 60–100 Hz

Energy redistribution indicates structural changes.

### Damage Index

The final Damage Index is calculated using a weighted combination of:

- Frequency Shift
- Energy Difference
- Damping Change

The result is normalized to:

```
0%  → Healthy

15% → Caution

30% → Damaged

100% → Severe Damage
```

---

# ▶️ Running the Project

## 📋 Prerequisites

- Python 3.10+
- Arduino IDE
- Node.js 18+
- MySQL Server
- ESP32 Board Package
- Git

## 1. Clone Repository

```bash
git clone https://github.com/Rakesh-Bhandari/Structural-Health-Monitoring-System-using-IoT.git

cd Structural-Health-Monitoring-System-using-IoT
```

---

## 2. Upload ESP32 Firmware

Open

```
bridge_monitoring_system/ESP32/SHM_ESP32.ino
```

using Arduino IDE.

Select

- ESP32 Board
- Correct COM Port

Upload the firmware.

---

## 3. Install Python Dependencies

```bash
cd bridge_monitoring_system/server

pip install -r requirements.txt
```

---

## 4. Start Backend Server

Open Terminal 1

```bash
cd bridge_monitoring_system/server
python main.py
```

---

## 5. Start Monitoring

Open Terminal 2

```bash
cd bridge_monitoring_system
python bridge_monitor.py
```
---

## 6. Run Web Dashboard

```bash
cd bridge_monitoring_system/webapp

npm install

npm run dev
```

Open

```
http://localhost:5173
```

---

## 7. Run Computer Vision Module

```bash
cd computer_vision_crack_detector

pip install opencv-python numpy

python your_script.py
```

---

## 📊 Example Output

The system provides:

- Baseline Natural Frequency
- Current Natural Frequency
- Frequency Shift
- Damage Index
- Energy Distribution
- Structural Health Status

Example:

```
Baseline Natural Frequency : 13 Hz

Current Natural Frequency : 8 Hz

Frequency Shift : 5 Hz

Damage Index : 100 %

Status : DAMAGED
```

---

## 📁 Generated Output

The system automatically stores vibration analysis logs in

```text
bridge_monitoring_system/bridge_data/
```

Each generated CSV fie stores

- Timestamp
- RMS
- Natural Frequency
- Frequency Shift
- Damage Index
- Health Status
- Analysis Mode
 
---

## 🧰 Technologies Used

| Category | Technologies |
|-----------|--------------|
| Embedded | ESP32, MPU6050, Arduino IDE |
| Backend | Python, Flask, NumPy, SciPy |
| Database | MySQL |
| Frontend | React, Vite |
| Data Visualization | Matplotlib |
| Communication | Serial UART |
| Computer Vision | Python, OpenCV |

---

## 📚 Applications

- Bridge Health Monitoring
- Building Monitoring
- Railway Bridge Inspection
- Wind Turbine Monitoring
- Industrial Machinery Monitoring
- Structural Safety Assessment
- Predictive Maintenance
- Research in Modal Analysis
- Smart Infrastructure Monitoring
- Digital Twin Systems
- Civil Engineering Research

---

## 📸 Screenshots

### Dashboard

![Dashboard](Advanced_Structural_Health_Monitoring.png)

---

### Circuit Diagram

![Circuit](Circuit_Diagram.jpg)

---

### Project Outputs

Complete screenshots of the project including

- Web Dashboard
- Crack Detection
- Database Logging
- FFT Graphs
- Serial Monitor
- Health Dashboard

are available here:

📂 **[Screenshots Folder](./Screenshots/)**

