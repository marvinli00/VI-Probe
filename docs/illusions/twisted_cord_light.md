# Twisted Cord Illusion (Light)

Category: **orientation** — released VI-Probe case **24** (`24_TwistedCordIllusionLight`). Low-contrast gray variant of case 23.

## The illusion

Same perceptual effect as the classic twisted cord illusion (Fraser, 1908): oblique stripe segments inside a straight vertical pole bias its perceived global orientation, making it look tilted or twisted. This variant tests whether the effect (and model behavior) survives when the stripe contrast is reduced from black/white to two mid grays on a gray background.

## What the generator draws

On a 512x512 medium-gray background (0.5, 0.5, 0.5), the generator draws `NUM_CORDS` (default 2) vertical poles, each `CORD_WIDTH` px wide (default 60 here, vs 30 in the dark version) and 90% of the canvas tall, evenly spaced. Each pole is filled with alternating dark-gray (0.3) and light-gray (0.7) stripes at a fixed 45 degrees; the second pole gets a horizontally flipped (mirror) pattern. A 10 px dark-gray (0.3) ground line spans the bottom of the poles.

- **Original mode**: poles vertical; `strength` multiplies the stripe width (`STRIPE_WIDTH * strength`, e.g. 1.0 -> 10 px).
- **Perturbed mode**: stripe width fixed at `STRIPE_WIDTH`; poles are physically rotated by `-(strength - 1.0) * 10` degrees, the second pole in the opposite direction. With the published strengths 0.5-1.5 (1.0 excluded), real tilts reach +/-5 degrees.

## Variants

| Variant | What it means here |
|---|---|
| original | Vertical poles with 45-degree gray stripes; strength scales stripe width. |
| original_control | Stripe pattern overwritten with an all-zeros array, so poles render as solid black rectangles on the gray background; poles stay vertical. |
| perturbed | Poles tilted by `-(strength-1)*10` degrees in opposite directions; stripes unchanged. |
| perturbed_control | Same solid-black pattern replacement; pole rotation is not reset (line commented out), so the physical tilt remains. |
| with_guide | 3 px red vertical lines along the outer left and right edges of each pole, demonstrating the edges are straight and parallel. |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `NUM_CORDS` | 2 | Number of poles. |
| `CORD_WIDTH` | 60 | Pole width in px. The published sweep overrides this per scale factor (15-35 px for scale 0.50-1.50). |
| `STRIPE_WIDTH` | 10 | Base stripe width in px (config sets 10). |
| `SR_FACTOR` | 4 | Super-resolution factor for anti-aliased rendering. |

Canvas is fixed at 512x512; declared strength levels are [0.5, 0.8, 1.0, 1.2, 1.5, 2.0], but the published sweep uses 0.5-1.5 in steps of 0.1 with 1.0 excluded.

## Benchmark question

> "Are those vertical columns parallel?"

Correct answer: **1 (yes)** for original images (the poles are genuinely vertical and parallel); **0 (no)** for perturbed images (the poles are physically tilted in opposite directions).

## Notes

- As in case 25, `apply_control_modification` builds a vertical gray stripe pattern and then replaces it with zeros, so control poles are solid black — not low-contrast striped — in the published data.
- The `control_mode` branch in `_draw_twisted_cord` (solid 0.7 gray pole) is dead code; controls go through the pattern replacement above.
