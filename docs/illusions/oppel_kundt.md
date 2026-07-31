# Oppel-Kundt Illusion

Category: **size** — released VI-Probe case **8** (`8_OppelKundtIllusion`).

## The illusion

First reported by Johann Joseph Oppel (1855) and later studied by August Kundt (1863), the Oppel-Kundt illusion shows that a spatial extent subdivided by intervening elements appears longer than an equal, empty extent. It is one of the oldest documented geometric-optical illusions, yet it still lacks a fully accepted explanation.

## What the generator draws

On a 512x256 white canvas, three tall black vertical boundary lines (100 px tall, 2 px wide, vertically centered) define two horizontal segments: left boundary at `center_x - left_segment_length`, center boundary at `center_x`, right boundary at `center_x + right_segment_length`. Small black letters "A", "B", "C" are drawn just below the left, center, and right boundaries. The **right** segment (B-C) additionally contains 7 intermediate vertical lines (`NUM_DIVISIONS = 8`, evenly spaced at `right_segment_length // 8`), same height and style as the boundaries; the left segment (A-B) is empty.

Strength (levels 0.4-1.6) scales segment length: `segment_length = DEFAULT_SEGMENT_LENGTH * strength`. In **original** mode both segments get this length (equal). In **perturbed** mode the left segment is fixed at the default length while the right segment is strength-scaled — this is done directly in `define_elements` (with subdivision spacing recomputed), so `apply_perturbation` is a no-op.

## Variants

| Variant | What it means here |
|---|---|
| original | Both segments equal (strength-scaled); right segment filled with 7 subdivision lines |
| original_control | Same boundaries and letters, `draw_subdivisions = False`: no intermediate lines |
| perturbed | Left segment fixed at default length, right segment strength-scaled; subdivisions kept |
| perturbed_control | Perturbed lengths, no subdivision lines |
| with_guide | Three short vertical markers (20 px tall) near the top of the image at the three boundary x-positions, plus a horizontal line connecting them through their midpoints |

## Constructor parameters

| Parameter | Default (code) | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_SEGMENT_LENGTH` | 192 | 100 | Segment length in pixels at strength 1.0 (each segment spans this distance from the center boundary) |

Fixed internals: 512x256 canvas, white background, black 2 px lines, 100 px boundary height, 8 divisions, strength levels `[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]`.

## Benchmark question

> "Are the distances between the vertical markers labeled A–B and B–C equal?"

Correct answer: **1 (yes)** for original images, **0 (no)** for perturbed images (except strength = 1.0, where both segments are equal).

## Notes

Because subdivision spacing uses integer division (`right_segment_length // 8`), the last subdivision gap before the C boundary can be slightly wider than the others. Unlike most illusions in this suite, the perturbation is applied inside `define_elements` rather than `apply_perturbation`.
