# Ponzo Illusion

Category: **size** — released VI-Probe case **3** (output folder `3_PonzoIllusion`).

## The illusion

In the Ponzo illusion (Mario Ponzo, 1911) two identical horizontal lines are placed
between a pair of converging lines resembling railway tracks receding in depth. The
line nearer the convergence point is interpreted as farther away and therefore
appears longer, a classic demonstration of size-constancy scaling driven by linear
perspective cues.

## What the generator draws

A 512 x 256 white canvas containing:

- **Two converging black lines** (2 px), symmetric about the horizontal center:
  150 px apart at the bottom (y = height-10) narrowing to 40 px apart at the top
  (y = 10). These are fixed and never change with strength.
- **Top horizontal black line** at y = height/4 (inside the narrow region, "farther").
- **Bottom horizontal black line** at y = 3·height/4 (inside the wide region,
  "closer"). Both are 2 px thick and centered.

Horizontal line length is `DEFAULT_LINE_LENGTH * strength` (strength 1.0 gives the
default; the docstring's [-1, 1] interpolation description is stale).

- **Original mode:** both horizontal lines get the same strength-scaled length —
  always physically equal.
- **Perturbed mode:** the bottom line stays at `DEFAULT_LINE_LENGTH`, while the top
  line is set to the strength-scaled length in `apply_perturbation`. For any
  strength != 1.0 the two lines are physically unequal.

## Variants

| Variant | Meaning here |
|---|---|
| `original` | Equal-length horizontal lines with converging lines drawn — illusion active. |
| `original_control` | Same equal-length lines, but `draw_converging_lines` set to False (no perspective context). |
| `perturbed` | Bottom line at default length, top line strength-scaled — physically unequal, converging lines drawn. |
| `perturbed_control` | Same unequal lines without the converging lines. |
| `with_guide` | Adds red dashed vertical lines spanning the full image height at the **top line's** endpoints, for length comparison. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_LINE_LENGTH` | 80 | 80 | Horizontal line length in pixels at strength 1.0; the fixed length of the bottom line in perturbed mode. |

Fixed internals: canvas 512 x 256, white background, converging-line bottom/top
widths 150/40 px, all line thickness 2 px, internal name `ponzo_classical`, built-in
`strength_levels = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]` (the published sweep
overrides this with 51 strengths in [0.5, 1.5], excluding 1.0).

## Benchmark question

> Are the two horizontal black lines of equal length?

- **Original** (and original_control): lines are equal — correct answer **1** (yes).
- **Perturbed** (and perturbed_control): lines differ — correct answer **0** (no).

## Notes

- Unlike the Müller-Lyer generators, the **top** line is the one perturbed here (the
  bottom line is the fixed reference); the guide bars therefore track the varied line
  in perturbed mode.
- `_calculate_line_length`'s docstring describes a [-1, 1] interpolation that the
  code no longer uses; length is simply `DEFAULT_LINE_LENGTH * strength`.
