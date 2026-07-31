# Cornsweet Illusion

Category: **color** — released VI-Probe case **12** (legacy config key: `CornswweetIllusion`, output folder `12_CornswweetIllusion`).

## The illusion

In the classic Cornsweet (Craik–O'Brien–Cornsweet) illusion, a sharp luminance edge with opposing shallow gradients on either side makes two physically identical regions appear to have different brightness (Cornsweet, 1970; after Craik and O'Brien). This generator uses the underlying mechanism — local luminance context biasing perceived surface color — by placing two identical gray targets on a smooth dark-to-light gradient, so the target on the dark side appears lighter than the one on the light side.

## What the generator draws

- Canvas: 512 x 256.
- Background: a horizontal, perceptually uniform gradient computed in LAB space from `GRADIENT_LEFT_COLOR` (default black) to `GRADIENT_RIGHT_COLOR` (default white), filling the whole canvas. In the published `color` sweep the gradient endpoints are supplied as HSB triples (0, 0.43, 0.2) to (0, 0.43, 0.95), i.e. a dark-red to light-red gradient rather than black-to-white.
- Two small circles (radius = width/30 ≈ 17 px), antialiased, at (width/4, height/2) and (3*width/4, height/2).

Circle color depends on `strength` and `strength_mode`:

- `lightness` mode (default): circle gray value = `DEFAULT_GRAY * strength`, clamped to [0, 1]; the circle is an achromatic gray.
- `hue` mode: circle color is HLS(`base_hue` + (strength - 1) * 360 degrees, `DEFAULT_GRAY`, `base_saturation`).

In **original** mode both circles get the same strength-dependent color. In **perturbed** mode the left circle varies with strength while the right circle is fixed at the strength = 1.0 color, so the two circles are genuinely different whenever strength != 1.0.

## Variants

| Variant | Meaning for this illusion |
|---|---|
| original | Both circles identical color (from strength) on the gradient background — they look different but are the same. |
| original_control | Same identical circles, but `draw_gradient` is set False, leaving the flat background color — no illusion. |
| perturbed | Left circle color from strength, right circle fixed at strength = 1.0 — genuinely different colors on the gradient. |
| perturbed_control | Same unequal circles without the gradient background. |
| with_guide | A solid horizontal bar (width = radius/1.5) connecting the two circle centers, drawn in the LEFT circle's color, allowing direct comparison. |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `DEFAULT_GRAY` | 0.65 | Base gray value [0, 1] of the circles (sweep uses 0.5). |
| `strength_mode` | `'lightness'` | `'lightness'` scales the gray; `'hue'` rotates a colored version of it. |
| `base_hue` | 180 | Base hue in degrees used in `'hue'` mode. |
| `base_saturation` | 0.3 | Saturation used in `'hue'` mode. |
| `GRADIENT_LEFT_COLOR` | (0, 0, 0) | Left end of the background gradient (sweep passes HSB (0, 0.43, 0.2)). |
| `GRADIENT_RIGHT_COLOR` | (1, 1, 1) | Right end of the background gradient (sweep passes HSB (0, 0.43, 0.95)). |

Fixed internals: circle radius ratio 1/30, circle x positions at 1/4 and 3/4 of the width, default strength levels [0.5, 0.75, 1.0, 1.25, 1.5]. The published sweep uses 51 strengths in [0.5, 1.5] excluding 1.0.

## Benchmark question

> Are the two circles of the same color?

Correct answer: **1 (yes)** for original images (identical circles, illusion or not), **0 (no)** for perturbed images (the left circle's color differs from the right).

## Notes

- The class docstring calls this "Case 2"; the published VI-Probe case number is 13.
- `background_color` is black but is fully covered by the gradient except in control variants.
