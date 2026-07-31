# Zollner Illusion (Vertical)

Category: **orientation** — released VI-Probe case **22** (output folder `22_ZollnerIllusionVertical`).

## The illusion

A rotated variant of the Zöllner illusion (Johann Karl Friedrich Zöllner, 1860): long vertical parallel lines crossed by short diagonal hatch marks of alternating orientation appear to lean left and right, although they are perfectly vertical. The effect is attributed to perceptual exaggeration of the acute angles between the lines and the hatches.

## What the generator draws

On a 512x512 white canvas the generator draws `NUM_PARALLEL_LINES` vertical **red** lines (2 px), evenly spaced horizontally (spacing = 512 / (N+1)), spanning y = 50 to y = 462. Each line carries `NUM_HASH_MARKS_PER_LINE` short black hash marks (1 px, 20 px long, angle measured relative to the horizontal axis) evenly distributed along it and centered on the line. Hash-mark angle alternates sign between successive columns.

Effect of `strength`:

- **Original mode**: lines stay vertical and parallel; strength scales the hash-mark angle, `angle = 45 * strength` degrees.
- **Perturbed mode**: hash-mark angle fixed at 45 degrees; the red lines are genuinely tilted by `3 * (strength - 1.0)` degrees, alternating sign per column (even columns: top shifts left, bottom shifts right; odd columns the reverse). strength = 1.0 keeps them vertical.

## Variants

| Variant | Meaning here |
|---|---|
| original | Vertical parallel red lines with alternating diagonal hash marks (illusion present) |
| original_control | Hash marks removed (`draw_hash_marks = False`); plain vertical red lines |
| perturbed | Hash marks at fixed 45 deg + red lines actually tilted in alternating directions |
| perturbed_control | Tilted red lines with hash marks removed |
| with_guide | Two dashed gray vertical lines (1 px) over the full height at the x of the first and last red lines |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `NUM_PARALLEL_LINES` | 6 | Number of vertical red test lines (also sets horizontal spacing) |
| `NUM_HASH_MARKS_PER_LINE` | 10 | Number of diagonal hash marks per line |

In the published sweep (`orientation.yaml`, `param_mode: table`), `NUM_HASH_MARKS_PER_LINE` is fixed at 10 and `NUM_PARALLEL_LINES` is set per scale factor from 5 (at 0.50) to 25 (at 1.50) in steps of 1. `is_guide_first_by_class` is `true` for this class.

## Benchmark question

> Are the those red lines straight?

(The wording, including the typo "the those", is frozen as published.)

Correct answer: **1 (yes)** for original images (lines are truly vertical/parallel), **0 (no)** for perturbed images (lines are actually tilted).

## Notes

- Internal strength levels `[0.4 ... 1.6]` set in `__init__` are overridden by the sweep config (0.5–1.5, 11 steps, 1.0 excluded for perturbed).
- The class registers itself under the internal name `zollner_illusion_v` (not `zollner_illusion_vertical`).
- Perturbed tilt shifts the two endpoints horizontally by ±(length·tan(tilt)/2), keeping the midpoint fixed.
