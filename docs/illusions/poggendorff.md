# Poggendorff Illusion

Category: **orientation** — released VI-Probe case **25** (`25_PoggendorffIllusion`).

## The illusion

The Poggendorff illusion, first described by Johann Poggendorff in 1860, demonstrates a misperception of collinearity: when a diagonal line is interrupted by an occluding surface, its two visible segments appear laterally misaligned even though they are perfectly collinear. It remains a benchmark stimulus for studying how the visual system extrapolates contours across occlusion.

## What the generator draws

On a 512x512 white canvas:

- A diagonal line running from lower-left to upper-right through the image center, drawn as two segments split at the right edge of the occluder: the **left segment is red**, the **right segment is black** (both 3 px wide). The red segment's endpoint is retracted 5 px along the diagonal so the colors do not touch.
- A solid **black vertical occluder rectangle** (60 px wide, 300 px tall) centered on the canvas, drawn on top of the line so it hides the middle of the diagonal.
- The constructor's `vertical_offset` shifts the whole diagonal up or down, moving where it crosses the occluder.

Strength (levels 0.4-1.6):

- **Original mode**: strength sets the diagonal's angle via `angle = 20 + strength * 25` degrees (0.4 -> 30°, 1.0 -> 45°, 1.6 -> 60°). The segments remain truly collinear.
- **Perturbed mode**: the angle is fixed at 45° and strength instead controls a real vertical misalignment of the black (right) segment: `offset = (strength - 1.0) * 80` px (0.5 -> 40 px up, 1.5 -> 40 px down).

A blue "confusion line" is computed in `define_elements` but never drawn by `generate_illusion`.

## Variants

| Variant | Meaning here |
|---|---|
| original | Occluder drawn; red and black segments truly collinear; strength sets the diagonal angle. |
| original_control | Same scene with the occluder removed (`draw_occluder = False`), so continuity is directly visible. |
| perturbed | Occluder drawn, angle fixed at 45°; black right segment shifted vertically by `(strength - 1.0) * 80` px, genuinely breaking collinearity. |
| perturbed_control | Perturbed geometry with the occluder removed, so the real offset is directly visible. |
| with_guide | A thin (1 px) dashed red line along the true diagonal, extended 100 px beyond each end and drawn in two pieces split at the occluder's right edge. |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vertical_offset` | `0` | Vertical shift (px) of the whole diagonal line; positive moves it down. |

The published sweep (`orientation.yaml`, `param_mode: table`) varies `vertical_offset` from -50 to +50 px across scale factors 0.50-1.50 (0 at scale 1.00).

## Benchmark question

> "Are the red and black solid diagonal lines aligned?"

Correct answer: **1 (yes)** for original images (the segments are collinear despite appearing offset), **0 (no)** for perturbed images (the black segment is genuinely displaced).

## Notes

- Several internal comments/docstrings are stale: the module docstring claims a default angle of 30° and a fixed 15 px perturbation offset, but the code uses `DEFAULT_ANGLE = 45` and a strength-dependent offset of `(strength - 1.0) * 80` px. `PERTURB_OFFSET`, `OCCLUDER_LINE_WIDTH`, `GUIDE_COLOR`, and the confusion-line settings are unused.
