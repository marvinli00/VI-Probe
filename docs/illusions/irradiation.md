# Irradiation Illusion

Category: **size** — released VI-Probe case **9** (`9_IrradiationIllusion`).

## The illusion

Bright shapes on a dark background appear larger than identical dark shapes on a bright background. The effect, discussed by Helmholtz (1867) and known since Galileo's observations of planets, is attributed to light spreading ("irradiation") in the retinal response: the bright figure's borders bleed outward, inflating its perceived size.

## What the generator draws

A 512x256 canvas split into two half-canvas panels: the left half is filled with a black background, the right half with a white background. A white square (`rect_left`) is centered on the black left panel at (128, 128); a black square (`rect_right`) is centered on the white right panel at (384, 128). Squares are drawn without antialiasing.

Strength scales the square size: `side = DEFAULT_RECT_WIDTH/HEIGHT * strength`.

- Original mode: both squares get the same strength-scaled size; physically equal, but the white one looks larger.
- Perturbed mode: the left (white) square scales with strength while the right (black) square stays fixed at the default size, so the two squares are physically unequal (except at strength 1.0).

## Variants

| Variant | Meaning here |
|---|---|
| original | Both squares equal, strength-scaled; white-on-black vs black-on-white. |
| original_control | `apply_control_modification`: background panels not drawn (plain white canvas) and the left square is recolored black — two identical black squares, no illusion. |
| perturbed | Left square strength-scaled, right square fixed at default; backgrounds kept. Perturbation itself is handled in `define_elements`; `apply_perturbation` is a no-op. |
| perturbed_control | Perturbed sizes with backgrounds removed and both squares black. |
| with_guide | `add_visual_guides`: two dashed red horizontal lines across the full width at the top and bottom edges of the left square. |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_RECT_WIDTH` | 128 | 100 | Square width in px at strength 1.0. |
| `DEFAULT_RECT_HEIGHT` | 128 | 100 | Square height in px at strength 1.0. |

Fixed by the class: 512x256 canvas, white background, square centers at width/4 and 3*width/4. The class defines `strength_levels=[0.4 ... 1.6]`, but the published sweep (`size.yaml`) uses 51 strengths from 0.5 to 1.5 with 1.0 excluded for perturbed.

## Benchmark question

Non-control images:

> "Are the left white square and the right black square equal in size?"

Control images (both squares are black):

> "Are the left black square and the right black square equal in size?"

Correct answer: `1` (yes) for original images (squares are equal), `0` (no) for perturbed images (left differs from right).
