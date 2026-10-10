# Devpost draft

Fill **[brackets]** with real data. Paste section by section into Devpost.

## Name
G-Load Haptic Trainer

## Tagline
Feel the squeeze of a G-suit in your flight sim, for under **[total]** dollars.

## Inspiration
Flight sims look and sound real, but your body has no idea you just pulled 7 G. Real pilots feel G through their
G-suit: bladders on the legs that inflate harder as G rises. We wanted that cue at home, cheaply.

## What it does
A pressure cuff on your thigh inflates in proportion to the live G-load in your flight sim. Pull up hard and it
squeezes; level off and it lets go. It's a **G-load haptic feedback trainer**, not a G-force simulator: it can't
create real acceleration, but it gives the same pressure cue a G-suit does, in time with your flight.

## How we built it
- **Sim link:** a Python script reads G-load from X-Plane over UDP (or plays a scripted demo flight) and sends it to
  an Arduino over USB serial, 20 times a second.
- **Firmware:** the Arduino maps G to a target fill level and drives a 12V air pump and a vent solenoid through relays.
  With no pressure sensor, it estimates fill from pump and vent timing, re-zeroing each time G returns to 1.
- **Hardware:** blood pressure cuff bladder, 12V mini pump, normally-open solenoid valve, check valve, 8xAA pack.
- **Safety:** fails deflated on power loss, signal loss (0.5 s) or a board reset; pump run time capped; wearer kill switch.
- The control logic is unit-tested on a laptop (dead-man timeout, pump cap, deadband, garbage serial input).

## Challenges we ran into
[Fill in on the day. Candidates: confirming the pump inflates rather than sucks; the normally-open valve flipping
the control logic; sourcing a T-fitting; cuff fill speed vs. how fast G changes; open-loop drift.]

## Accomplishments we're proud of
[e.g. it works end to end on stage; the safety design; built and tested in one day.]

## What we learned
[Fill in.]

## What's next
Pressure sensor for closed-loop control, second leg, lateral G (one side squeezes harder in turns), spoken
anti-G straining cues.

## Built with
python, pyserial, arduino, c++, x-plane, udp

## Parts list (from receipts)

| Part | Price |
|---|---|
| Blood pressure cuff + bladder | [ ] |
| 12V mini air pump | [ ] |
| Solenoid valve (normally open) | [ ] |
| Silicone tubing | [ ] |
| T-fittings / check valve | [ ] |
| 8xAA holder | [ ] |
| Zip ties, velcro, enclosure | [ ] |
| Arduino Uno (already owned) | [ ] |
| 4-channel relay module (already owned) | [ ] |
| **Total** | **[ ]** |

## Media checklist
- [ ] 30 s video: cuff squeezing during a sim pull (record as soon as milestone 3 works)
- [ ] Photo of the hardware laid out
- [ ] Photo of someone wearing it
- [ ] G-vs-time graph from a `bridge/logs/` CSV (open in Numbers → line chart)
