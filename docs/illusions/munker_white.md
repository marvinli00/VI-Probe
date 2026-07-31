# Munker-White Illusion

Category: **color** — released VI-Probe case **14** (config key: `MunkerWhiteIllusion`, output folder `14_MunkerWhiteIllusion`).

## The illusion

In White's illusion (White, 1979) and its chromatic extension by Munker, identical gray or colored bars embedded in a black/white grating appear different depending on which stripes overlap them: bars interleaved with white stripes look darker, bars interleaved with black stripes look lighter. Notably, the effect runs opposite to classical simultaneous contrast, which makes it a key test case for lightness theories.

## What the generator draws

- Canvas: 512 x 256, black background.
- A horizontal grating of `NUM_ALTERNATIONS` = 4 black/white stripe pairs (each stripe 16 px tall; the internal comment claiming "8 pairs" is stale).
- Two full-height vertical rectangles, 128 px wide (width/4), centered at x = 128 and x = 384.

Layering order creates the illusion: black stripes (full width) → left rectangle → white stripes (full width, overlaying the left rectangle) → right rectangle → black stripes (right half only, overlaying the right rectangle; the right-half black stripes are drawn 2 px thinner except the top one, shifted up 1 px). Result: the left rectangle is crossed by white stripes and appears darker, the right by black stripes and appears lighter.

Rectangle color depends on `strength` and `strength_mode`:

- `lightness` mode (default): convert `DEFAULT_COLOR` to HSB and multiply brightness by strength (asserted to stay in [0, 1]).
- `hue` mode: convert to HLS and rotate hue by (strength - 1) * 360 degrees.

In **original** mode both rectangles get the same strength-dependent color. In **perturbed** mode the left rectangle varies with strength and the right is fixed at the strength = 1.0 color.

## Variants

| Variant | Meaning for this illusion |
|---|---|
| original | Identical rectangles (from strength) interleaved with the black/white grating — they look different but are the same. |
| original_control | `draw_stripes` set False: the same identical rectangles on the plain black canvas — no illusion. |
| perturbed | Left rectangle from strength, right fixed at strength = 1.0 — genuinely different colors, grating present. |
| perturbed_control | Same unequal rectangles without the grating. |
| with_guide | A 40 px bar connecting the two rectangle centers, drawn in the LEFT rectangle's color (uniform, no gradient, no border). |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `DEFAULT_COLOR` | (0.65, 0.65, 0.35) | Base RGB color (olive green) of the vertical rectangles (also used by the sweep). |
| `strength_mode` | `'lightness'` | `'lightness'` scales HSB brightness; `'hue'` rotates hue. |
| `BLACK_STRIPE_COLOR` | (0, 0, 0) | "Black" stripe color (sweep passes HSB (0, 0.43, 0.26), a dark red). |
| `WHITE_STRIPE_COLOR` | (1, 1, 1) | "White" stripe color (sweep passes HSB (0, 0.43, 1.0), a light red). |

Fixed internals: 4 stripe alternations, rectangle width ratio 1/4, default strength levels [0.5, 0.75, 1.0, 1.25, 1.5]. The published sweep uses 51 strengths in [0.5, 1.5] excluding 1.0.

## Benchmark question

> Are the two rectangle the same color?

(Typo "rectangle" is verbatim from the frozen published config.) Correct answer: **1 (yes)** for original images, **0 (no)** for perturbed images.

## Notes

- The `define_elements` docstring says the perturbed variant fixes the left rectangle and varies the right; the code does the opposite (left varies, right fixed at strength = 1.0).
- The class docstring calls this "Case 1"; the published VI-Probe case number is 15.
