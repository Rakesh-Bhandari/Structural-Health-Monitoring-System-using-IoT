import serial
import time

# CONFIGURATION
SERIAL_PORT = "COM3"   # Check if this is correct
BAUD_RATE = 115200     # We will verify if this is correct

print(f"--- ATTEMPTING CONNECTION TO {SERIAL_PORT} AT {BAUD_RATE} BAUD ---")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2.0)
    print(f"✓ SUCCESSFULLY CONNECTED TO {SERIAL_PORT}")
    print("Waiting for data (press Ctrl+C to stop)...")
    
    while True:
        if ser.in_waiting > 0:
            # Read the raw line
            raw_line = ser.readline()
            
            # Try to decode it
            try:
                decoded_line = raw_line.decode('utf-8').strip()
                print(f"RECEIVED: {decoded_line}")
            except UnicodeDecodeError:
                print(f"RAW (Decoding Failed - Baud Rate mismatch?): {raw_line}")
        else:
            # Simple heartbeat to show script is alive
            time.sleep(0.1)

except serial.SerialException as e:
    print(f"ERROR: Could not open port {SERIAL_PORT}. Is it open in another window?")
    print(f"Details: {e}")
except KeyboardInterrupt:
    print("\nTest Stopped.")