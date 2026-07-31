# Mach Band Illusion

Category: **color** — released VI-Probe case **15** (`15_MachBandIllusion`).

## The illusion

Mach bands (Ernst Mach, 1865) are illusory bright and dark bands perceived at the boundaries between adjacent regions of gradually changing luminance, even though each region is internally uniform and no such bands exist in the stimulus. The effect is classically attributed to lateral inhibition in the retina, which exaggerates contrast at edges.

## What the generator draws

A 512 x 256 canvas (white background) filled with 16 vertical stripes of equal width (`width // num_stripes`). Stripe colors are sampled from a perceptually uniform gradient computed in LAB color space between `start_color` and `end_color` (defaults black to green; the published sweep overrides these via HSB parameters to a dark-to-bright green ramp). Stripes are drawn with `antialias=False` so the boundaries stay sharp.

- **Original mode**: stripes are drawn with no borders (`border_width=0`, `border_alpha=0`); strength does not change the drawing at all.
- **Perturbed mode**: each stripe gets a semi-transparent white border, making real boundaries between regions. Strength scales the border according to `border_control_mode`:
  - `'border_width'` (default): border width = `default_border_width * strength`, alpha fixed at `default_border_alpha`.
  - `'border_alpha'`: alpha = `default_border_alpha * strength`, width fixed.
  - `'both'`: both scale with strength.

Strength levels default to `[0.5, 0.75, 1.0, 1.25, 1.5]`.

## Variants

| Variant | Meaning here |
|---|---|
| original | Borderless gradient stripes; illusory bands appear at boundaries. |
| original_control | Same stripes but each is narrowed by `stripes_offset` (2 px), leaving white gaps that break adjacency and kill the illusion. |
| perturbed | Semi-transparent white borders drawn between stripes (properties scaled by strength), so boundaries are physically present. |
| perturbed_control | Perturbed stripes plus the 2 px gaps. |
| with_guide | A 30 px horizontal bar at the top of the image showing the full smooth LAB gradient from `start_color` to `end_color`. |

Note: `apply_perturbation` is a no-op; the perturbation branch lives entirely in `define_elements` (keyed on `is_original`).

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `start_color` | `(0, 0, 0)` | RGB start of the stripe gradient (black). |
| `end_color` | `(0, 1, 0)` | RGB end of the gradient (green). |
| `num_stripes` | `16` | Number of vertical stripes. |
| `border_control_mode` | `'border_width'` | Which border property strength scales (`'border_width'`, `'border_alpha'`, `'both'`). |
| `default_border_width` | `3` | Base border width in pixels. |
| `default_border_alpha` | `0.1` | Base border alpha. |
| `border_color` | `(1, 1, 1)` | Border color (white). |

Sweep config (`color.yaml`): `num_stripes: 16`, plus HSB overrides `start_color: (0.0, 0.43, 0.26)` and `end_color: (0.0, 0.43, 1.0)`.

## Benchmark question

> "Is there an boundary in between every adjecent regions?"

(Typo preserved verbatim from the frozen as-run config.)

- **Original** (no drawn boundaries; any perceived bands are illusory): correct answer is **0** (no).
- **Perturbed** (white borders physically drawn between stripes): correct answer is **1** (yes).

Note the polarity is inverted relative to most VI-Probe cases: here the original image's ground-truth answer is "no".
