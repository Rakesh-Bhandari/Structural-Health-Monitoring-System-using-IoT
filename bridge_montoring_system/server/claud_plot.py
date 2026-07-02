import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np
from datetime import datetime
import threading
import queue

# ============================================================
# Configuration
# ============================================================
SERIAL_PORT = 'COM3'  # Change to your ESP32 port (COM3, /dev/ttyUSB0, etc.)
BAUD_RATE = 115200
MAX_POINTS = 300  # Number of points to display (adjust for speed)
VIBRATION_THRESHOLD = 0.15

# ============================================================
# Data Storage
# ============================================================
class SensorData:
    def __init__(self, max_size=300):
        self.max_size = max_size
        self.timestamp = deque(maxlen=max_size)
        self.rms1 = deque(maxlen=max_size)
        self.rms2 = deque(maxlen=max_size)
        self.max_rms = deque(maxlen=max_size)
        self.flex = deque(maxlen=max_size)
        self.float_status = deque(maxlen=max_size)
        self.alert_status = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add_data(self, ts, r1, r2, mr, f, fs, alrt):
        with self.lock:
            self.timestamp.append(ts)
            self.rms1.append(r1)
            self.rms2.append(r2)
            self.max_rms.append(mr)
            self.flex.append(f)
            self.float_status.append(fs)
            self.alert_status.append(alrt)
    
    def get_data(self):
        with self.lock:
            return (list(self.timestamp), list(self.rms1), list(self.rms2), 
                   list(self.max_rms), list(self.flex), list(self.float_status),
                   list(self.alert_status))

# ============================================================
# Serial Reader Thread
# ============================================================
def serial_reader(ser, data_queue, sensor_data):
    """Read serial data in background thread"""
    sample_count = 0
    start_time = None
    
    try:
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Skip header lines
                if 'timestamp_ms' in line or '===' in line or line.startswith('---'):
                    continue
                
                try:
                    parts = line.split(',')
                    if len(parts) == 7:
                        ts = int(parts[0])
                        r1 = float(parts[1])
                        r2 = float(parts[2])
                        mr = float(parts[3])
                        fx = float(parts[4])
                        fs = int(parts[5])
                        alrt = parts[6].strip()
                        
                        # Convert timestamp to relative seconds
                        if start_time is None:
                            start_time = ts
                        rel_time = (ts - start_time) / 1000.0
                        
                        sensor_data.add_data(rel_time, r1, r2, mr, fx, fs, alrt)
                        sample_count += 1
                        
                        # Print console feedback every 50 samples
                        if sample_count % 50 == 0:
                            print(f"Samples: {sample_count} | RMS1: {r1:.5f} | RMS2: {r2:.5f} | Flex: {fx:.3f}")
                            
                except (ValueError, IndexError) as e:
                    continue
            else:
                threading.Event().wait(0.001)
                
    except Exception as e:
        print(f"Serial Reader Error: {e}")
        ser.close()

# ============================================================
# Plotting Functions
# ============================================================
def plot_data(sensor_data):
    """Create live updating plots"""
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('ESP32 Bridge Health Monitoring System', fontsize=16, fontweight='bold')
    
    # Create subplots
    ax1 = plt.subplot(3, 2, 1)  # MPU Vibration Comparison
    ax2 = plt.subplot(3, 2, 2)  # Difference between MPU1 and MPU2
    ax3 = plt.subplot(3, 2, 3)  # Flex Sensor
    ax4 = plt.subplot(3, 2, 4)  # Float Sensor
    ax5 = plt.subplot(3, 2, 5)  # Alert Status
    ax6 = plt.subplot(3, 2, 6)  # Combined Overview
    
    def animate(frame):
        ts, r1, r2, mr, fx, fs, alrt = sensor_data.get_data()
        
        if len(ts) == 0:
            return
        
        # --- Subplot 1: MPU Vibration Comparison ---
        ax1.clear()
        ax1.plot(ts, r1, 'b-', linewidth=2, label='MPU1 RMS', alpha=0.8)
        ax1.plot(ts, r2, 'r-', linewidth=2, label='MPU2 RMS', alpha=0.8)
        ax1.axhline(y=VIBRATION_THRESHOLD, color='orange', linestyle='--', 
                   linewidth=2, label=f'Threshold ({VIBRATION_THRESHOLD})')
        ax1.set_title('MPU6050 Vibration (RMS)', fontweight='bold')
        ax1.set_ylabel('RMS Acceleration (g)')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        if len(ts) > 0:
            ax1.set_xlim(max(0, ts[-1] - 30), ts[-1] + 1)
        
        # --- Subplot 2: Difference between MPU1 and MPU2 ---
        ax2.clear()
        diff = np.array(r1) - np.array(r2)
        colors = ['red' if d < -0.05 else 'green' if d > 0.05 else 'gray' for d in diff]
        ax2.bar(range(len(diff))[-50:], diff[-50:], color=colors[-50:], alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.set_title('MPU Difference (RMS1 - RMS2)', fontweight='bold')
        ax2.set_ylabel('Difference (g)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # --- Subplot 3: Flex Sensor ---
        ax3.clear()
        colors_flex = ['red' if f > 0 else 'blue' if f < 0 else 'green' for f in fx]
        ax3.fill_between(ts, 0, fx, alpha=0.5, color='purple')
        ax3.plot(ts, fx, 'mo-', linewidth=2, markersize=4)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax3.set_title('Flex Sensor (Normalized: -1 to +1)', fontweight='bold')
        ax3.set_ylabel('Flex Value')
        ax3.set_ylim(-1.2, 1.2)
        ax3.grid(True, alpha=0.3)
        if len(ts) > 0:
            ax3.set_xlim(max(0, ts[-1] - 30), ts[-1] + 1)
        
        # --- Subplot 4: Float Sensor ---
        ax4.clear()
        float_binary = [1 if f == 0 else 0 for f in fs]  # 0 = water detected, 1 = normal
        ax4.step(ts, float_binary, where='post', linewidth=2, color='cyan')
        ax4.fill_between(ts, 0, float_binary, alpha=0.3, color='cyan')
        ax4.set_title('Float Sensor (0=Water Present, 1=Normal)', fontweight='bold')
        ax4.set_ylabel('Status')
        ax4.set_ylim(-0.2, 1.2)
        ax4.grid(True, alpha=0.3)
        if len(ts) > 0:
            ax4.set_xlim(max(0, ts[-1] - 30), ts[-1] + 1)
        
        # --- Subplot 5: Alert Status ---
        ax5.clear()
        alert_numeric = []
        alert_colors = []
        for a in alrt:
            if 'VIBRATION' in a or 'VIB' in a:
                alert_numeric.append(2)
                alert_colors.append('red')
            elif 'LEAK' in a:
                alert_numeric.append(1.5)
                alert_colors.append('orange')
            else:
                alert_numeric.append(0)
                alert_colors.append('green')
        
        ax5.bar(range(len(alert_numeric))[-50:], alert_numeric[-50:], 
               color=alert_colors[-50:], alpha=0.7)
        ax5.set_title('Alert Status', fontweight='bold')
        ax5.set_ylabel('Alert Level')
        ax5.set_yticks([0, 1.5, 2])
        ax5.set_yticklabels(['Normal', 'Leak', 'Vibration'])
        ax5.grid(True, alpha=0.3, axis='y')
        
        # --- Subplot 6: Combined Overview ---
        ax6.clear()
        ax6_twin1 = ax6.twinx()
        ax6_twin2 = ax6.twinx()
        ax6_twin2.spines['right'].set_position(('outward', 60))
        
        p1 = ax6.plot(ts, mr, 'b-', linewidth=2, label='Max RMS', alpha=0.8)
        p2 = ax6_twin1.plot(ts, fx, 'purple', linewidth=2, label='Flex', alpha=0.8)
        p3 = ax6_twin2.plot(ts, float_binary, 'cyan', linewidth=2, label='Float', alpha=0.8)
        
        ax6.set_title('Combined Sensor Overview', fontweight='bold')
        ax6.set_xlabel('Time (seconds)')
        ax6.set_ylabel('RMS (g)', color='b')
        ax6_twin1.set_ylabel('Flex (-1 to +1)', color='purple')
        ax6_twin2.set_ylabel('Float Status', color='cyan')
        ax6.tick_params(axis='y', labelcolor='b')
        ax6_twin1.tick_params(axis='y', labelcolor='purple')
        ax6_twin2.tick_params(axis='y', labelcolor='cyan')
        
        # Combined legend
        ps = p1 + p2 + p3
        labels = [p.get_label() for p in ps]
        ax6.legend(ps, labels, loc='upper left')
        ax6.grid(True, alpha=0.3)
        if len(ts) > 0:
            ax6.set_xlim(max(0, ts[-1] - 30), ts[-1] + 1)
        
        # Add common x-label
        fig.text(0.5, 0.02, 'Time (seconds)', ha='center', fontsize=11)
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    ani = animation.FuncAnimation(fig, animate, interval=100, blit=False, cache_frame_data=False)
    plt.show()

# ============================================================
# Main Program
# ============================================================
def main():
    print("=" * 60)
    print("ESP32 Bridge Health Monitoring - Live Plot")
    print("=" * 60)
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✓ Connected to {SERIAL_PORT}")
        print("Waiting for data from ESP32... (This may take a few seconds)\n")
        
    except Exception as e:
        print(f"✗ Connection Error: {e}")
        print(f"Available ports: Check your device manager or use 'python -m serial.tools.list_ports'")
        return
    
    # Create shared data storage
    sensor_data = SensorData(max_size=MAX_POINTS)
    
    # Start serial reader thread
    reader_thread = threading.Thread(target=serial_reader, args=(ser, None, sensor_data), daemon=True)
    reader_thread.start()
    
    # Give it time to receive first data
    import time
    time.sleep(2)
    
    # Start plotting
    try:
        plot_data(sensor_data)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        ser.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()