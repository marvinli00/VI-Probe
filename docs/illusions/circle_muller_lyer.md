# Circle Müller-Lyer Illusion

Category: **size** — released VI-Probe case **2** (output folder `2_CircleMullerLyerIllusion`).

## The illusion

A variant of the classic Müller-Lyer illusion (Müller-Lyer, 1889) in which the arrow
fins are replaced by circles at the line endpoints. The position of the circles
relative to the endpoints (inside vs. outside the line) biases perceived line length
in the same way fins do, showing the effect does not depend on the specific arrow
shape.

## What the generator draws

A 512 x 256 white canvas with two horizontal black lines (2 px wide), horizontally
centered:

- **Top line** at y = height/4, with hollow circles positioned **inward** (inside the
  endpoints).
- **Bottom line** at y = 3·height/4, with hollow circles positioned **outward**
  (outside the endpoints).

Circles are hollow with a fixed 20 px radius, independent of strength. No arrows are
drawn (`arrow_length=0`).

Line length is `DEFAULT_LINE_LENGTH * strength` (strength 1.0 gives the default; the
docstring's [-1, 1] interpolation description is stale).

- **Original mode:** both lines get the same strength-scaled length — always
  physically equal.
- **Perturbed mode:** the top line stays at `DEFAULT_LINE_LENGTH`, while the bottom
  line is set to the strength-scaled length in `apply_perturbation`. For any
  strength != 1.0 the two lines are physically unequal.

## Variants

| Variant | Meaning here |
|---|---|
| `original` | Both lines equal length (strength-scaled), endpoint circles present — illusion active. |
| `original_control` | Same equal-length lines, but `circle_radius` set to 0 (no circles, no illusion). |
| `perturbed` | Top line at default length, bottom line strength-scaled — physically unequal, circles present. |
| `perturbed_control` | Same unequal lines without circles. |
| `with_guide` | Adds red dashed vertical lines spanning the full image height at the **top line's** endpoints, for length comparison. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_LINE_LENGTH` | 300 | 200 | Line length in pixels at strength 1.0; the fixed length of the top line in perturbed mode. |

Fixed internals: canvas 512 x 256, white background, circle radius 20 px, hollow
circles, built-in `strength_levels = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]` (the
published sweep overrides this with 51 strengths in [0.5, 1.5], excluding 1.0).

## Benchmark question

> Are the two black lines of equal length?

- **Original** (and original_control): lines are equal — correct answer **1** (yes).
- **Perturbed** (and perturbed_control): lines differ — correct answer **0** (no).

## Notes

- The module docstring claims the inward-circle line "appears shorter"; the drawn
  layout is top = inward circles, bottom = outward circles.
- `_calculate_line_length`'s docstring describes a [-1, 1] interpolation that the
  code no longer uses; length is simply `DEFAULT_LINE_LENGTH * strength`.
