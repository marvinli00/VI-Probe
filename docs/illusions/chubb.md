# Chubb Illusion

Category: **color** — released VI-Probe case **17** (`17_ChubbIllusion`).

## The illusion

The Chubb illusion, or contrast-contrast effect (Chubb, Sperling & Solomon, 1989), shows that the perceived contrast of a texture depends on the contrast of its surround. A patch embedded in a high-contrast textured background appears to have lower contrast than an identical patch on a uniform background, demonstrating that contrast perception is computed relative to spatial context.

## What the generator draws

A 512 x 256 canvas split into two background halves: the left half is a uniform gray rectangle (`left_bg_color = (0.5, 0.5, 0.5)`, re-tinted via `modify_color` with the configured hue/saturation), the right half is filled with high-contrast binary random noise (values 0/255, clipped to [0.1, 0.9] and color-tinted). One circle (radius `width // 16`) sits at the center of each half, filled with binary noise textures alpha-blended onto the background at `circle_alpha`.

Circle contrast uses a midpoint-preserving formula around `mid = (base_low + base_high) / 2`: `low = mid - strength * range`, `high = mid + strength * range` (clamped to [0, 255], then clipped to [0.1, 0.9] after normalization). All textures are recolored through `update_texture_color` / `modify_color`, which maps each unique gray value to an HSB/HSL-tinted color using the constructor `hue` and `base_saturation`.

- **Original mode**: both circles get identical contrast, computed from the current strength.
- **Perturbed mode** (`perturb_mode='contrast'`, the default): the left circle is fixed at strength 1.0; the right circle uses the mirrored strength `2 - strength` (`strength_map = -(s-1)+1`), so its physical contrast differs from the left. With `perturb_mode='hue'`, both circles keep default contrast and the right circle's texture is instead hue-shifted by `(strength - 1) * 360 / 180` via `modify_color`.

Strength levels default to `[0.5, 0.75, 1.0, 1.25, 1.5]`.

## Variants

| Variant | Meaning here |
|---|---|
| original | Gray/noise backgrounds plus two circles with physically identical noise contrast. |
| original_control | `draw_backgrounds=False`: circles rendered on plain white, so their equal contrast is obvious and no illusion occurs. |
| perturbed | Right circle's contrast (or hue, in `'hue'` mode) actually differs from the left circle's. |
| perturbed_control | Perturbed circles without the background rectangles. |
| with_guide | A horizontal noise bar (width `width // 2`, height half the circle radius) drawn across the image center, regenerated with the left circle's contrast values and the same color tinting, for direct comparison. |

Note: `apply_perturbation` is a no-op; the perturbation lives in `define_elements`.

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `base_low` | `0` | Low value of circle noise contrast (0-255 scale). |
| `base_high` | `170` | High value of circle noise contrast. |
| `circle_alpha` | `1` | Alpha for blending circle textures onto the background. |
| `base_saturation` | `0.5` | Saturation used when tinting all textures. |
| `hue` | `(0, 0.5, 0.5)` | RGB tuple converted via `rgb_to_hsl` to the tint hue. |
| `perturb_mode` | `'contrast'` | What the perturbation changes: `'contrast'` or `'hue'`. |
| `seed` | `None` | Optional numpy seed applied at the start of `define_elements` for reproducible noise. |

Sweep config (`color.yaml`): `base_saturation: 0.2`, `circle_alpha: 1`, and HSB override `hue: (0, 0.5, 0.5)`.

## Benchmark question

> "Are the two circles of the same color?"

- **Original** (identical circle textures, illusory difference from context): correct answer is **1** (yes).
- **Perturbed** (right circle physically different): correct answer is **0** (no).

## Notes

- The `hue=0` historical default crashed (`rgb_to_hsl` cannot unpack an int); the packaged default is now `hue=(0, 0.5, 0.5)`, the value used to render the published dataset.
- The published dataset was generated with an **unseeded** RNG, so its exact noise textures are not bit-reproducible. The new `seed` parameter makes fresh generations reproducible; `seed=None` preserves the original behavior.
