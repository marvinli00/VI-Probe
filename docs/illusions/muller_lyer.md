# Müller-Lyer Illusion

Category: **size** — released VI-Probe case **1** (output folder `1_MullerLyerIllusion`).

## The illusion

The Müller-Lyer illusion shows that arrow-like fins at the ends of a line change its
perceived length: a line with outward-pointing fins (`>──<`) appears longer than an
identical line with inward-pointing fins (`──><──`). First published by Franz Carl
Müller-Lyer (1889, *Optische Urteilstäuschungen*), it is one of the most studied
geometric illusions; a common explanation is misapplied size-constancy scaling
(Gregory, 1963).

## What the generator draws

A 512 x 256 white canvas with two horizontal black lines (2 px wide), horizontally
centered:

- **Top line** at y = height/4, with **outward**-pointing arrow fins at both ends.
- **Bottom line** at y = 3·height/4, with **inward**-pointing arrow fins at both ends.

Arrow fins are fixed at 20 px length and 30 degrees, independent of strength.

Line length is `DEFAULT_LINE_LENGTH * strength` (so strength 1.0 gives the default
length; the docstring's [-1, 1] interpolation description is stale).

- **Original mode:** both lines get the same strength-scaled length — they are always
  physically equal; only the overall size varies with strength.
- **Perturbed mode:** the top line stays at `DEFAULT_LINE_LENGTH`, while the bottom
  line is set to the strength-scaled length in `apply_perturbation`. For any
  strength != 1.0 the two lines are physically unequal.

## Variants

| Variant | Meaning here |
|---|---|
| `original` | Both lines equal length (strength-scaled), fins present — illusion active. |
| `original_control` | Same equal-length lines, but `arrow_length` set to 0 (no fins, no illusion). |
| `perturbed` | Top line at default length, bottom line strength-scaled — physically unequal, fins present. |
| `perturbed_control` | Same unequal lines without fins. |
| `with_guide` | Adds red dashed vertical lines spanning the full image height at the **top line's** endpoints, for length comparison. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_LINE_LENGTH` | 300 | 200 | Line length in pixels at strength 1.0; the fixed length of the top line in perturbed mode. |

Fixed internals: canvas 512 x 256, white background, arrow length 20 px, arrow angle
30 degrees, built-in `strength_levels = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]`
(the published sweep overrides this with 51 strengths in [0.5, 1.5], excluding 1.0).

## Benchmark question

> Are the two black lines of equal length?

- **Original** (and original_control): lines are equal — correct answer **1** (yes).
- **Perturbed** (and perturbed_control): lines differ — correct answer **0** (no).

## Notes

- Several internal comments are stale: `_calculate_line_length` documents a [-1, 1]
  interpolation that is no longer used, `apply_perturbation`'s comments say
  "Fix Line 1" while the code modifies `line_bottom`, and the guide-bar color comment
  says "Gray" though the color is red `(1, 0, 0)`.
