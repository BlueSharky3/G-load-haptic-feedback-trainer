# G-load haptic feedback trainer (hackPHS 2026)

A thigh pressure cuff that inflates in proportion to live G-load from a flight sim, like a G-suit bladder.
It is a G-load haptic feedback trainer, not a G-force simulator.

```
sim / demo -> bridge/bridge.py (laptop) -> USB serial "G:<float>\n" @ 20 Hz -> Arduino Uno -> relays -> pump + vent solenoid -> cuff
```

## Folders
- `bridge/` - Python laptop script (handoff 03). Demo mode works; live sim mode not built yet.
- `firmware/` - Arduino sketch (handoff 02), to be added.

## Run the bridge (Mac)
```bash
cd bridge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python bridge.py --demo --print   # no Arduino needed
.venv/bin/python bridge.py --demo           # real Arduino, auto-detects the port
```
Press ENTER for a 6 G spike, Ctrl+C to quit. Each run logs to `bridge/logs/`.
