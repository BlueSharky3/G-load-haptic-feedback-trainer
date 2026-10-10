# Demo runbook (handoff 04)

## Milestones (do them in order, tick them off)

- [ ] **1. Cuff alone.** Pump inflates and valve vents from the 8xAA pack, no Arduino. Inflate and vent times measured.
- [ ] **2. Firmware alone.** Sketch uploaded, real timings entered, `TEST` works in Serial Monitor.
- [ ] **3. End to end, demo mode.** `bridge.py --demo` squeezes the real cuff. **Record the backup video now.**
- [ ] **4. Live sim.** `bridge.py --live` with FlightGear. If it isn't working by the cutoff time, demo mode is the plan.
- [ ] **5. Rehearse twice** with someone wearing the cuff, full pitch, timed.

Live-sim cutoff time: ______ (pick one; after it, stop working on live mode and polish the demo).

## Setup (every time)

1. 8xAA pack in, **kill switch OFF**.
2. Arduino plugged into the Mac. Relays silent, LEDs off.
3. Terminal:
   ```bash
   cd ~/hackphs/repo/bridge
   .venv/bin/python bridge.py --demo --print
   ```
   G lines scroll → software is fine. Ctrl+C.
4. Cuff on the volunteer's thigh, over clothes, snug but not tight. Kill switch in **their** hand.
5. Kill switch ON. Run for real:
   ```bash
   .venv/bin/python bridge.py --demo --loop     # or --live
   ```
6. Press ENTER for a spike whenever you want a squeeze on cue.

## Live mode with FlightGear

1. **Turn on FlightGear's web server.** In the FlightGear launcher, open **Settings** and type this in the
   **Additional Settings** box at the bottom:
   ```
   --httpd=5400
   ```
2. Fly, and use a JSBSim aircraft. The default Cessna 172P is fine.
3. Check it in a browser: open http://localhost:5400/json/fdm/jsbsim/accelerations/Nz. You should see a `"value"`
   close to **1.0** while flying level. If it's a number, live mode will work.
4. `.venv/bin/python bridge.py --live`. It prints which property it's reading, then "FlightGear connected".
5. Pull back on the yoke: G rises, cuff squeezes. Level off: it vents.
6. If FlightGear runs on another computer: `--sim-host <that computer's IP>`.

The bridge tries these G properties in order and uses the first that answers:
`/fdm/jsbsim/accelerations/Nz`, `/accelerations/pilot-gdamped`, `/accelerations/pilot-g`.
To force one: `--fg-prop /accelerations/pilot-gdamped`. You can browse every property at http://localhost:5400.

**Check before the demo:** level flight reads about 1.0, a hard pull reads 3 or more, and it moves while you fly.
If it sits at exactly 1.0 during a pull, that property isn't updating for this aircraft. Force another one.

Test live mode without FlightGear:
```bash
.venv/bin/python fake_flightgear.py       # terminal 1
.venv/bin/python bridge.py --live --print # terminal 2
```

X-Plane also works (`--live --sim xplane`, no X-Plane setup needed; test with `fake_xplane.py`).

## Fallback ladder (if something breaks on stage, step down one rung)

1. Live FlightGear
2. `--demo --loop` (scripted flight + ENTER spikes)
3. Serial Monitor, type `TEST` (proves the hardware alone)
4. The backup video

Say it honestly: "the live sim link is flaky, so here's the same cuff on a scripted flight."

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "No Arduino found" | Cable is charge-only, or Serial Monitor has the port open | Swap the cable; close Serial Monitor |
| Relays click on at power-up | Relay board is active-high | `RELAY_ACTIVE_LOW = false`, re-upload |
| Relays click but cuff doesn't fill | Kill switch off, flat batteries, tube off a barb, valve stuck open | Check switch, measure pack (~12V fresh), re-seat tubes |
| Cuff fills then deflates every half second | Script not sending steadily | Make sure `bridge.py` is running, not just Serial Monitor |
| Cuff lags way behind G | Pump is slow for the bladder | Stretch `DEMO_PROFILE` timings; lower `gFull` so it fills sooner |
| Never reaches full squeeze | `pumpMaxRunMs` shorter than `inflateMs` | Set the cap ~25% above `inflateMs` |
| Squeeze weaker as the day goes on | AAs sagging | Fresh batteries |
| "Waiting for FlightGear..." forever | FlightGear started without `--httpd=5400`, or still loading | See live mode notes above |
| Connected but G stuck at one value | Property exists but this aircraft doesn't update it | Try another with `--fg-prop` (see live mode notes) |

## Safety (say this in the pitch)

- Wearer holds a kill switch that cuts power, which stops the pump and vents the cuff.
- Vent valve is normally open: power loss, unplugging or an Arduino reset all deflate.
- No signal for 0.5 s → vent. Pump run time hard-capped. Pump never runs with the vent open.
- Max squeeze set on the bench to "firm but comfortable". Over clothes only. Anyone can stop at any time.
  Volunteers with circulation problems sit it out.

## Batteries and spares

- Spare AAs (pump + valve current drains them; holding pressure keeps the valve powered).
- Cold-spare Arduino with the sketch already uploaded.
- Spare tubing, zip ties, a second USB cable.
