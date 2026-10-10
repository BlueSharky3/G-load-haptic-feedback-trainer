# Demo runbook (handoff 04)

## Milestones (do them in order, tick them off)

- [ ] **1. Cuff alone.** Pump inflates and valve vents from the 8xAA pack, no Arduino. Inflate and vent times measured.
- [ ] **2. Firmware alone.** Sketch uploaded, real timings entered, `TEST` works in Serial Monitor.
- [ ] **3. End to end, demo mode.** `bridge.py --demo` squeezes the real cuff. **Record the backup video now.**
- [ ] **4. Live sim.** `bridge.py --live` with X-Plane. If it isn't working by the cutoff time, demo mode is the plan.
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

## Live mode with X-Plane

1. Start X-Plane on the Mac and get flying (a small aerobatic plane pulls G easily).
2. `.venv/bin/python bridge.py --live`. It prints "X-Plane connected" once data flows.
3. Pull back on the stick: G rises, cuff squeezes. Level off: it vents.
4. If X-Plane runs on another computer: `--xplane-host <that computer's IP>`.

No settings needed inside X-Plane. The script asks for `sim/flightmodel/forces/g_nrml` over UDP port 49000.
If nothing arrives, check the name exists in `X-Plane/Resources/plugins/DataRefs.txt` (or the free DataRefEditor
plugin), and pass the right one with `--dataref`.

Test live mode without X-Plane:
```bash
.venv/bin/python fake_xplane.py          # terminal 1
.venv/bin/python bridge.py --live --print # terminal 2
```

## Fallback ladder (if something breaks on stage, step down one rung)

1. Live X-Plane
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
| "Waiting for X-Plane..." forever | X-Plane not running, wrong host, wrong dataref | See live mode notes above |

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
