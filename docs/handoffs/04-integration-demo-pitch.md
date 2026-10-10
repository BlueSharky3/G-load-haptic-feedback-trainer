# Handoff 04: Integration, demo, pitch

Project: hackPHS 2026 haptic G-load trainer ("Into the Skies"). Full plan: `~/hackphs/project-plan.md`.
Tracks on offer: ElevenLabs (voice), Cybersecurity, Codeset. Pick only what genuinely fits.

## Status (2026-10-10)
Drafts ready: `docs/demo-runbook.md` (milestone checklist, setup, fallback ladder, troubleshooting), `pitch/pitch-script.md`, `pitch/devpost.md`. Fill the bracketed numbers from receipts and measurements. Pick a live-sim cutoff time.

## Your job
Own the glue: make the other three pieces work together, run the demo, write the Devpost, and build the pitch. Integration is the step that always eats more time than planned, so start the real integration test early, not in the last two hours.

## Team pieces
- 01 hardware: cuff + pump + solenoid, timings.
- 02 firmware: Arduino reads `G:<float>\n`, drives relays.
- 03 software: sim -> serial bridge, with `--demo` mode.
Serial contract is in 02 and 03: 115200 baud, `G:<float>\n`, about 20 Hz.

## Milestones
1. Hardware alone inflates and vents from a bare 12V supply.
2. Firmware responds to typed `G:` lines in the Serial Monitor.
3. Bridge in `--demo` mode drives the real cuff end to end. This is the demo-safe path. Get here before attempting live sim.
4. Live sim hooked up. If it flakes, demo mode is the fallback and we say so honestly.
5. Rehearse the demo at least twice, with someone actually wearing the cuff.

## Pitch rules
- Framing: "G-load haptic feedback trainer". It is NOT a real G-force simulator (impossible cheap, it needs real acceleration). Say this explicitly. It survives technical questions, an oversold claim does not.
- Hook: commercial motion rigs cost $5k to $50k+ (find one real product to cite, or drop it), this is under $150 (from receipts). Same squeeze principle as a real G-suit bladder. Don't claim Air Force trainers use squeeze cues without a source.
- Know sim-racing belt tensioners and G-seats before a judge asks how this differs.
- Do not use a "future CS teacher" backstory. It does not connect to the project.
- Cost number must come from the real receipts. Add them up, do not estimate.

## Devpost checklist
- Short description, what it does, how it is built, challenges, what is next.
- Photos/video of the real hardware working. A 30-second clip of cuff squeezing during a sim pull is the best asset we can have, so record one early as backup.
- Parts list with prices.

## Risks to watch
- Live hardware demo flakiness is the main risk, not the idea. Keep a spare cuff/bladder if budget allows, and the cold-spare Arduino.
- One working zone beats two half-wired zones. Say no to stretch goals (second leg, harness servo, rib bladders) until the core runs on stage.
- Safety: hard time cap on pump runs, vent on serial loss. Mention it in the pitch, judges like it.

## Open question
None. Event is today.
