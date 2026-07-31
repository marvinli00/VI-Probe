# Ebbinghaus Illusion

Category: **size** — released VI-Probe case **5** (output folder `5_EbbinghausIllusion`).

## The illusion

The Ebbinghaus illusion (also known as Titchener circles, popularized by Titchener, 1901, after Hermann Ebbinghaus) is a classic relative-size illusion: a central circle surrounded by small circles appears larger than an identical circle surrounded by large circles. It is a standard probe of context-dependent size perception and has been used to dissociate perception from action (Aglioti et al., 1995).

## What the generator draws

On a 512x256 white canvas:

- **Left group** at (128, 128): an orange central circle (RGB 0.9, 0.5, 0.22) surrounded by a ring of 8 small blue-gray circles (RGB 0.57, 0.64, 0.72), each with radius `DEFAULT_CENTER_RADIUS / 2`.
- **Right group** at (384, 128): an identical orange central circle surrounded by a ring of 6 large blue-gray circles, each with radius `DEFAULT_CENTER_RADIUS * 1.3`.

Surrounding circles are placed at distance `1.3 * (center_radius + surrounding_radius)` from the group center, evenly spaced by angle, and drawn first so the central circles sit on top. Surrounding radii are fixed; only the central radius scales as `DEFAULT_CENTER_RADIUS * strength`.

- **Original mode**: both central circles get the same strength-scaled radius, so they are always physically equal; strength shrinks or grows the equal pair (and pushes the surrounding rings in or out, since the ring distance depends on the central radius).
- **Perturbed mode**: the right central circle stays at `DEFAULT_CENTER_RADIUS` while the left central circle is rescaled to `DEFAULT_CENTER_RADIUS * strength` (the left ring positions are recalculated accordingly), so the two orange circles are physically unequal (except at strength = 1.0).

## Variants

| Variant | Meaning for this illusion |
|---|---|
| original | Both orange circles equal (strength-scaled), with small-circle ring on the left and large-circle ring on the right. |
| original_control | `apply_control_modification` sets `draw_surrounding_circles = False`: only the two equal orange circles on white, no context. |
| perturbed | Left orange circle scaled by strength, right fixed at default; both rings drawn. |
| perturbed_control | Same unequal orange circles without any surrounding circles. |
| with_guide | Two gray dashed horizontal lines (1 px) across the full width at the top and bottom edges of the left central circle, so its diameter can be compared against the right circle. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_CENTER_RADIUS` | 25 | 20 | Central circle radius in pixels at strength = 1.0. Also sets the small surrounding radius (half of it) and the large surrounding radius (1.3x it). |

Fixed internals: canvas 512x256, 8 small / 6 large surrounding circles, spacing factor 1.3, colors as listed above.

## Benchmark question

From `configs/sweeps/size.yaml` (`EbbinghausIllusion`):

> "Are the two orange circles the same size?"

Correct answer: **1 (yes)** for original images (central circles are equal), **0 (no)** for perturbed images (left circle differs from right).
