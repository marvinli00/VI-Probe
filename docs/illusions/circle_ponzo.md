# Circle Ponzo Illusion

Category: **size** — released VI-Probe case **11** (`11_CirclePonzoIllusion`).

## The illusion

A circle variant of the Ponzo illusion (Ponzo, 1911). Converging lines act as a linear-perspective depth cue, so an object placed closer to the convergence point is interpreted as farther away and is perceptually enlarged. Two physically identical circles between converging lines therefore appear different in size.

## What the generator draws

On a 512x256 white canvas, two black lines (2 px wide) start at (50, 30) and (50, 226) and converge toward a vanishing point at (612, 128), i.e. 100 px beyond the right edge — the lines get closer together toward the right. Two solid black circles sit on the horizontal midline: the left circle at x = width/3 (wide end, appears smaller) and the right circle at x = 2*width/3 (narrow end, appears larger).

Strength scales circle radius: `radius = DEFAULT_CIRCLE_RADIUS * strength`.

- Original mode: both circles share the same strength-scaled radius; physically equal, the right one looks larger.
- Perturbed mode: the left circle is fixed at the default radius while the right circle scales with strength (unequal except at strength 1.0). Note this is the mirror of the irradiation cases, where the left element varies.

## Variants

| Variant | Meaning here |
|---|---|
| original | Equal strength-scaled circles between the converging lines. |
| original_control | `apply_control_modification`: converging lines not drawn — just two equal circles on white, no illusion. |
| perturbed | Right circle strength-scaled, left circle fixed at default; lines kept. Handled in `define_elements`; `apply_perturbation` is a no-op. |
| perturbed_control | Perturbed radii with the converging lines removed. |
| with_guide | `add_visual_guides`: two dashed gray horizontal lines across the full width at the top and bottom edges of the right circle. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_CIRCLE_RADIUS` | 40 | 40 | Circle radius in px at strength 1.0. |

Fixed by the class: 512x256 white canvas, line width 2 px, vanishing point offset 100 px beyond the right edge, circle centers at width/3 and 2*width/3 on the vertical midline. The class defines `strength_levels=[0.4 ... 1.6]`, but the published sweep (`size.yaml`) uses 51 strengths from 0.5 to 1.5 with 1.0 excluded for perturbed.

## Benchmark question

> "Are the two circles the same size?"

The same question is used for control images (`size.yaml` defines no separate control question for this class). Correct answer: `1` (yes) for original images, `0` (no) for perturbed images.
