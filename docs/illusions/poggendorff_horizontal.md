# Poggendorff Horizontal Illusion

Category: **orientation** — released VI-Probe case **26** (`26_PoggendorffHorizontalIllusion`).

## The illusion

This is a rotated variant of the classic Poggendorff illusion (Poggendorff, 1860): a diagonal line interrupted by an occluder appears misaligned across it even though its segments are collinear. Here the occluder is a horizontal bar rather than the traditional vertical one, so the apparent misalignment is judged left-right instead of up-down.

## What the generator draws

On a 512x512 white canvas:

- A diagonal line running from lower-left to upper-right through the image center, drawn as two segments split at the occluder: the **bottom segment is red**, the **top segment is black** (both 3 px wide). The red segment's endpoint is retracted 3 px along the diagonal so the colors do not touch.
- A solid **black horizontal occluder rectangle** (300 px wide, 60 px tall) centered on the canvas, drawn on top of the line so it hides the middle of the diagonal.
- The constructor's `horizontal_offset` shifts the whole diagonal left or right, moving where it crosses the occluder.

Strength (levels 0.4-1.6):

- **Original mode**: strength sets the diagonal's angle via `angle = 20 + strength * 25` degrees (0.4 -> 30°, 1.0 -> 45°, 1.6 -> 60°). The segments remain truly collinear.
- **Perturbed mode**: the angle is fixed at 30° (`DEFAULT_ANGLE`) and strength instead controls a real horizontal misalignment of the black (top) segment: `offset = (strength - 1.0) * 80` px (0.5 -> 40 px left, 1.5 -> 40 px right).

A blue "confusion line" is computed in `define_elements` but never drawn by `generate_illusion`.

## Variants

| Variant | Meaning here |
|---|---|
| original | Occluder drawn; red and black segments truly collinear; strength sets the diagonal angle. |
| original_control | Same scene with the occluder removed (`draw_occluder = False`), so continuity is directly visible. |
| perturbed | Occluder drawn, angle fixed at 30°; black top segment shifted horizontally by `(strength - 1.0) * 80` px, genuinely breaking collinearity. |
| perturbed_control | Perturbed geometry with the occluder removed, so the real offset is directly visible. |
| with_guide | A thin (1 px) dashed red line along the true diagonal, extended 100 px beyond each end and drawn in two pieces split at the occluder's bottom edge. |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `horizontal_offset` | `0` | Horizontal shift (px) of the whole diagonal line; positive moves it right. |

The published sweep (`orientation.yaml`, `param_mode: table`) varies `horizontal_offset` from -50 to +50 px across scale factors 0.50-1.50 (0 at scale 1.00).

## Benchmark question

> "Are the red and black solid diagonal lines aligned?"

Correct answer: **1 (yes)** for original images (the segments are collinear despite appearing offset), **0 (no)** for perturbed images (the black segment is genuinely displaced).

## Notes

- Internal comments are partly stale: the module docstring claims a fixed 15 px perturbation offset, and `apply_perturbation`'s comments describe `* 100` while the code uses `(strength - 1.0) * 80`. `PERTURB_OFFSET`, `OCCLUDER_LINE_WIDTH`, `GUIDE_COLOR`, and the confusion-line settings are unused.
