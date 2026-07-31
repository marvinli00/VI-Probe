# Twisted Cord Illusion

Category: **orientation** — released VI-Probe case **23** (`23_TwistedCordIllusion`).

## The illusion

The twisted cord (or "twisted rope") illusion, described by James Fraser (1908) in the same family as the Fraser spiral, arises when a straight contour is filled or bordered with oblique black-and-white segments. The local diagonal orientation of the stripes is partially integrated into the perceived global orientation of the contour, so a perfectly straight, vertical cord appears tilted or twisted.

## What the generator draws

On a 512x512 light-gray background (0.9, 0.9, 0.9), the generator draws `NUM_CORDS` (default 2) vertical rectangular poles, each `CORD_WIDTH` px wide and 90% of the canvas tall, evenly spaced and horizontally centered. Each pole is filled with an alternating black/white diagonal stripe pattern at a fixed 45 degrees; the second pole uses a horizontally flipped copy of the pattern, so the two poles carry mirror-image stripes. A 10 px black horizontal ground line spans the full width at the bottom of the poles.

- **Original mode**: poles are exactly vertical; `strength` is a stripe-width multiplier (`stripe_width = STRIPE_WIDTH * strength`, e.g. 1.0 -> 10 px, 2.0 -> 20 px). The 45-degree stripes make the vertical poles look tilted.
- **Perturbed mode**: stripe width is fixed at `STRIPE_WIDTH`; the poles are actually rotated by `-(strength - 1.0) * 10` degrees, with the second pole rotated in the opposite direction (symmetric tilt). Strengths run 0.5-1.5 (1.0 excluded), giving real tilts up to +/-5 degrees.

## Variants

| Variant | What it means here |
|---|---|
| original | Vertical poles, 45-degree diagonal stripes; strength scales stripe width. |
| original_control | Stripe pattern replaced by an all-zeros array, so poles render as solid black rectangles (no stripes); poles remain vertical. |
| perturbed | Poles physically tilted by `-(strength-1)*10` degrees in opposite directions, stripes still 45 degrees. |
| perturbed_control | Same solid-black replacement of the stripe pattern; pole rotation is NOT reset (the reset line is commented out), so the tilt from the perturbation remains visible. |
| with_guide | 3 px red vertical lines drawn just outside the left and right edges of each pole, showing the edges are straight and parallel. |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `NUM_CORDS` | 2 | Number of poles. |
| `CORD_WIDTH` | 30 | Pole width in px. Swept per scale factor in the published run (15-35 px for scale 0.50-1.50). |
| `STRIPE_WIDTH` | 10 | Base stripe width in px (config sets 10). |
| `SR_FACTOR` | 4 | Super-resolution factor for anti-aliased rendering. |

Canvas size is fixed at 512x512; strength levels default to [0.5, 0.8, 1.0, 1.2, 1.5, 2.0], but the published sweep uses 0.5-1.5 in steps of 0.1 with 1.0 excluded.

## Benchmark question

> "Are those vertical columns parallel?"

Correct answer: **1 (yes)** for original images (poles are truly vertical and parallel despite the twisted appearance); **0 (no)** for perturbed images (poles are physically tilted in opposite directions).

## Notes

- `apply_control_modification` first regenerates a vertical (0 degree) stripe pattern, then immediately overwrites it with `np.zeros_like(...)`; the published control images therefore show solid black poles, not vertically striped ones, despite the docstring.
- The class docstring describing strength as "stripe angle in degrees" is stale; the actual semantics are stripe-width multiplier (original) and pole rotation (perturbed), as described above.
- The `control_mode` branch in `_draw_twisted_cord` (solid white pole) is never triggered by the pipeline; control goes through the stripe-pattern replacement instead.
