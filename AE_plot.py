import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

SERIAL_PORT = "COM3"  # replace with your ESP32 COM port
BAUD_RATE = 115200
WINDOW_SIZE = 300

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

rms_deque = deque([0]*WINDOW_SIZE, maxlen=WINDOW_SIZE)

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_ylim(0, max(rms_deque)*1.2)
ax.set_xlim(0, WINDOW_SIZE)
ax.set_xlabel("Samples")
ax.set_ylabel("RMS (g)")
ax.set_title("Real-Time AE Detection")

def update(frame):
    # Read all available lines
    while ser.in_waiting:
        line_bytes = ser.readline().decode('utf-8').strip()
        if ',' in line_bytes:
            try:
                _, rms = line_bytes.split(',')
                rms = float(rms)
                rms_deque.append(rms)
            except:
                pass

    line.set_data(range(len(rms_deque)), list(rms_deque))
    ax.set_ylim(0, max(list(rms_deque))*1.2 + 0.001)  # auto scale with buffer
    return line,

ani = animation.FuncAnimation(fig, update, blit=True, interval=50, cache_frame_data=False)
plt.show()
