import serial
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time
import numpy as np
from collections import deque
from scipy.fft import fft, fftfreq
import warnings
import json

warnings.filterwarnings('ignore')

# ================= CONFIGURATION =================
SERIAL_PORT = "COM3"   # Ensure this matches your ESP32 Port
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1.0

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Rakesh@260', 
    'database': 'shm_db'
}

SAMPLE_RATE = 500       
WINDOW_SIZE = 500       
BASELINE_SAMPLES = 1000 
# CHANGED: Updated from 2.0 to 1.0 second
AGGREGATION_INTERVAL = 3.0 

# ================= GLOBAL STATE =================
data_lock = threading.Lock()
raw_rms_buffer = deque(maxlen=WINDOW_SIZE)
calibration_buffer = []
aggregation_buffer = []
historical_trends = deque(maxlen=200)

baseline_features = {
    'natural_freq': None,
    'energy_distribution': None,
    'calibrated': False
}

current_status = {
    'shm_health_status': 'INITIALIZING',
    'damage_index': 0.0,
    'natural_freq': 0.0,
    'rms_current_1': 0.0,
    'flex_raw': 0,
    'float_status': 0,     
    'timestamp': datetime.now().isoformat(),
    'last_prediction': "[]" 
}

# ================= DATABASE FUNCTIONS =================
def init_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shm_trend_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50),
                natural_freq FLOAT,
                damage_index FLOAT,
                rms_val FLOAT,
                flex_val FLOAT,
                float_alert TINYINT,
                predictions TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def save_to_database(data):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            INSERT INTO shm_trend_log 
            (status, natural_freq, damage_index, rms_val, flex_val, float_alert, predictions)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['status'], 
            data['natural_freq'], 
            data['damage_index'], 
            data['rms_val'], 
            data['flex_val'], 
            data['float_alert'],
            data['predictions']
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving to DB: {e}")

def get_db_history(minutes=10):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        time_limit = datetime.now() - timedelta(minutes=minutes)
        query = """
            SELECT timestamp, status, natural_freq, damage_index, rms_val, flex_val, float_alert, predictions
            FROM shm_trend_log WHERE timestamp >= %s ORDER BY timestamp ASC
        """
        cursor.execute(query, (time_limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        formatted = []
        for row in rows:
            formatted.append({
                'timestamp': row['timestamp'].isoformat(),
                'avg_freq': row['natural_freq'],
                'max_damage': row['damage_index'],
                'rms_1': row['rms_val'],    
                'flex_mean': row['flex_val'],
                'float_alert': row['float_alert'],
                'status': row['status'],
                'predictions': row['predictions']
            })
        return formatted
    except Exception as e:
        print(f"Error reading DB: {e}")
        return []

# ================= SERIAL WORKER THREAD =================
def serial_worker():
    global current_status, calibration_buffer, baseline_features
    
    print(f"Connecting to Serial Port {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
        time.sleep(2)
        ser.flushInput()
        print(f"✓ Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"✗ Serial Connection Error: {e}")
        return

    last_aggregation_time = time.time()
    
    while True:
        try:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line or line.startswith('#'): continue
                
                parts = line.split(',')
                
                # ROBUST PARSING: Try to extract data even if format varies slightly
                try:
                    if len(parts) >= 6:
                        rms_val = float(parts[1])
                        float_val = int(parts[3])
                        flex_val = int(parts[4])
                        esp_status = parts[5]
                    elif len(parts) >= 3:
                        # Fallback for simpler format
                        rms_val = float(parts[0])
                        float_val = int(parts[1])
                        flex_val = int(parts[2])
                        esp_status = "UNKNOWN"
                    else:
                        print(f"Ignored malformed line: {line}")
                        continue

                    with data_lock:
                        current_status['rms_current_1'] = rms_val
                        current_status['flex_raw'] = flex_val
                        current_status['float_status'] = float_val
                        current_status['timestamp'] = datetime.now().isoformat()
                        
                        raw_rms_buffer.append(rms_val)
                        aggregation_buffer.append({'rms': rms_val, 'flex': flex_val, 'float': float_val})
                        
                        # --- CALIBRATION LOGIC ---
                        if not baseline_features['calibrated'] and esp_status != "CALIBRATING":
                            calibration_buffer.append(rms_val)
                            current_status['shm_health_status'] = 'CALIBRATING'
                            if len(calibration_buffer) >= BASELINE_SAMPLES:
                                arr = np.array(calibration_buffer)
                                baseline_features['natural_freq'] = find_natural_frequency(arr)
                                baseline_features['energy_distribution'] = calculate_energy_distribution(arr)
                                baseline_features['calibrated'] = True
                                print(f"✓ Calibration Complete. Freq: {baseline_features['natural_freq']:.2f}Hz")
                        
                        # --- HEALTH CHECK LOGIC ---
                        elif len(raw_rms_buffer) >= WINDOW_SIZE:
                            arr = np.array(raw_rms_buffer)
                            curr_freq = find_natural_frequency(arr)
                            curr_energy = calculate_energy_distribution(arr)
                            dmg = calculate_damage_index(baseline_features, curr_freq, curr_energy)
                            current_status['damage_index'] = dmg
                            current_status['natural_freq'] = curr_freq
                            
                            if float_val == 1:
                                current_status['shm_health_status'] = 'CRITICAL_LEAK'
                            elif esp_status == "CALIBRATING":
                                current_status['shm_health_status'] = 'CALIBRATING'
                            elif esp_status == "DAMAGED":
                                current_status['shm_health_status'] = 'CRITICAL_DAMAGE'
                            elif dmg > 30:
                                current_status['shm_health_status'] = 'CRITICAL_DAMAGE'
                            elif dmg > 15:
                                current_status['shm_health_status'] = 'WARNING_DAMAGE'
                            else:
                                current_status['shm_health_status'] = 'HEALTHY'
                                
                except ValueError as ve:
                    print(f"Parsing Error on line: '{line}' -> {ve}")
                    continue

            # --- AGGREGATION & DATA PUSH ---
            if time.time() - last_aggregation_time >= AGGREGATION_INTERVAL:
                with data_lock:
                    if aggregation_buffer:
                        avg_rms = float(np.mean([x['rms'] for x in aggregation_buffer]))
                        avg_flex = float(np.mean([x['flex'] for x in aggregation_buffer]))
                        max_float = int(max([x['float'] for x in aggregation_buffer]))
                        vision_data = current_status.get('last_prediction', "[]")

                        # 1. Save to Database
                        db_record = {
                            'status': current_status['shm_health_status'],
                            'natural_freq': current_status['natural_freq'],
                            'damage_index': current_status['damage_index'],
                            'rms_val': avg_rms,
                            'flex_val': avg_flex,
                            'float_alert': max_float,
                            'predictions': vision_data
                        }
                        save_to_database(db_record)
                        
                        # 2. Update Live Frontend Queue
                        frontend_record = {
                            'timestamp': datetime.now().isoformat(),
                            'status': current_status['shm_health_status'],
                            'avg_freq': current_status['natural_freq'],
                            'max_damage': current_status['damage_index'],
                            'rms_1': avg_rms,      
                            'flex_mean': avg_flex, 
                            'float_alert': max_float,
                            'predictions': vision_data
                        }
                        historical_trends.append(frontend_record)
                        print(f"Data Pushed: RMS={avg_rms:.4f}, Flex={avg_flex:.1f}") 
                        
                        aggregation_buffer.clear()
                
                last_aggregation_time = time.time()
                
        except Exception as e:
            time.sleep(1)

# ================= SIGNAL PROCESSING =================
def find_natural_frequency(data):
    if len(data) < 256: return 0.0
    windowed = data * np.hamming(len(data))
    fft_vals = fft(windowed)
    freqs = fftfreq(len(data), 1/SAMPLE_RATE)
    mask = (freqs > 1) & (freqs < 100)
    power = np.abs(fft_vals[mask])
    valid_freqs = freqs[mask]
    if len(power) == 0: return 0.0
    peak_idx = np.argmax(power)
    return float(valid_freqs[peak_idx])

def calculate_energy_distribution(data):
    if len(data) < 256: return np.zeros(5)
    windowed = data * np.hamming(len(data))
    fft_vals = fft(windowed)
    freqs = fftfreq(len(data), 1/SAMPLE_RATE)
    power = np.abs(fft_vals)**2
    bands = [(0, 5), (5, 15), (15, 30), (30, 60), (60, 100)]
    energy = []
    for low, high in bands:
        mask = (freqs >= low) & (freqs < high)
        energy.append(np.sum(power[mask]))
    total = np.sum(energy) + 1e-10
    return np.array(energy) / total

def calculate_damage_index(baseline, current_freq, current_energy):
    if not baseline['calibrated']: return 0.0
    freq_shift = abs(baseline['natural_freq'] - current_freq)
    freq_shift_ratio = freq_shift / (baseline['natural_freq'] + 1e-6)
    energy_diff = 0.0
    if baseline['energy_distribution'] is not None:
        energy_diff = np.sum(np.abs(baseline['energy_distribution'] - current_energy))
    damage_index = (freq_shift_ratio * 60.0 + energy_diff * 40.0)
    return min(damage_index * 100.0, 100.0)

# ================= FLASK WEB SERVER =================
app = Flask(__name__)
CORS(app)

@app.route('/api/status')
def api_status():
    with data_lock:
        response_trends = list(historical_trends)
        if not response_trends:
            response_trends = get_db_history(minutes=10)

        response = {
            'shm_health_status': current_status['shm_health_status'],
            'damage_index': round(current_status['damage_index'], 2),
            'natural_freq': round(current_status['natural_freq'], 2),
            'rms_current_1': current_status['rms_current_1'],
            'flex_raw': current_status['flex_raw'],
            'float_status': current_status['float_status'],
            'timestamp': current_status['timestamp'],
            'historical_trends': response_trends,
            'calibration_complete': baseline_features['calibrated'],
            'last_prediction': current_status['last_prediction']
        }
    return jsonify(response)

@app.route('/api/update_vision', methods=['POST'])
def update_vision():
    try:
        data = request.json
        preds = data.get('predictions', [])
        with data_lock:
            current_status['last_prediction'] = json.dumps(preds)
        return jsonify({"status": "success", "message": "Vision data updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/reset')
def reset():
    global calibration_buffer, baseline_features
    with data_lock:
        calibration_buffer = []
        baseline_features['calibrated'] = False
        baseline_features['natural_freq'] = None
        current_status['last_prediction'] = "[]"
    return jsonify({"status": "Reset Successful"})

if __name__ == "__main__":
    init_database()
    t = threading.Thread(target=serial_worker, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5001, debug=False)