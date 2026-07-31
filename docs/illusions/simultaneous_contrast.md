# Simultaneous Contrast Illusion

Category: **color** — released VI-Probe case **13** (config key: `SimultaneousContrastIllusion`, output folder `13_SimultaneousContrastIllusion`).

## The illusion

Simultaneous contrast is one of the oldest documented color/lightness phenomena, described systematically by Chevreul (1839): a patch of fixed color appears lighter on a dark surround and darker on a light surround. Identical targets embedded in strongly contrasting backgrounds are therefore perceived as having different colors.

## What the generator draws

- Canvas: 512 x 256, black background.
- Two large 256 x 256 background squares side by side, centered at (128, 128) and (384, 128), filling the canvas. Defaults are two grays, (0.5, 0.5, 0.5) and (0.752, 0.752, 0.752); in the published `color` sweep they are supplied as HSB triples (0, 0.43, 0.26) and (0, 0.43, 1.0), i.e. dark vs light red.
- One small square (1/3 of the background size, about 85 x 85 px) centered on each background square. No antialiasing.

Small-square color depends on `strength` and `strength_mode`:

- `lightness` mode (default): convert `DEFAULT_COLOR` to HSB and multiply the brightness by strength (asserts the result stays in [0, 1]).
- `hue` mode: convert to HLS, add 0.3 saturation, rotate hue by (strength - 1) * 360 degrees.

In **original** mode both small squares get the same strength-dependent color. In **perturbed** mode the left small square varies with strength and the right is fixed at the strength = 1.0 color.

## Variants

| Variant | Meaning for this illusion |
|---|---|
| original | Identical small squares (from strength) on contrasting background squares — they look different but are the same. |
| original_control | `draw_backgrounds` set False: same identical small squares on the uniform black canvas — no illusion. |
| perturbed | Left small square from strength, right fixed at strength = 1.0 — genuinely different colors, backgrounds present. |
| perturbed_control | Same unequal small squares without the background squares. |
| with_guide | A 10 px antialiased bar connecting the two small-square centers, drawn in the LEFT small square's color (uniform, no gradient). |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `DEFAULT_COLOR` | (0.65, 0.65, 0.35) | Base RGB color of the small squares (sweep uses (0.5, 0.5, 0.5)). |
| `strength_mode` | `'lightness'` | `'lightness'` scales HSB brightness; `'hue'` rotates hue. |
| `LEFT_BG_COLOR` | (0.5, 0.5, 0.5) | Left background square color (sweep passes HSB (0, 0.43, 0.26)). |
| `RIGHT_BG_COLOR` | (0.752, 0.752, 0.752) | Right background square color (sweep passes HSB (0, 0.43, 1.0)). |

Fixed internals: background squares 256 x 256, small-square ratio 1/3, default strength levels [0.5, 0.75, 1.0, 1.25, 1.5]. The published sweep uses 51 strengths in [0.5, 1.5] excluding 1.0.

## Benchmark question

> Are the two small squares of the same color?

Correct answer: **1 (yes)** for original images, **0 (no)** for perturbed images.

## Notes

- Inline comments labeling the default backgrounds "Pink" and "Dark blue" are stale; the coded defaults are two neutral grays.
- The `define_elements` docstring says "Left rectangle fixed, right varies" for perturbed; the code does the opposite (left varies, right fixed at strength = 1.0).
- The class docstring calls this "Case 1"; the published VI-Probe case number is 14.
