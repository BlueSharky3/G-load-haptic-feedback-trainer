"""
hackPHS 2026 - G-load bridge (handoff 03)

What this does, in one sentence:
    Every 1/20th of a second, pick a G value and send it to the Arduino
    as a line of text like "G:3.20".

How to run it (from the bridge folder):
    .venv/bin/python bridge.py --demo --print     # no Arduino needed, just prints
    .venv/bin/python bridge.py --demo             # sends to the real Arduino
    .venv/bin/python bridge.py --demo --loop      # repeat the demo forever
    .venv/bin/python bridge.py --live             # read G from X-Plane

While it runs: press ENTER to trigger a 6 G spike. Press Ctrl+C to quit.
"""

import argparse
import csv
import os
import socket
import struct
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

# Live mode (X-Plane). X-Plane listens for requests on UDP port 49000 and
# sends the value back to us. g_nrml = vertical G-load in g (1.0 in level flight).
XPLANE_PORT = 49000
XPLANE_DATAREF = "sim/flightmodel/forces/g_nrml"
LIVE_TIMEOUT_S = 1.0   # no data from X-Plane this long -> stop sending (cuff vents)
SMOOTHING = 0.4        # 0..1, how far to move toward each new reading. 1 = no smoothing


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
# Reading G from X-Plane
# ---------------------------------------------------------------------------

class XPlane:
    """Asks X-Plane to stream one value (a 'dataref') to us over UDP.
    No setup needed inside X-Plane: we send an RREF request, it replies."""

    INDEX = 1   # our label for the value; X-Plane sends it back with each reply

    def __init__(self, host, dataref):
        self.addr = (host, XPLANE_PORT)
        self.dataref = dataref
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 0))   # any free port; replies come back here
        self.sock.setblocking(False)
        self.last_value = None
        self.last_rx = 0.0
        self.last_request = 0.0

    def _request(self, rate_hz):
        # 'RREF', a zero byte, how often (per second), our index, the dataref name
        msg = struct.pack("<4sxii400s", b"RREF", rate_hz, self.INDEX, self.dataref.encode())
        try:
            self.sock.sendto(msg, self.addr)
        except OSError:
            pass   # network hiccup; we retry anyway

    def read(self):
        """Newest G from X-Plane, or None if nothing has arrived for a while."""
        now = time.time()
        # (Re)subscribe every 2 s until data flows - covers X-Plane starting late.
        if now - self.last_rx > LIVE_TIMEOUT_S and now - self.last_request > 2:
            self._request(SEND_RATE_HZ)
            self.last_request = now
        while True:   # drain every packet waiting, keep the newest value
            try:
                data, _ = self.sock.recvfrom(2048)
            except (BlockingIOError, OSError):
                break
            if not data.startswith(b"RREF") or len(data) < 13:
                continue
            for i in range(5, len(data) - 7, 8):   # 8-byte (index, value) pairs
                idx, value = struct.unpack("<if", data[i:i + 8])
                if idx == self.INDEX and value == value:   # value == value skips NaN
                    self.last_value = value
                    self.last_rx = now
        if now - self.last_rx > LIVE_TIMEOUT_S:
            return None
        return self.last_value

    def close(self):
        self._request(0)   # rate 0 = unsubscribe
        self.sock.close()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    global spike_started_at

    parser = argparse.ArgumentParser(description="Send G-load to the Arduino.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="play the scripted demo flight")
    mode.add_argument("--live", action="store_true", help="read live G from X-Plane")
    parser.add_argument("--print", action="store_true", help="print lines instead of sending them")
    parser.add_argument("--loop", action="store_true", help="repeat the demo forever")
    parser.add_argument("--port", help="serial port, e.g. /dev/tty.usbmodem1101 (default: auto-detect)")
    parser.add_argument("--xplane-host", default="127.0.0.1",
                        help="IP of the computer running X-Plane (default: this one)")
    parser.add_argument("--dataref", default=XPLANE_DATAREF, help="X-Plane value to read")
    args = parser.parse_args()

    # Open the Arduino connection unless we're only printing.
    ser = None if args.print else connect(args.port)
    xp = XPlane(args.xplane_host, args.dataref) if args.live else None

    # Start a CSV log file for this run, e.g. logs/run-2026-10-10_14-03-22.csv
    os.makedirs("logs", exist_ok=True)
    log_path = datetime.now().strftime("logs/run-%Y-%m-%d_%H-%M-%S.csv")
    log_file = open(log_path, "w", newline="")
    log = csv.writer(log_file)
    log.writerow(["time_s", "g_raw", "g_sent", "source"])
    print(f"Logging to {log_path}")

    threading.Thread(target=listen_for_enter, daemon=True).start()
    print("Running. Press ENTER for a spike, Ctrl+C to quit.\n")

    start = time.time()
    demo_length = DEMO_PROFILE[-1][0]
    smoothed = None
    waiting_shown = False

    try:
        while True:
            now = time.time()
            t = now - start

            # 1. Decide on G
            if args.live:
                raw = xp.read()
                if raw is None:
                    # No data from X-Plane: send nothing, so the Arduino vents.
                    if not waiting_shown:
                        print(f"Waiting for X-Plane at {args.xplane_host}... (cuff stays vented)")
                        waiting_shown = True
                    smoothed = None
                    time.sleep(1 / SEND_RATE_HZ)
                    continue
                if waiting_shown:
                    print("X-Plane connected.")
                    waiting_shown = False
                smoothed = raw if smoothed is None else smoothed + SMOOTHING * (raw - smoothed)
                g = smoothed
                source = "live"
            else:
                if args.loop:
                    t_demo = t % demo_length
                elif t > demo_length:
                    print("Demo finished.")
                    break
                else:
                    t_demo = t
                raw = g = demo_g(t_demo)
                source = "demo"

            if spike_started_at is not None:
                s = spike_g(now - spike_started_at)
                if s is None:
                    spike_started_at = None      # spike over
                elif s > g:
                    g = s                        # spike wins if it's higher
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
            log.writerow([f"{t:.2f}", f"{raw:.2f}", f"{g:.2f}", source])
            log_file.flush()   # save now, so a crash doesn't lose the log

            # 4. Wait until it's time for the next line
            time.sleep(max(0, 1 / SEND_RATE_HZ - (time.time() - now)))

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        log_file.close()
        if xp:
            xp.close()
        if ser:
            ser.close()   # Arduino stops hearing us -> vents the cuff on its own


if __name__ == "__main__":
    main()
