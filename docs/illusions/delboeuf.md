# Delboeuf Illusion

Category: **size** — released VI-Probe case **7** (`7_DelboeufIllusion`).

## The illusion

Described by Belgian philosopher Joseph Delboeuf (1865), this illusion shows that a disc surrounded by a closely fitting ring appears larger than an identical disc surrounded by a much larger ring. It is a classic size-contrast/assimilation effect and the basis of well-known applied findings such as the "smaller plate" effect in food-portion research.

## What the generator draws

On a 512x256 white canvas, two solid black inner circles sit at x = width/4 and x = 3*width/4, vertically centered. Each is enclosed by a hollow black outer ring drawn around the same center:

- Left: outer ring radius = 2.0x the left inner radius (`LEFT_OUTER_RADIUS_RATIO = 2.0`).
- Right: outer ring radius = 1.3x the right inner radius (`RIGHT_OUTER_RADIUS_RATIO = 1.3` — the docstrings say "1.5x", the code uses 1.3).

Rings are drawn first, filled inner circles on top.

Strength (levels 0.4-1.6) scales the inner radius: `inner_radius = DEFAULT_INNER_RADIUS * strength`. In **original** mode both inner circles get this radius (equal), and each outer ring scales proportionally. In **perturbed** mode both start at the default radius, then `apply_perturbation` rescales only the **right** inner circle (and its outer ring) to `DEFAULT_INNER_RADIUS * strength`, while the left pair stays at default.

## Variants

| Variant | What it means here |
|---|---|
| original | Both inner circles equal (strength-scaled); left has a large ring (2.0x), right a tight ring (1.3x) |
| original_control | Same inner circles, `draw_outer_rings = False`: only the two solid discs |
| perturbed | Right inner circle and ring scaled by strength; left pair fixed at default |
| perturbed_control | Perturbed sizes, no outer rings |
| with_guide | Two dashed gray horizontal lines across the full width at the top and bottom edges of the **left** inner circle |

## Constructor parameters

| Parameter | Default (code) | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_INNER_RADIUS` | 25 | 30 | Inner-circle radius in pixels at strength 1.0; outer rings are 2.0x (left) and 1.3x (right) of the inner radius |

Fixed internals: 512x256 canvas, white background, black elements, strength levels `[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]`.

## Benchmark question

> "Are the two solid circles the same size?"

Correct answer: **1 (yes)** for original images, **0 (no)** for perturbed images (except strength = 1.0, where both circles are equal).

## Notes

Module and class docstrings state a 1.5x right-ring ratio and describe perturbation direction inconsistently in one place; the implemented behavior is a 1.3x right ring and a strength-varied **right** inner circle.
