import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np
from datetime import datetime
import csv
import os
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

# ============ CONFIGURATION ============
SERIAL_PORT = "COM3"  # CHECK THIS MATCHES YOUR ESP32
BAUD_RATE = 115200
WINDOW_SIZE = 500
UPDATE_INTERVAL = 100 # Faster update for smoother plotting
SAMPLE_RATE = 500  # Hz

# Structural Health Monitoring Parameters
BASELINE_SAMPLES = 1000  # Samples to collect for FFT baseline
DAMAGE_THRESHOLD = 0.15  # Frequency shift threshold

# Data storage
DATA_DIR = "bridge_data"
os.makedirs(DATA_DIR, exist_ok=True)
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = os.path.join(DATA_DIR, f"shm_analysis_{timestamp_str}.csv")

# ============ SERIAL SETUP ============
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✓ Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    exit()

# ============ DATA STRUCTURES ============
rms_deque = deque(maxlen=WINDOW_SIZE)
threshold_deque = deque(maxlen=WINDOW_SIZE) # NEW: Store dynamic threshold
water_level_deque = deque(maxlen=100)
flex_deque = deque(maxlen=WINDOW_SIZE)
baseline_data = []
current_sample_buffer = []

# Feature tracking
baseline_features = {
    'natural_freq': None,
    'damping_ratio': None,
    'freq_spectrum': None,
    'energy_distribution': None
}

current_features = {
    'natural_freq': 0,
    'frequency_shift': 0,
    'energy_change': 0,
    'damping_change': 0,
    'damage_index': 0
}

# Statistics
calibration_complete = False
baseline_count = 0
damage_detections = 0
start_time = datetime.now()
current_water_status = 0
current_flex_value = 0
current_esp_status = "WAITING" # NEW: Status from ESP32
current_threshold = 0.0 # NEW: Threshold from ESP32

# ============ CSV INITIALIZATION ============
csv_file = open(CSV_FILE, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'RMS', 'Natural_Freq', 'Freq_Shift', 
                     'Damage_Index', 'Water_Level', 'Flex_Value', 'ESP_Status', 'ESP_Threshold'])
csv_file.flush()

# ============ ADVANCED SIGNAL PROCESSING ============

def find_natural_frequency(data, sample_rate=500):
    """Find dominant natural frequency using FFT"""
    if len(data) < 256: return 0
    windowed_data = data * np.hamming(len(data))
    fft_vals = fft(windowed_data)
    freqs = fftfreq(len(data), 1/sample_rate)
    mask = (freqs > 1) & (freqs < 100)
    power = np.abs(fft_vals[mask])
    valid_freqs = freqs[mask]
    if len(power) == 0: return 0
    peak_idx = np.argmax(power)
    return valid_freqs[peak_idx]

def calculate_energy_distribution(data, sample_rate=500):
    if len(data) < 256: return np.zeros(5)
    windowed_data = data * np.hamming(len(data))
    fft_vals = fft(windowed_data)
    freqs = fftfreq(len(data), 1/sample_rate)
    power = np.abs(fft_vals)**2
    bands = [(0, 5), (5, 15), (15, 30), (30, 60), (60, 100)]
    energy = []
    for low, high in bands:
        mask = (freqs >= low) & (freqs < high)
        energy.append(np.sum(power[mask]))
    total_energy = np.sum(energy) + 1e-10
    return np.array(energy) / total_energy

def estimate_damping_ratio(data):
    if len(data) < 100: return 0
    try:
        analytic_signal = scipy_signal.hilbert(data)
        envelope = np.abs(analytic_signal)
        t = np.arange(len(envelope))
        if np.max(envelope) > 0:
            log_env = np.log(envelope + 1e-10)
            coeffs = np.polyfit(t, log_env, 1)
            damping = abs(coeffs[0]) * 100 
            return min(damping, 100)
    except:
        pass
    return 0

def calculate_damage_index(baseline_feat, current_feat):
    if baseline_feat['natural_freq'] is None: return 0
    freq_shift = abs(baseline_feat['natural_freq'] - current_feat['natural_freq'])
    freq_shift_ratio = freq_shift / (baseline_feat['natural_freq'] + 1e-6)
    energy_diff = 0
    if baseline_feat['energy_distribution'] is not None:
        energy_diff = np.sum(np.abs(baseline_feat['energy_distribution'] - current_feat['energy_distribution']))
    damping_change = 0
    if baseline_feat['damping_ratio'] is not None:
        damping_change = abs(current_feat['damping_ratio'] - baseline_feat['damping_ratio'])
    damage_index = (freq_shift_ratio * 40 + energy_diff * 30 + damping_change * 30)
    return min(damage_index * 100, 100)

# ============ FIGURE SETUP ============
fig = plt.figure(figsize=(16, 9))
manager = plt.get_current_fig_manager()
try:
    manager.window.state('zoomed')
except:
    pass

fig.canvas.manager.set_window_title('Advanced Structural Health Monitoring System')
fig.suptitle('Bridge Health Monitoring - Vibration, Modal Analysis & Flex Sensors', 
             fontsize=16, fontweight='bold')

# Grid Layout
ax1 = plt.subplot(3, 3, 1)
ax2 = plt.subplot(3, 3, 2)
ax3 = plt.subplot(3, 3, 3)
ax4 = plt.subplot(3, 3, 4)
ax5 = plt.subplot(3, 3, 5)
ax6 = plt.subplot(3, 3, 6)
ax7 = plt.subplot(3, 3, 7)         
ax8 = plt.subplot(3, 3, (8, 9))    

# 1. Time domain signal
line1, = ax1.plot([], [], 'b-', lw=1, alpha=0.7, label='Vibration')
line1_thresh, = ax1.plot([], [], 'r--', lw=1.5, label='Threshold') # NEW: Threshold line
ax1.set_xlim(0, WINDOW_SIZE)
ax1.set_ylim(0, 1.0) # Adjusted for RMS
ax1.set_xlabel('Samples')
ax1.set_ylabel('RMS Amplitude')
ax1.set_title('Vibration vs Dynamic Threshold')
ax1.legend(loc='upper right', fontsize='x-small')
ax1.grid(True, alpha=0.3)

# 2. Frequency spectrum
line2_baseline, = ax2.plot([], [], 'g-', lw=2, label='Baseline', alpha=0.7)
line2_current, = ax2.plot([], [], 'r-', lw=2, label='Current')
ax2.set_xlim(0, 50)
ax2.set_ylim(0, 1)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Normalized Power')
ax2.set_title('Frequency Spectrum Comparison')
ax2.legend(loc='upper right', fontsize='small')
ax2.grid(True, alpha=0.3)

# 3. Natural frequency
freq_history = deque(maxlen=100)
line3, = ax3.plot([], [], 'purple', lw=2, marker='o', markersize=3)
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 50)
ax3.set_xlabel('Sample')
ax3.set_ylabel('Natural Freq (Hz)')
ax3.set_title('Natural Frequency Shift')
ax3.grid(True, alpha=0.3)

# 4. Damage index
damage_history = deque(maxlen=100)
line4, = ax4.plot([], [], 'red', lw=3)
ax4.axhline(y=15, color='orange', linestyle='--', lw=2, label='Caution')
ax4.axhline(y=30, color='red', linestyle='--', lw=2, label='Damage')
ax4.set_xlim(0, 100)
ax4.set_ylim(0, 100)
ax4.set_xlabel('Sample')
ax4.set_ylabel('Damage Index (%)')
ax4.set_title('Damage Detection Index')
ax4.legend(loc='upper left', fontsize='small')
ax4.grid(True, alpha=0.3)

# 5. Energy distribution
bars = ax5.bar([0, 1, 2, 3, 4], [0, 0, 0, 0, 0], color=['blue', 'green', 'yellow', 'orange', 'red'])
ax5.set_ylim(0, 1)
ax5.set_xticklabels(['0-5Hz', '5-15Hz', '15-30Hz', '30-60Hz', '60-100Hz'], rotation=45)
ax5.set_ylabel('Normalized Energy')
ax5.set_title('Energy Distribution')
ax5.grid(True, alpha=0.3, axis='y')

# 6. Water Level
ax6.set_xlim(0, 100)
ax6.set_ylim(-0.2, 1.2)
ax6.set_title('Water Level Status', fontweight='bold', fontsize=12)
ax6.set_yticks([0, 1])
ax6.set_yticklabels(['💧 WATER', '✅ DRY'], fontsize=10, fontweight='bold')
ax6.grid(True, alpha=0.3)
line_water, = ax6.plot([], [], 'b-', lw=4, marker='o', markersize=8)
water_text_obj = ax6.text(50, 0.5, '', fontsize=12, fontweight='bold', 
                          ha='center', va='center',
                          bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

# 7. Flex Sensor
line_flex, = ax7.plot([], [], 'm-', lw=2) 
ax7.set_xlim(0, WINDOW_SIZE)
ax7.set_ylim(0, 4096) 
ax7.set_xlabel('Samples')
ax7.set_ylabel('Flex Value')
ax7.set_title('Flex / Bending Sensor')
ax7.grid(True, alpha=0.3)

# 8. Statistics
ax8.axis('off')
stats_text = ax8.text(0.05, 0.95, '', fontsize=9, verticalalignment='top', 
                      family='monospace', bbox=dict(boxstyle='round', 
                      facecolor='lightblue', alpha=0.5))

plt.tight_layout(rect=[0, 0, 1, 0.96])

# ============ ANIMATION UPDATE ============
def update(frame):
    global calibration_complete, baseline_count, baseline_features, damage_detections
    global current_sample_buffer, current_water_status, current_flex_value
    global current_esp_status, current_threshold
    
    # Read data
    lines_read = 0
    while ser.in_waiting and lines_read < 20:
        try:
            line_bytes = ser.readline().decode('utf-8').strip()
            if line_bytes.startswith('#') or line_bytes.startswith('---') or not ',' in line_bytes:
                continue
            
            parts = line_bytes.split(',')
            
            # UPDATED: Parse 7 Columns from new Firmware
            # timestamp, RMS, magnitude, FloatStatus, FlexValue, status, threshold
            if len(parts) >= 6: 
                # timestamp = float(parts[0]) 
                rms = float(parts[1])
                # mag = float(parts[2])
                water_sensor = int(parts[3]) 
                flex_val = int(parts[4])
                esp_status = parts[5] # String: CALIBRATING, NORMAL, DAMAGED
                
                # Check if threshold is sent (index 6)
                thresh_val = 0.0
                if len(parts) > 6:
                    thresh_val = float(parts[6])

                # Update Globals
                current_esp_status = esp_status
                current_threshold = thresh_val
                current_water_status = water_sensor
                current_flex_value = flex_val
                
                # Update Buffers
                rms_deque.append(rms)
                threshold_deque.append(thresh_val)
                current_sample_buffer.append(rms)
                water_level_deque.append(water_sensor)
                flex_deque.append(flex_val)
                
                # Only collect FFT baseline if ESP32 is done calibrating OR if we decide to
                # However, for this code, we run a parallel calibration logic for FFT
                if not calibration_complete and esp_status != "CALIBRATING":
                    baseline_data.append(rms)
                    baseline_count += 1
                
                lines_read += 1
        except Exception as e:
            pass
    
    # CALIBRATION PHASE (Python side)
    # We wait until ESP32 says it's done calibrating before we trust the data
    if not calibration_complete and baseline_count >= BASELINE_SAMPLES:
        baseline_array = np.array(baseline_data)
        baseline_features['natural_freq'] = find_natural_frequency(baseline_array)
        baseline_features['damping_ratio'] = estimate_damping_ratio(baseline_array)
        baseline_features['energy_distribution'] = calculate_energy_distribution(baseline_array)
        
        windowed = baseline_array * np.hamming(len(baseline_array))
        fft_vals = fft(windowed)
        freqs = fftfreq(len(baseline_array), 1/SAMPLE_RATE)
        mask = (freqs > 0) & (freqs < 50)
        baseline_features['freq_spectrum'] = (freqs[mask], np.abs(fft_vals[mask]))
        calibration_complete = True
    
    # ANALYSIS PHASE
    if calibration_complete and len(current_sample_buffer) >= 500:
        current_array = np.array(current_sample_buffer[-500:])
        current_features['natural_freq'] = find_natural_frequency(current_array)
        current_features['damping_ratio'] = estimate_damping_ratio(current_array)
        current_features['energy_distribution'] = calculate_energy_distribution(current_array)
        current_features['frequency_shift'] = abs(baseline_features['natural_freq'] - current_features['natural_freq'])
        current_features['damage_index'] = calculate_damage_index(baseline_features, current_features)
        
        freq_history.append(current_features['natural_freq'])
        damage_history.append(current_features['damage_index'])
        
        if current_features['damage_index'] > 30: damage_detections += 1
        
        csv_writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            f"{np.mean(current_array):.6f}",
            f"{current_features['natural_freq']:.3f}",
            f"{current_features['frequency_shift']:.3f}",
            f"{current_features['damage_index']:.2f}",
            current_water_status,
            current_flex_value,
            current_esp_status,
            current_threshold
        ])
        csv_file.flush()
    
    # Update plots
    line1.set_data(range(len(rms_deque)), list(rms_deque))
    line1_thresh.set_data(range(len(threshold_deque)), list(threshold_deque)) # Update threshold line
    
    # Spectrum
    if calibration_complete and baseline_features['freq_spectrum'] is not None:
        line2_baseline.set_data(baseline_features['freq_spectrum'][0], 
                                baseline_features['freq_spectrum'][1] / (np.max(baseline_features['freq_spectrum'][1]) + 1e-10))
        if len(current_sample_buffer) >= 256:
            current_array = np.array(current_sample_buffer[-256:])
            windowed = current_array * np.hamming(len(current_array))
            fft_vals = fft(windowed)
            freqs = fftfreq(len(current_array), 1/SAMPLE_RATE)
            mask = (freqs > 0) & (freqs < 50)
            current_spectrum = np.abs(fft_vals[mask])
            line2_current.set_data(freqs[mask], current_spectrum / (np.max(current_spectrum) + 1e-10))
    
    line3.set_data(range(len(freq_history)), list(freq_history))
    if baseline_features['natural_freq'] is not None:
        ax3.axhline(y=baseline_features['natural_freq'], color='green', linestyle='--', lw=2, alpha=0.7)
    
    line4.set_data(range(len(damage_history)), list(damage_history))
    
    if calibration_complete and current_features['energy_distribution'] is not None:
        for bar, height in zip(bars, current_features['energy_distribution']):
            bar.set_height(height)
    
    # Water Level
    if len(water_level_deque) > 0:
        water_data = list(water_level_deque)
        line_water.set_data(range(len(water_data)), water_data)
        if current_water_status == 1: 
            ax6.set_facecolor('#ffcccc')
            line_water.set_color('red')
            water_text_obj.set_text('💧 WATER DETECTED')
            water_text_obj.set_bbox(dict(boxstyle='round', facecolor='red', alpha=0.7))
        else:
            ax6.set_facecolor('#ccffcc')
            line_water.set_color('green')
            water_text_obj.set_text('✅ NO WATER')
            water_text_obj.set_bbox(dict(boxstyle='round', facecolor='green', alpha=0.7))

    line_flex.set_data(range(len(flex_deque)), list(flex_deque))
    
    # Stats Block
    esp_display = current_esp_status
    if esp_display == "CALIBRATING":
        esp_display = "⚙️ CALIBRATING..."
    elif esp_display == "DAMAGED":
        esp_display = "❌ DAMAGED (THRESHOLD)"
    
    health = "✅ HEALTHY"
    if current_features['damage_index'] > 30: health = "❌ DAMAGED (FFT)"
    elif current_features['damage_index'] > 15: health = "⚠️ CAUTION"

    elapsed = (datetime.now() - start_time).total_seconds()
    baseline_natfreq = f"{baseline_features['natural_freq']:.2f}" if baseline_features['natural_freq'] is not None else "--"
    current_natfreq = f"{current_features['natural_freq']:.2f}" if current_features.get('natural_freq') is not None else "--"
    
    stats = f"""
╔══════════════════════════════════════════════╗
║        STRUCTURAL HEALTH MONITORING          ║
╚══════════════════════════════════════════════╝
  ESP Status: {esp_display}
  Python Mode: {"CALIBRATING" if not calibration_complete else "ANALYZING"}
  Time: {int(elapsed//60)}m {int(elapsed%60)}s
  
  REAL-TIME:
  • Flex Value: {current_flex_value}
  • Water: {current_water_status}
  • RMS: {rms_deque[-1] if len(rms_deque)>0 else 0:.4f}
  • Limit: {current_threshold:.4f}

  FFT ANALYSIS:
  • Base Freq: {baseline_natfreq} Hz
  • Curr Freq: {current_natfreq} Hz
  • Damage Idx: {current_features['damage_index']:.1f} %
"""
    stats_text.set_text(stats)
    return line1, line1_thresh, line2_baseline, line2_current, line3, line4, stats_text, line_water, water_text_obj, line_flex

# ============ START ============
print("\n" + "="*60)
print("🏗️ BRIDGE HEALTH MONITORING SYSTEM")
print("="*60)
print(f"Listening on {SERIAL_PORT}...")

ani = animation.FuncAnimation(fig, update, interval=UPDATE_INTERVAL, 
                              cache_frame_data=False, blit=False)
plt.show()
csv_file.close()