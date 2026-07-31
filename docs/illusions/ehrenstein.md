# Ehrenstein Illusion

Category: **orientation** — released VI-Probe case **27** (`27_EhrensteinIllusion`).

## The illusion

In the Ehrenstein square illusion (Walter Ehrenstein, 1921), a square superimposed on a bundle of radial lines appears distorted: its perfectly straight sides seem to bow, because the intersecting radial lines bias the perceived orientation of the edges. It belongs to the same family of orientation-contrast distortions as the Hering and Wundt illusions.

## What the generator draws

On a 512x512 white canvas, the generator draws:

- A fan of `num_lines` thin gray lines (color 0.6, width 2 px, length 180 px) radiating from the image center, evenly spaced over 360 degrees.
- Two hollow black squares (80 px side, 3 px border), centered 80 px to the left and 80 px to the right of the image center, so both squares sit on top of the radial bundle.

Strength behavior:

- **Original mode**: the squares' edges are perfectly straight and strength has no effect inside the class (`num_lines` is fixed to the constructor's `NUM_LINES`; curvature is 0). The published sweep instead varies illusion magnitude by passing a different `NUM_LINES` per strength via the config table (10 lines at strength 0.50 up to 30 at 1.50).
- **Perturbed mode**: line count is fixed at `NUM_LINES`, and the square edges are drawn as parabolic curves with depth `(strength - 1.0) * 30` px — concave (bowed toward the square center) for strength < 1.0, straight at 1.0 (excluded from the sweep), convex for strength > 1.0.

## Variants

| Variant | What it means here |
|---|---|
| original | Radial lines plus two straight-edged squares; the edges only appear curved. |
| original_control | `apply_control_modification` disables radial-line drawing, leaving only the two straight squares (no illusion). |
| perturbed | Radial lines kept; both squares' edges rendered as genuinely curved parabolas, depth `(strength-1)*30` px. |
| perturbed_control | Radial lines removed but the curved edges remain, so the real curvature is plainly visible. |
| with_guide | A 90%-opaque white rectangle (square size + 60 px padding) is blended over each square to mask the radial lines locally, then the squares are redrawn on top — making the true edge shape easy to judge. |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `NUM_LINES` | 24 | Number of radial lines. In the published run this is set per strength from the sweep table (10-30). |

Fixed internals: canvas 512x512, line length 180 px, gray line color (0.6), squares 80 px at x-offsets -80/+80, black 3 px borders. Declared strength levels: [0.5, 0.8, 1.0, 1.2, 1.5]; the published sweep uses 0.5-1.5 in steps of 0.1 with 1.0 excluded.

## Benchmark question

> "Do the squares on the left and right have straight edges?"

Correct answer: **1 (yes)** for original images (edges are geometrically straight despite appearing bowed); **0 (no)** for perturbed images (edges are actually curved).

## Notes

- The class docstring saying strength controls "radial line length" (and an inline comment about line count 12-36) is stale; in this code the original-mode strength is inert and illusion magnitude is swept externally through `NUM_LINES`.
- `generate_illusion`'s docstring mentions drawing a circle; no circle is drawn — only the two squares and the radial lines.
