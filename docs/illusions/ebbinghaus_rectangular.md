# Ebbinghaus Illusion (Rectangular Layout)

Category: **size** — released VI-Probe case **6** (`6_EbbinghausIllusionRectangular`).

## The illusion

The Ebbinghaus (Titchener circles) illusion, popularized by Hermann Ebbinghaus and Edward Titchener around the turn of the 20th century, shows that the perceived size of a circle depends on the size of its surrounding context circles: a circle ringed by small circles looks larger than an identical circle ringed by large ones. This variant keeps the classic size-contrast context but arranges the surrounding circles in a rectangular (square) frame rather than the usual ring, testing whether models rely on the memorized canonical layout.

## What the generator draws

On a 512x256 white canvas, two orange central circles (RGB 0.9, 0.5, 0.22) sit at x = width/4 and x = 3*width/4, vertically centered. Each is surrounded by 12 blue-gray circles (RGB 0.57, 0.64, 0.72) placed on the edges of a square around it (3 per side, corners shared):

- Left target: surrounded by small circles (radius = `DEFAULT_CENTER_RADIUS / 2`).
- Right target: surrounded by large circles (radius = `DEFAULT_CENTER_RADIUS * 1.3`).

The square's half-width is `1.3 * (center_radius + surrounding_radius)`. Surrounding circles are drawn first, so the central circles render on top.

Strength (levels 0.4-1.6) scales the central-circle radius: `center_radius = DEFAULT_CENTER_RADIUS * strength`. In **original** mode both central circles get this radius (they stay equal). In **perturbed** mode both start at the default radius, then `apply_perturbation` rescales only the **left** central circle to `DEFAULT_CENTER_RADIUS * strength` (recomputing its surrounding-circle square) while the right circle stays at the default; the two are unequal except at strength 1.0.

## Variants

| Variant | What it means here |
|---|---|
| original | Both central circles equal (strength-scaled); left ringed by small, right by large circles |
| original_control | Same central circles, but `draw_surrounding_circles = False`: only the two orange circles remain |
| perturbed | Left central circle scaled by strength, right fixed at default; context circles kept |
| perturbed_control | Perturbed sizes, no surrounding circles |
| with_guide | Two dashed gray horizontal lines across the full width at the top and bottom edges of the **left** central circle |

## Constructor parameters

| Parameter | Default (code) | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_CENTER_RADIUS` | 25 | 20 | Central-circle radius in pixels at strength 1.0; also sets surrounding radii (small = /2, large = *1.3) |

Fixed internals: 512x256 canvas, white background, strength levels `[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]`.

## Benchmark question

> "Are the two orange circles the same size?"

Correct answer: **1 (yes)** for original images (both central circles equal), **0 (no)** for perturbed images (except the strength = 1.0 case, where sizes coincide).

## Notes

Surrounding radii are derived from the constructor default, not from strength, so in perturbed mode the left context circles keep their size but their square is re-spaced around the resized target.
