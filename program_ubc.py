import serial
import time
import csv

PORT = "COM3"
BAUDRATE = 9600
TIMEOUT = 1

def send(ser, cmd, delay=0.3):
    ser.write((cmd + '\r').encode())
    resp = ser.readline().decode(errors='ignore').strip()
    print(f"> {cmd}\n< {resp}")
    time.sleep(delay)
    return resp

def program_channels(csv_file):
    with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
        time.sleep(0.5)
        ser.reset_input_buffer()

        # Confirm connection and scanner model
        send(ser, "MDL")
        send(ser, "PRG")

        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 9:
                    continue

                _, channel, name, freq, mode, squelch, step, _, _ = row # CSV format: CIN,channel,name,freq,mode,squelch,step,xyz,xyz

                freq_int = int(freq.lstrip('0')) if freq.lstrip('0') else 0

                # format: CIN,<channel>,<name>,<freq>,<mode>,<squelch>,<step>,0,0
                cmd = f"CIN,{int(channel)},{name},{freq_int},{mode},{squelch},{step},0,0"
                resp = send(ser, cmd)

                if resp != "CIN,OK":
                    print(f"Error programming channel {channel}: {resp}")

                # Optional: verify channel by querying back
                send(ser, f"CIN,{int(channel)}")

        send(ser, "EPG")
        print("[✓] Programming complete. Please restart the scanner to apply changes.")

if __name__ == "__main__":
    program_channels("RRUK_presets/AllMilFreqsProgram.R125")
