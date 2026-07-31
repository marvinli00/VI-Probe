# Ponzo Trapezoid Illusion

Category: **size** — released VI-Probe case **4** (output folder `4_PonzoTrapezoidIllusion`).

## The illusion

The Ponzo illusion (Mario Ponzo, 1911) shows that context suggesting linear perspective distorts perceived length: two identical horizontal lines drawn over converging contours appear unequal, because the line nearer the "vanishing point" is interpreted as farther away and therefore larger. This variant replaces the classic pair of converging lines with a filled trapezoid, whose narrowing shape provides the same depth cue.

## What the generator draws

On a 512x256 white canvas:

- A filled gray trapezoid (RGB 0.7, 0.7, 0.7), horizontally centered, spanning from y = 10 down to y = height - 10, with a 40 px wide top edge and a 150 px wide bottom edge. Its geometry is fixed and never changes with strength. It is filled scanline-by-scanline with linearly interpolated width.
- Two black horizontal lines (2 px thick), horizontally centered on the canvas: the top line at 1/4 of the height (y = 64) and the bottom line at 3/4 of the height (y = 192), drawn on top of the trapezoid.

Line length is `DEFAULT_LINE_LENGTH * strength`, rounded to an integer.

- **Original mode**: both lines get the same strength-scaled length, so they are always physically equal; strength just makes the equal pair shorter or longer relative to the trapezoid.
- **Perturbed mode**: the bottom line stays at `DEFAULT_LINE_LENGTH` (strength 1.0) while the top line is rescaled to `DEFAULT_LINE_LENGTH * strength`, so the two lines are physically unequal (except at strength = 1.0).

## Variants

| Variant | Meaning for this illusion |
|---|---|
| original | Trapezoid + two equal-length lines (both scaled by strength). |
| original_control | `apply_control_modification` sets `draw_trapezoid = False`: only the two equal lines on white, no perspective cue. |
| perturbed | Trapezoid + unequal lines: bottom fixed at default length, top scaled by strength. |
| perturbed_control | Same unequal lines without the trapezoid. |
| with_guide | Two red dashed vertical lines (1 px) spanning the full canvas height at the top line's endpoints, for comparing the two lines' extents. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_LINE_LENGTH` | 80 | 80 | Horizontal line length in pixels at strength = 1.0. |

Fixed internals: canvas 512x256, strength levels declared as `[0.4 ... 1.6]` in the class (the sweep config overrides with 51 values in [0.5, 1.5], excluding 1.0 for perturbed), trapezoid geometry and colors as listed above.

## Benchmark question

From `configs/sweeps/size.yaml` (`PonzoTrapezoidIllusion`):

> "Are the two horizontal black lines of equal length?"

Correct answer: **1 (yes)** for original images (lines are equal), **0 (no)** for perturbed images (top line differs from bottom line).
