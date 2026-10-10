"""
hackPHS 2026 - G-load bridge (handoff 03)

What this does, in one sentence:
    Every 1/20th of a second, pick a G value and send it to the Arduino
    as a line of text like "G:3.20".

How to run it (from the bridge folder):
    .venv/bin/python bridge.py --demo --print     # no Arduino needed, just prints
    .venv/bin/python bridge.py --demo             # sends to the real Arduino
    .venv/bin/python bridge.py --demo --loop      # repeat the demo forever

While it runs: press ENTER to trigger a 6 G spike. Press Ctrl+C to quit.
"""

import argparse
import csv
import os
import threading
import time
from datetime import datetime

import serial
import serial.tools.list_ports


# ---------------------------------------------------------------------------
# SETTINGS - the numbers you are most likely to change
# ---------------------------------------------------------------------------

BAUD = 115200          # serial speed, must match the Arduino sketch
SEND_RATE_HZ = 20      # how many lines per second we send
MIN_G, MAX_G = 0.0, 9.0

# The pretend flight for demo mode: (seconds since start, G at that moment).
# Between two points the G value slides smoothly from one to the other.
# Stretch these out if the cuff turns out to inflate slowly.
DEMO_PROFILE = [
    (0, 1.0),
    (3, 1.0),
    (7, 5.0),    # first pull up to 5 G
    (10, 5.0),   # hold it
    (14, 1.0),   # back to level flight
    (17, 1.0),
    (21, 7.0),   # bigger pull to 7 G
    (24, 7.0),
    (28, 1.0),
    (31, 1.0),
]

# What happens when you press ENTER: ramp up, hold, ramp down.
SPIKE_G = 6.0
SPIKE_RAMP_UP = 1.0    # seconds
SPIKE_HOLD = 2.0
SPIKE_RAMP_DOWN = 1.5


# ---------------------------------------------------------------------------
# Working out the G value
# ---------------------------------------------------------------------------

def slide(a, b, fraction):
    """Linear interpolation: 'fraction' of the way from a to b (0.0 to 1.0)."""
    return a + (b - a) * fraction


def demo_g(t):
    """G value from DEMO_PROFILE at t seconds into the demo."""
    for (t1, g1), (t2, g2) in zip(DEMO_PROFILE, DEMO_PROFILE[1:]):
        if t1 <= t <= t2:
            return slide(g1, g2, (t - t1) / (t2 - t1))
    return DEMO_PROFILE[-1][1]   # past the end: stay at the last value


def spike_g(t):
    """Extra G from an ENTER-key spike, t seconds after the key was pressed.
    Returns None when the spike is over."""
    if t < SPIKE_RAMP_UP:
        return slide(1.0, SPIKE_G, t / SPIKE_RAMP_UP)
    t -= SPIKE_RAMP_UP
    if t < SPIKE_HOLD:
        return SPIKE_G
    t -= SPIKE_HOLD
    if t < SPIKE_RAMP_DOWN:
        return slide(SPIKE_G, 1.0, t / SPIKE_RAMP_DOWN)
    return None


def clamp(g):
    """Keep G inside the range the Arduino accepts."""
    return max(MIN_G, min(MAX_G, g))


# ---------------------------------------------------------------------------
# Listening for the ENTER key (runs in the background)
# ---------------------------------------------------------------------------

spike_started_at = None   # time of the last ENTER press, or None


def listen_for_enter():
    global spike_started_at
    while True:
        try:
            input()
        except EOFError:
            return
        spike_started_at = time.time()
        print(">>> SPIKE!")


# ---------------------------------------------------------------------------
# Talking to the Arduino
# ---------------------------------------------------------------------------

def find_arduino_port():
    """Look through USB serial devices for something that looks like an Arduino.
    Genuine Unos show up as 'usbmodem', cheap clones as 'usbserial'/'wchusbserial'."""
    for p in serial.tools.list_ports.comports():
        name = p.device.lower()
        desc = (p.description or "").lower()
        if "usbmodem" in name or "usbserial" in name or "arduino" in desc or "ch340" in desc:
            return p.device
    return None


def connect(port_override):
    """Open the serial port. Keeps trying until it works (Ctrl+C to give up)."""
    while True:
        port = port_override or find_arduino_port()
        if port is None:
            print("No Arduino found. Plug it in... (retrying)")
        else:
            try:
                ser = serial.Serial(port, BAUD, timeout=0)
                print(f"Connected to {port}. Waiting 2 s for the Arduino to reboot...")
                time.sleep(2)   # opening the port resets the Uno
                return ser
            except serial.SerialException as e:
                print(f"Could not open {port}: {e} (retrying)")
        time.sleep(1)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    global spike_started_at

    parser = argparse.ArgumentParser(description="Send G-load to the Arduino.")
    parser.add_argument("--demo", action="store_true", help="play the scripted demo flight")
    parser.add_argument("--print", action="store_true", help="print lines instead of sending them")
    parser.add_argument("--loop", action="store_true", help="repeat the demo forever")
    parser.add_argument("--port", help="serial port, e.g. /dev/tty.usbmodem1101 (default: auto-detect)")
    args = parser.parse_args()

    if not args.demo:
        print("Live sim mode isn't built yet. Run with --demo for now.")
        return

    # Open the Arduino connection unless we're only printing.
    ser = None if args.print else connect(args.port)

    # Start a CSV log file for this run, e.g. logs/run-2026-10-10_14-03-22.csv
    os.makedirs("logs", exist_ok=True)
    log_path = datetime.now().strftime("logs/run-%Y-%m-%d_%H-%M-%S.csv")
    log_file = open(log_path, "w", newline="")
    log = csv.writer(log_file)
    log.writerow(["time_s", "g_sent", "source"])
    print(f"Logging to {log_path}")

    threading.Thread(target=listen_for_enter, daemon=True).start()
    print("Running. Press ENTER for a spike, Ctrl+C to quit.\n")

    start = time.time()
    demo_length = DEMO_PROFILE[-1][0]

    try:
        while True:
            now = time.time()
            t = now - start

            # 1. Decide on G
            if args.loop:
                t_demo = t % demo_length
            elif t > demo_length:
                print("Demo finished.")
                break
            else:
                t_demo = t
            g = demo_g(t_demo)
            source = "demo"

            if spike_started_at is not None:
                s = spike_g(now - spike_started_at)
                if s is None:
                    spike_started_at = None      # spike over
                else:
                    g = max(g, s)                # spike wins if it's higher
                    source = "spike"

            g = clamp(g)
            line = f"G:{g:.2f}\n"

            # 2. Send it (or just print it)
            if args.print:
                print(line, end="")
            else:
                try:
                    ser.write(line.encode())
                    ser.read(ser.in_waiting or 1)   # throw away anything the Arduino sends back
                except (serial.SerialException, OSError):
                    print("Lost the Arduino! Reconnecting...")
                    ser.close()
                    ser = connect(args.port)

            # 3. Write it to the log
            log.writerow([f"{t:.2f}", f"{g:.2f}", source])

            # 4. Wait until it's time for the next line
            time.sleep(max(0, 1 / SEND_RATE_HZ - (time.time() - now)))

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        log_file.close()
        if ser:
            ser.close()   # Arduino stops hearing us -> vents the cuff on its own


if __name__ == "__main__":
    main()
