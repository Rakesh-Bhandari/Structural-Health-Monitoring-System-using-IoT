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
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
WINDOW_SIZE = 500
UPDATE_INTERVAL = 250
SAMPLE_RATE = 500  # Hz

# Structural Health Monitoring Parameters
BASELINE_SAMPLES = 1000  # Samples to collect for baseline
CALIBRATION_MODE = True
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

# ============ CSV INITIALIZATION ============
csv_file = open(CSV_FILE, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'RMS', 'Natural_Freq', 'Freq_Shift', 
                     'Damage_Index', 'Status', 'Mode'])
csv_file.flush()

# ============ ADVANCED SIGNAL PROCESSING ============

def find_natural_frequency(data, sample_rate=500):
    """Find dominant natural frequency using FFT"""
    if len(data) < 256:
        return 0
    
    # Apply Hamming window to reduce spectral leakage
    windowed_data = data * np.hamming(len(data))
    
    # FFT
    fft_vals = fft(windowed_data)
    freqs = fftfreq(len(data), 1/sample_rate)
    
    # Only positive frequencies between 1-100 Hz
    mask = (freqs > 1) & (freqs < 100)
    power = np.abs(fft_vals[mask])
    valid_freqs = freqs[mask]
    
    if len(power) == 0:
        return 0
    
    # Find peak frequency
    peak_idx = np.argmax(power)
    natural_freq = valid_freqs[peak_idx]
    
    return natural_freq

def calculate_energy_distribution(data, sample_rate=500):
    """Calculate energy in different frequency bands"""
    if len(data) < 256:
        return np.zeros(5)
    
    windowed_data = data * np.hamming(len(data))
    fft_vals = fft(windowed_data)
    freqs = fftfreq(len(data), 1/sample_rate)
    power = np.abs(fft_vals)**2
    
    # Energy in frequency bands
    bands = [(0, 5), (5, 15), (15, 30), (30, 60), (60, 100)]
    energy = []
    
    for low, high in bands:
        mask = (freqs >= low) & (freqs < high)
        band_energy = np.sum(power[mask])
        energy.append(band_energy)
    
    total_energy = np.sum(energy) + 1e-10
    return np.array(energy) / total_energy  # Normalized

def estimate_damping_ratio(data):
    """Estimate damping from envelope decay"""
    if len(data) < 100:
        return 0
    
    # Hilbert transform to get envelope
    try:
        analytic_signal = scipy_signal.hilbert(data)
        envelope = np.abs(analytic_signal)
        
        # Fit exponential decay
        t = np.arange(len(envelope))
        if np.max(envelope) > 0:
            log_env = np.log(envelope + 1e-10)
            coeffs = np.polyfit(t, log_env, 1)
            damping = abs(coeffs[0]) * 100  # Convert to percentage
            return min(damping, 100)
    except:
        pass
    return 0

def calculate_damage_index(baseline_feat, current_feat):
    """
    Calculate damage index based on multiple features
    Higher index = more damage
    """
    if baseline_feat['natural_freq'] is None:
        return 0
    
    # Frequency shift (damaged structures have lower natural frequencies)
    freq_shift = abs(baseline_feat['natural_freq'] - current_feat['natural_freq'])
    freq_shift_ratio = freq_shift / (baseline_feat['natural_freq'] + 1e-6)
    
    # Energy distribution change
    if baseline_feat['energy_distribution'] is not None:
        energy_diff = np.sum(np.abs(
            baseline_feat['energy_distribution'] - current_feat['energy_distribution']
        ))
    else:
        energy_diff = 0
    
    # Damping change (damage increases damping)
    damping_change = 0
    if baseline_feat['damping_ratio'] is not None:
        damping_change = abs(current_feat['damping_ratio'] - baseline_feat['damping_ratio'])
    
    # Combined damage index (weighted sum)
    damage_index = (
        freq_shift_ratio * 40 +  # Frequency shift most important
        energy_diff * 30 +        # Energy redistribution
        damping_change * 30       # Damping increase
    )
    
    return min(damage_index * 100, 100)  # Scale to 0-100

# ============ FIGURE SETUP ============
fig = plt.figure(figsize=(16, 9))
manager = plt.get_current_fig_manager()
try:
    manager.window.state('zoomed')
except:
    try:
        manager.window.showMaximized()
    except:
        pass

fig.canvas.manager.set_window_title('Advanced Structural Health Monitoring')
fig.suptitle('Advanced Structural Health Monitoring - Modal Analysis', 
             fontsize=16, fontweight='bold')

ax1 = plt.subplot(2, 3, 1)
ax2 = plt.subplot(2, 3, 2)
ax3 = plt.subplot(2, 3, 3)
ax4 = plt.subplot(2, 3, 4)
ax5 = plt.subplot(2, 3, 5)
ax6 = plt.subplot(2, 3, 6)

# Time domain signal
line1, = ax1.plot([], [], 'b-', lw=1, alpha=0.7)
ax1.set_xlim(0, WINDOW_SIZE)
ax1.set_ylim(-0.3, 0.3)
ax1.set_xlabel('Samples')
ax1.set_ylabel('Acceleration (g)')
ax1.set_title('Raw Vibration Signal')
ax1.grid(True, alpha=0.3)

# Frequency spectrum comparison
line2_baseline, = ax2.plot([], [], 'g-', lw=2, label='Baseline', alpha=0.7)
line2_current, = ax2.plot([], [], 'r-', lw=2, label='Current')
ax2.set_xlim(0, 50)
ax2.set_ylim(0, 1)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Normalized Power')
ax2.set_title('Frequency Spectrum Comparison')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Natural frequency tracking
freq_history = deque(maxlen=100)
line3, = ax3.plot([], [], 'purple', lw=2, marker='o', markersize=3)
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 50)
ax3.set_xlabel('Sample')
ax3.set_ylabel('Natural Freq (Hz)')
ax3.set_title('Natural Frequency Shift')
ax3.grid(True, alpha=0.3)

# Damage index
damage_history = deque(maxlen=100)
line4, = ax4.plot([], [], 'red', lw=3)
ax4.axhline(y=15, color='orange', linestyle='--', lw=2, label='Caution')
ax4.axhline(y=30, color='red', linestyle='--', lw=2, label='Damage')
ax4.set_xlim(0, 100)
ax4.set_ylim(0, 100)
ax4.set_xlabel('Sample')
ax4.set_ylabel('Damage Index (%)')
ax4.set_title('Damage Detection Index')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Energy distribution
bars = ax5.bar([0, 1, 2, 3, 4], [0, 0, 0, 0, 0], color=['blue', 'green', 'yellow', 'orange', 'red'])
ax5.set_ylim(0, 1)
ax5.set_xticks([0, 1, 2, 3, 4])
ax5.set_xticklabels(['0-5Hz', '5-15Hz', '15-30Hz', '30-60Hz', '60-100Hz'], rotation=45)
ax5.set_ylabel('Normalized Energy')
ax5.set_title('Energy Distribution')
ax5.grid(True, alpha=0.3, axis='y')

# Statistics
ax6.axis('off')
stats_text = ax6.text(0.05, 0.95, '', fontsize=9, verticalalignment='top', 
                      family='monospace', bbox=dict(boxstyle='round', 
                      facecolor='lightblue', alpha=0.5))

plt.tight_layout(rect=[0, 0, 1, 0.96])

try:
    fig.canvas.manager.window.resizable(False, False)
except:
    pass

# ============ ANIMATION UPDATE ============
def update(frame):
    global calibration_complete, baseline_count, baseline_features, damage_detections
    global current_sample_buffer
    
    # Read data
    lines_read = 0
    while ser.in_waiting and lines_read < 20:
        try:
            line_bytes = ser.readline().decode('utf-8').strip()
            if line_bytes.startswith('#') or line_bytes.startswith('---') or not ',' in line_bytes:
                continue
            
            parts = line_bytes.split(',')
            if len(parts) >= 2:
                rms = float(parts[1])
                rms_deque.append(rms)
                current_sample_buffer.append(rms)
                
                if not calibration_complete:
                    baseline_data.append(rms)
                    baseline_count += 1
                
                lines_read += 1
        except:
            pass
    
    # CALIBRATION PHASE
    if not calibration_complete and baseline_count >= BASELINE_SAMPLES:
        print("\n" + "="*60)
        print("ANALYZING BASELINE (HEALTHY STRUCTURE)...")
        
        baseline_array = np.array(baseline_data)
        
        # Extract baseline features
        baseline_features['natural_freq'] = find_natural_frequency(baseline_array)
        baseline_features['damping_ratio'] = estimate_damping_ratio(baseline_array)
        baseline_features['energy_distribution'] = calculate_energy_distribution(baseline_array)
        
        # Baseline spectrum
        windowed = baseline_array * np.hamming(len(baseline_array))
        fft_vals = fft(windowed)
        freqs = fftfreq(len(baseline_array), 1/SAMPLE_RATE)
        mask = (freqs > 0) & (freqs < 50)
        baseline_features['freq_spectrum'] = (freqs[mask], np.abs(fft_vals[mask]))
        
        calibration_complete = True
        
        print(f"✓ Baseline Natural Frequency: {baseline_features['natural_freq']:.2f} Hz")
        print(f"✓ Baseline Damping: {baseline_features['damping_ratio']:.3f}%")
        print(f"✓ Calibration Complete!")
        print("\n NOW TEST ON DAMAGED STRUCTURE")
        print("="*60 + "\n")
    
    # ANALYSIS PHASE
    if calibration_complete and len(current_sample_buffer) >= 500:
        current_array = np.array(current_sample_buffer[-500:])
        
        # Extract current features
        current_features['natural_freq'] = find_natural_frequency(current_array)
        current_features['damping_ratio'] = estimate_damping_ratio(current_array)
        current_features['energy_distribution'] = calculate_energy_distribution(current_array)
        
        # Calculate damage index
        current_features['frequency_shift'] = abs(
            baseline_features['natural_freq'] - current_features['natural_freq']
        )
        current_features['damage_index'] = calculate_damage_index(
            baseline_features, current_features
        )
        
        # Track history
        freq_history.append(current_features['natural_freq'])
        damage_history.append(current_features['damage_index'])
        
        # Determine status
        status = "HEALTHY"
        if current_features['damage_index'] > 30:
            status = "DAMAGED"
            damage_detections += 1
        elif current_features['damage_index'] > 15:
            status = "CAUTION"
        
        # Log to CSV
        csv_writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            f"{np.mean(current_array):.6f}",
            f"{current_features['natural_freq']:.3f}",
            f"{current_features['frequency_shift']:.3f}",
            f"{current_features['damage_index']:.2f}",
            status,
            "ANALYSIS"
        ])
        csv_file.flush()
    
    # Update plots
    line1.set_data(range(len(rms_deque)), list(rms_deque))
    
    # Spectrum comparison
    if calibration_complete and baseline_features['freq_spectrum'] is not None:
        line2_baseline.set_data(baseline_features['freq_spectrum'][0], 
                                baseline_features['freq_spectrum'][1] / 
                                (np.max(baseline_features['freq_spectrum'][1]) + 1e-10))
        
        if len(current_sample_buffer) >= 256:
            current_array = np.array(current_sample_buffer[-256:])
            windowed = current_array * np.hamming(len(current_array))
            fft_vals = fft(windowed)
            freqs = fftfreq(len(current_array), 1/SAMPLE_RATE)
            mask = (freqs > 0) & (freqs < 50)
            current_spectrum = np.abs(fft_vals[mask])
            line2_current.set_data(freqs[mask], current_spectrum / (np.max(current_spectrum) + 1e-10))
    
    # Natural frequency history
    line3.set_data(range(len(freq_history)), list(freq_history))
    if baseline_features['natural_freq'] is not None:
        ax3.axhline(y=baseline_features['natural_freq'], color='green', 
                   linestyle='--', lw=2, alpha=0.7, label='Baseline')
    
    # Damage index
    line4.set_data(range(len(damage_history)), list(damage_history))
    
    # Energy bars
    if calibration_complete and current_features['energy_distribution'] is not None:
        for bar, height in zip(bars, current_features['energy_distribution']):
            bar.set_height(height)
    
    # Statistics
    mode = "CALIBRATION" if not calibration_complete else "🧪 ANALYSIS"
    progress = f"{baseline_count}/{BASELINE_SAMPLES}" if not calibration_complete else "Complete"
    
    health = "HEALTHY"
    if calibration_complete:
        if current_features['damage_index'] > 30:
            health = "DAMAGED"
        elif current_features['damage_index'] > 15:
            health = "CAUTION"
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
        # Safe formatting for None values
    baseline_natfreq = f"{baseline_features['natural_freq']:.2f}" if baseline_features['natural_freq'] is not None else "--"
    baseline_damping = f"{baseline_features['damping_ratio']:.3f}" if baseline_features['damping_ratio'] is not None else "--"
    current_natfreq = f"{current_features['natural_freq']:.2f}" if current_features.get('natural_freq') is not None else "--"
    current_freqshift = f"{current_features['frequency_shift']:.2f}" if current_features.get('frequency_shift') is not None else "--"
    current_damageidx = f"{current_features['damage_index']:.1f}" if current_features.get('damage_index') is not None else "--"

    stats = f"""
╔════════════════════════════════════════╗
║  STRUCTURAL HEALTH MONITORING          ║
╚════════════════════════════════════════╝

Mode: {mode}
Progress: {progress}
Status: {health}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASELINE (Healthy Structure):
    • Natural Freq: {baseline_natfreq} Hz
    • Damping: {baseline_damping}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CURRENT ANALYSIS:
    • Natural Freq: {current_natfreq} Hz
    • Freq Shift: {current_freqshift} Hz
    • Damage Index: {current_damageidx}%
    • Detections: {damage_detections}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Runtime: {int(elapsed//60)}m {int(elapsed%60)}s
Logging: {os.path.basename(CSV_FILE)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTRUCTIONS:
1. Calibrate on HEALTHY chair (tap it)
2. Wait for "Calibration Complete"
3. Switch to BROKEN chair
4. Tap it - watch damage index!
"""
    stats_text.set_text(stats)
    
    return line1, line2_baseline, line2_current, line3, line4, stats_text

# ============ START ============
print("\n" + "="*60)
print(" ADVANCED STRUCTURAL HEALTH MONITORING")
print("="*60)
print("\n TESTING PROCEDURE:")
print("1. Place sensor on HEALTHY chair")
print("2. TAP the chair repeatedly for 10-15 seconds")
print("3. Wait for calibration to complete")
print("4. Move sensor to BROKEN chair")
print("5. TAP the broken chair - watch damage index spike!")
print("\n Key: Damage changes natural frequency & energy distribution")
print("="*60 + "\n")

ani = animation.FuncAnimation(fig, update, interval=UPDATE_INTERVAL, 
                              cache_frame_data=False, blit=False)

try:
    plt.show()
except KeyboardInterrupt:
    print("\n Stopped")
finally:
    csv_file.close()
    ser.close()
    print(f"\n Data saved: {CSV_FILE}")
