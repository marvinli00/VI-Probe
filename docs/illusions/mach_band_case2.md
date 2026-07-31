# Mach Band Illusion Case 2

Category: **color** — released VI-Probe case **16** (`16_MachBandIllusion_Case2`, legacy class key `MachBandIllusion_Case2`).

## The illusion

Mach bands (Ernst Mach, 1865) are illusory bright and dark bands perceived at boundaries between adjacent, internally uniform regions of gradually changing luminance. Lateral inhibition in the visual system exaggerates contrast at each edge, so viewers report bands that are not physically in the stimulus. Case 2 renders the same phenomenon with a stacked-trapezoid layout instead of Case 1's equal vertical stripes.

## What the generator draws

A 512 x 512 canvas (white background) with 16 horizontal stripes stacked top to bottom, each `height // num_stripes` tall and horizontally centered. Stripe colors follow a perceptually uniform LAB gradient from `start_color` to `end_color` (defaults black to gray 0.7; the published sweep overrides via HSB to a dark-to-bright green ramp). Stripe widths increase linearly from `width // 8` (top) to the full image width (bottom), producing a pyramid/trapezoid-stacking silhouette. Stripes are drawn without antialiasing.

- **Original mode**: no borders; strength does not affect the drawing.
- **Perturbed mode**: each stripe gets a semi-transparent white border. Strength scales the border per `border_control_mode`: `'border_width'` (default) scales width = `default_border_width * strength`; `'border_alpha'` scales alpha = `default_border_alpha * strength`; `'both'` scales both.

Strength levels default to `[0.5, 0.75, 1.0, 1.25, 1.5]`.

## Variants

| Variant | Meaning here |
|---|---|
| original | Borderless gradient stripes; bands at boundaries are illusory. |
| original_control | Each stripe's height reduced by `stripes_offset` (2 px), leaving white gaps that break adjacency and remove the illusion. |
| perturbed | Semi-transparent white borders drawn on every stripe (scaled by strength), so boundaries physically exist. |
| perturbed_control | Perturbed borders plus the 2 px gaps. |
| with_guide | A 30 px vertical bar on the left edge showing the full smooth LAB gradient from `start_color` to `end_color`. |

Note: `apply_perturbation` is a no-op; the perturbed branch is handled inside `define_elements` via `is_original`.

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `start_color` | `(0, 0, 0)` | RGB start of the gradient (black). |
| `end_color` | `(0.7, 0.7, 0.7)` | RGB end of the gradient (gray). |
| `num_stripes` | `16` | Number of horizontal stripes. |
| `border_control_mode` | `'border_width'` | Which border property strength scales (`'border_width'`, `'border_alpha'`, `'both'`). |
| `default_border_width` | `3` | Base border width in pixels. |
| `default_border_alpha` | `0.15` | Base border alpha. |
| `border_color` | `(1, 1, 1)` | Border color (white). |

Sweep config (`color.yaml`): `num_stripes: 16`, plus HSB overrides `start_color: (0.0, 0.43, 0.26)` and `end_color: (0.0, 0.43, 1.0)`.

## Benchmark question

> "Is there an boundary in between every adjecent regions?"

(Typo preserved verbatim from the frozen as-run config.)

- **Original** (no drawn boundaries): correct answer is **0** (no).
- **Perturbed** (white borders drawn between stripes): correct answer is **1** (yes).

As with Case 1, polarity is inverted relative to most VI-Probe cases: the original image's ground-truth answer is "no".
