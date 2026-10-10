# Pitch script (~2 minutes + live demo)

Blanks in **[brackets]** need real numbers before you say them. Don't fill them with guesses.

## 1. Hook (15 s)
"Pilots pulling hard turns get squeezed by their G-suit. Inflatable bladders on the legs push harder the more G they
pull. Sim pilots never feel that. We built a cuff that does it, for **[total from receipts]** dollars."

## 2. What it is, and what it isn't (15 s)
"To be clear: this is a **G-load haptic feedback trainer**, not a G-force simulator. Real G needs real acceleration.
You can't fake that cheaply. What we *can* give you is the same pressure cue a G-suit gives, timed to your flight."

(Say this before a judge asks. It's the line that survives technical questions.)

## 3. Live demo (45 s)
- Volunteer wears the cuff, kill switch in hand.
- Start the flight (live FlightGear, or `--demo` if live is flaky; say which).
- Call out the pulls: "Here's 5 G... easing off... now 7." Hit ENTER for an on-cue spike if needed.
- Ask the volunteer what they feel.

## 4. How it works (20 s)
"The sim's G-load goes to a Python script on the laptop, then over USB to an Arduino 20 times a second. The Arduino
switches a 12-volt pump and a vent valve. With no pressure sensor, it estimates how full the cuff is from pump and
vent timing, and re-zeroes every time you level off."

## 5. Safety (15 s)
"Everything fails deflated. The vent valve opens with no power. Lose the signal for half a second and it vents.
The pump has a hard time limit. And the wearer holds a kill switch."

## 6. What's next (10 s)
Pick one or two: a pressure sensor for closed-loop control, a second leg, lateral G (squeeze one side harder
in a turn), spoken straining cues for anti-G training.

## Likely judge questions
| Question | Answer |
|---|---|
| Isn't this just a blood pressure cuff? | The cuff is off the shelf; the control loop, safety design and sim link are what we built. |
| How is this different from sim-racing belt tensioners / G-seats? | Look these up before pitching so you can answer: they pull you into the seat; this mimics the G-suit leg squeeze specifically, at **[price]**. |
| Why open loop? | No pressure sensor in the budget. Time-based estimate plus re-zero on every return to 1 G. A sensor is the first upgrade. |
| How fast does it respond? | **[measured inflate time]** to full. Honest answer, plus what would speed it up (bigger pump, smaller bladder). |
| Is it safe? | Section 5. |

## Claims to verify before saying them
- "Commercial motion rigs cost $5k to $50k+": find one real product and price, or drop it.
- Don't say it's what the Air Force trains with unless you have a source. "Same squeeze principle as a G-suit" is safe.
