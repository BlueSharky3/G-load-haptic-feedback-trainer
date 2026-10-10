"""
Pretends to be FlightGear's web server (what you get with --httpd=5400), so
live mode can be tested without the sim.

Serves one G property as JSON, swinging between 1 G and 6 G every ~10 s.
Every other property path returns 404, like a property that doesn't exist.

    Terminal 1:  .venv/bin/python fake_flightgear.py
    Terminal 2:  .venv/bin/python bridge.py --live --print

Try --prop /accelerations/pilot-gdamped to check the bridge falls back to
another property. Don't run this while real FlightGear uses port 5400.
"""

import argparse
import json
import math
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=5400)
parser.add_argument("--prop", default="/fdm/jsbsim/accelerations/Nz",
                    help="the one property this fake FlightGear has")
args = parser.parse_args()
start = time.time()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path != "/json" + args.prop:
            self.send_error(404)
            return
        g = 3.5 - 2.5 * math.cos((time.time() - start) * 2 * math.pi / 10)   # 1..6 G
        body = json.dumps({
            "path": args.prop,
            "name": args.prop.rsplit("/", 1)[-1],
            "value": round(g, 4),
            "type": "double",
            "index": 0,
            "nChildren": 0,
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass   # keep the terminal quiet


print(f"Fake FlightGear on http://localhost:{args.port}/json{args.prop} (Ctrl+C to quit)")
try:
    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
except KeyboardInterrupt:
    print("\nStopped.")
