# Hering Illusion

Category: **orientation** — released VI-Probe case **19** (output folder `19_HeringIllusion`).

## The illusion

In the Hering illusion (Ewald Hering, 1861), two straight parallel lines are laid over a fan of lines radiating from a central point. The radial pattern induces an illusory perception of depth/expansion, making the straight lines appear to bow outward away from the center even though they are perfectly straight.

## What the generator draws

On a 512x512 white canvas the generator draws:

- A fan of thin black radial lines (1 px) emanating from the image center at equal angular spacing, extending past the image edges.
- Two horizontal black test lines (3 px), the upper at y = 195 and the lower at y = 316, spanning x = 25 to x = 487.

Effect of `strength`:

- **Original mode**: the test lines are always straight; strength scales the radial-line density, `num_lines = int(DEFAULT_NUM_RADIAL_LINES * strength)` (denser fan = stronger illusion). In the published sweep the density is instead driven per-strength via a table (see below).
- **Perturbed mode**: the radial fan is fixed at `DEFAULT_NUM_RADIAL_LINES`; the test lines get a parabolic curve of amplitude `15 * (strength - 1.0)` px at their midpoints. strength = 1.0 gives straight lines; strength > 1.0 bows them outward (upper line up, lower line down); strength < 1.0 bows them inward.

## Variants

| Variant | Meaning here |
|---|---|
| original | Radial fan + two straight horizontal lines (illusion present, lines truly straight) |
| original_control | Radial fan removed (`radial_lines.draw = False`); straight lines only |
| perturbed | Radial fan (fixed density) + genuinely curved test lines (parabolic, amplitude 15·(strength−1)) |
| perturbed_control | Curved test lines with the radial fan removed |
| with_guide | One opaque light-blue rectangle (alpha = 1) filling the region between the two test lines (x 25–487, y 195–316) |

## Constructor parameters

| Parameter | Default | Meaning |
|---|---|---|
| `DEFAULT_NUM_RADIAL_LINES` | 32 | Base number of radial background lines; fixed count in perturbed mode, multiplied by strength in original mode |

In the published sweep (`orientation.yaml`, `param_mode: table`), `DEFAULT_NUM_RADIAL_LINES` is set per scale factor from 6 (at 0.50) to 46 (at 1.50) in steps of 2. `is_guide_first_by_class` is `true` for this class.

## Benchmark question

> Are the two horizontal lines straight?

Correct answer: **1 (yes)** for original images (lines are straight), **0 (no)** for perturbed images (lines are actually curved).

## Notes

- Internal strength levels `[0.4 ... 1.6]` set in `__init__` are overridden by the sweep config (0.5–1.5, 11 steps, 1.0 excluded for perturbed).
- The guide rectangle uses `GUIDE_ALPHA = 1`, so despite comments about transparency it is fully opaque and covers the middle radial lines between the test lines.
