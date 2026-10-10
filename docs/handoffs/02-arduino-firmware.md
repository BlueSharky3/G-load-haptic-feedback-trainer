# Handoff 02: Arduino firmware + relay wiring

Project: hackPHS 2026 haptic G-load trainer. Full plan: `~/hackphs/project-plan.md`.
A laptop script streams a G value over USB serial; the Arduino turns it into pump + vent solenoid actions on a thigh cuff. It is a G-load haptic feedback trainer, not a G-force simulator.

## Status (2026-10-10)
Draft sketch is in `firmware/g_trainer/` with a README. It implements everything below for the NO valve and passes 20 laptop unit tests. Your job now: upload it, check relay polarity, enter 01's timings, run the hand test. Read `firmware/README.md`.

## Your job
Write the Arduino Uno sketch and wire the 4-channel relay board. You own everything between "serial bytes arrive" and "pump/solenoid switch".

## Hardware you have
- 2x Arduino Uno (use one, keep one as a cold spare), breadboard, jumpers, USB cables.
- 4-channel relay module (5V logic; switches 12V loads fine).
- 12V from the 8xAA pack goes to the relay COM terminals, never through the Arduino.
- Servo in the bin (stretch only, ignore for now).

## Serial contract (agreed with handoff 03, do not change without telling them)
- 115200 baud, newline-terminated ASCII lines.
- Laptop -> Arduino: `G:<float>\n`, e.g. `G:3.2\n`, sent about 20 times per second. Valid range 0.0 to 9.0.
- Arduino -> laptop: optional `OK\n` or nothing. Keep it simple.
- Any malformed line: ignore it, do not crash.

## Pin plan (change if you must, but record it here)
- Relay IN1 = pump, pin 7
- Relay IN2 = vent solenoid, pin 8
- IN3/IN4 reserved for the second leg (stretch).
- Many relay boards are ACTIVE-LOW. Test it. Make the idle state of every pin "relay off" before setup() finishes.

## Control logic (open loop, no pressure sensor in the parts list)
- Map G to a target fill level: 1 G or below = empty, about 6 G or more = full squeeze. Linear in between.
- Track estimated fill by integrating pump-on and vent-on time using the inflate/vent timings from handoff 01. Pump when estimate < target, vent when estimate > target, hold otherwise. Add a deadband so the relays do not chatter.
- Dead-man timeout: no valid serial line for 500 ms means vent fully and stop the pump. Fail safe is always deflated.
- Hard cap on continuous pump run time (get the number from handoff 01). Pump and vent are never on at the same time.
- Solenoid is NORMALLY OPEN (from 01): energize to close/hold, de-energize to vent. Pump only runs with the valve energized.

## Do first
Hand-test with the Serial Monitor typing `G:6.0` and `G:1.0` before the laptop script exists. Include a self-test command (e.g. `TEST\n` runs inflate 2 s, vent 2 s) so hardware can be checked without software.

## Open question
None. Event is today.
