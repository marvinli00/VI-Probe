# Cornsweet Illusion Case 1

Category: **color** — released VI-Probe case **18** (`18_CornswweetIllusionCase1`, legacy class key `CornswweetIllusionCase1` — the double-w typo is preserved in config keys).

## The illusion

The Craik-O'Brien-Cornsweet illusion (O'Brien, 1958; Cornsweet, 1970) shows that a luminance edge can dictate the perceived brightness of entire surfaces: two physically identical regions separated by opposing gradients at their shared border appear to differ in lightness. The visual system extrapolates the local edge contrast across each whole region, filling in a brightness difference that is not physically there.

## What the generator draws

A 512 x 512 canvas split into left and right vertical halves. The left half is filled uniformly with `left_base_color`, the right half with `right_color` (see below). At the center boundary, opposing linear gradients are painted over a zone of `GRADIENT_WIDTH` pixels on each side: with default polarity, the left side ramps darker toward the boundary (`left_color - GRADIENT_CONTRAST * t`) and the right side starts lighter at the boundary and ramps back to its base color (`right_color + GRADIENT_CONTRAST * t`, decaying outward). Values are clipped to [0, 1].

- **Original mode**: both halves are filled with `left_base_color` — identical — and strength has no effect on the fill; only the edge gradients create the apparent difference.
- **Perturbed mode**: the left half stays at `left_base_color`; the right half is physically changed by strength. In `'lightness'` mode (used in the published sweep) each channel of `right_base_color` is multiplied by strength (clamped to [0, 1]). In `'hue'` mode the right color is hue-rotated by `(strength - 1) * 360` degrees in HLS space.

Strength levels default to `[0.5, 0.75, 1.0, 1.25, 1.5]`.

## Variants

| Variant | Meaning here |
|---|---|
| original | Identical halves with strong opposing edge gradients (`GRADIENT_CONTRAST=0.3`, `GRADIENT_WIDTH=100`); halves look different but are the same. |
| original_control | Gradient reduced to `CONTROL_GRADIENT_CONTRAST=0.05` over `CONTROL_GRADIENT_WIDTH=5` px, effectively removing the edge cue so the equality is visible. |
| perturbed | Right half's fill color physically scaled (lightness) or rotated (hue) by strength; full-strength gradients kept. |
| perturbed_control | Perturbed fill colors with the minimized gradient. |
| with_guide | A horizontal color bar (width up to 40 px) drawn across the middle from x = width/4 to 3*width/4; both bar endpoints use `left_color`, so it is a solid strip of the left region's color overlapping both halves for comparison. |

Note: `apply_perturbation` is a no-op; the perturbed branch is handled in `_calculate_colors` via `is_original`.

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `DEFAULT_GRAY` | `0.5` | Legacy base gray value, kept for backward compatibility (not used in drawing). |
| `left_base_color` | `(0.5, 0.5, 0.5)` | RGB fill of the left region (also both regions in original mode). |
| `right_base_color` | `(0.5, 0.5, 0.5)` | RGB base for the right region before strength scaling (perturbed mode). |
| `strength_mode` | `'lightness'` | `'lightness'` scales the right color's channels; `'hue'` rotates its hue. |
| `base_hue` | `180` | Base hue in degrees for hue mode. |
| `base_saturation` | `0.3` | Saturation for hue mode. |
| `GRADIENT_WIDTH` | `100` | Width in pixels of each gradient zone at the boundary. |
| `GRADIENT_CONTRAST` | `0.3` | Amplitude of the edge gradients. |
| `CONTROL_GRADIENT_CONTRAST` | `0.05` | Gradient amplitude in the control condition. |
| `CONTROL_GRADIENT_WIDTH` | `5` | Gradient width in the control condition. |

Sweep config (`color.yaml`): `DEFAULT_GRAY: 0.5`, `strength_mode: lightness`, with HSB overrides `left_base_color: (0.5, 0.5, 0.5)` and `right_base_color: (0.5, 0.5, 0.5)`.

## Benchmark question

> "Are the two vertical bands of the same color?"

- **Original** (both halves are `left_base_color`; the difference is illusory): correct answer is **1** (yes).
- **Perturbed** (right half physically brightened/darkened or hue-shifted): correct answer is **0** (no).

## Notes

- `base_hue` and `base_saturation` are stored but never referenced by the drawing or color-calculation code; hue mode operates directly on `right_base_color` in HLS space.
