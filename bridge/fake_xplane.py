"""
Pretends to be X-Plane so live mode can be tested without the sim.

Listens on UDP 49000 like X-Plane does, answers RREF requests, and streams a
G value that swings between 1 G and 6 G every ~10 s.

    Terminal 1:  .venv/bin/python fake_xplane.py
    Terminal 2:  .venv/bin/python bridge.py --live --print

Don't run this at the same time as real X-Plane on the same computer.
"""

import math
import socket
import struct
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 49000))
sock.settimeout(0.01)
print("Fake X-Plane listening on 127.0.0.1:49000 (Ctrl+C to quit)")

subscriber = None   # (address, index, rate_hz)
start = time.time()
next_send = 0.0

try:
    while True:
        try:
            data, addr = sock.recvfrom(2048)
            if data.startswith(b"RREF") and len(data) >= 413:
                _, rate, index, name = struct.unpack("<4sxii400s", data[:413])
                name = name.split(b"\0")[0].decode()
                if rate > 0:
                    subscriber = (addr, index, rate)
                    print(f"Subscribed: {name} at {rate} Hz -> {addr}")
                else:
                    subscriber = None
                    print("Unsubscribed")
        except socket.timeout:
            pass

        now = time.time()
        if subscriber and now >= next_send:
            addr, index, rate = subscriber
            g = 3.5 - 2.5 * math.cos((now - start) * 2 * math.pi / 10)   # 1..6 G
            sock.sendto(b"RREF\0" + struct.pack("<if", index, g), addr)
            next_send = now + 1 / rate
except KeyboardInterrupt:
    print("\nStopped.")
