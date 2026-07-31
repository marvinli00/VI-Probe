# Zollner Illusion

Category: **orientation** — released VI-Probe case **21** (output folder `21_ZollnerIllusion`).

## The illusion

In the Zöllner illusion (Johann Karl Friedrich Zöllner, 1860), long parallel lines crossed by short diagonal hatch marks appear to converge or diverge. Neighboring lines carry hatch marks of opposite orientation, and the acute angles between line and hatches are perceptually exaggerated, making truly parallel lines look tilted in alternating directions.

## What the generator draws

On a 512x512 white canvas the generator draws `NUM_PARALLEL_LINES` horizontal **red** lines (2 px), evenly spaced vertically (spacing = 512 / (N+1)), spanning x = 50 to x = 462. Each line carries `NUM_HASH_MARKS_PER_LINE` short black hash marks (1 px, 20 px long) evenly distributed along it and centered on the line. Hash-mark angle alternates sign between successive lines (even rows +angle, odd rows −angle).

Effect of `strength`:

- **Original mode**: lines stay horizontal and parallel; strength scales the hash-mark angle, `angle = 45 * strength` degrees.
- **Perturbed mode**: hash-mark angle fixed at 45 degrees; the red lines are genuinely tilted by `3 * (strength - 1.0)` degrees, alternating sign per row (even rows +tilt, odd rows −tilt). strength = 1.0 keeps them parallel.

## Variants

| Variant | Meaning here |
|---|---|
| original | Parallel red lines with alternating diagonal hash marks (illusion present) |
| original_control | Hash marks removed (`draw_hash_marks = False`); plain parallel red lines |
| perturbed | Hash marks at fixed 45 deg + red lines actually tilted in alternating directions |
| perturbed_control | Tilted red lines with hash marks removed |
| with_guide | Two dashed gray horizontal lines (1 px) across the full width at the y of the first and last red lines |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `NUM_PARALLEL_LINES` | 6 | Number of horizontal red test lines (also sets vertical spacing) |
| `NUM_HASH_MARKS_PER_LINE` | 10 | Number of diagonal hash marks per line |

In the published sweep (`orientation.yaml`, `param_mode: table`), `NUM_HASH_MARKS_PER_LINE` is fixed at 10 and `NUM_PARALLEL_LINES` is set per scale factor from 5 (at 0.50) to 25 (at 1.50) in steps of 1. `is_guide_first_by_class` is `true` for this class.

## Benchmark question

> Are the those red lines straight?

(The wording, including the typo "the those", is frozen as published.)

Correct answer: **1 (yes)** for original images (lines are parallel/horizontal), **0 (no)** for perturbed images (lines are actually tilted).

## Notes

- Internal strength levels `[0.4 ... 1.6]` set in `__init__` are overridden by the sweep config (0.5–1.5, 11 steps, 1.0 excluded for perturbed).
- Perturbed tilt keeps each line's midpoint fixed: endpoints move by ±(length·tan(tilt)/2) in opposite vertical directions.
