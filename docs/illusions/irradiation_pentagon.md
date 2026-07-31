# Irradiation Pentagon Illusion

Category: **size** — released VI-Probe case **10** (`10_IrradiationPentagonIllusion`).

## The illusion

A shape variant of the classic irradiation effect (Helmholtz, 1867): a bright figure on a dark ground appears larger than an identical dark figure on a bright ground, because the bright region's borders perceptually spread outward. Here the effect is probed with regular pentagons instead of squares.

## What the generator draws

On a 512x256 white canvas, two large regular background pentagons of fixed radius 100 px (top vertex pointing up, `rotation_angle=-90`) are centered at (128, 128) and (384, 128). The left background pentagon is filled black; the right one is white with a 1 px black border. Inside each, a small pentagon is drawn: white on the left (on black), black on the right (on white).

Strength scales the small pentagons: `radius = DEFAULT_SMALL_RADIUS * strength`.

- Original mode: both small pentagons share the same strength-scaled radius; physically equal, the white one looks larger.
- Perturbed mode: the left small pentagon scales with strength while the right stays fixed at the default radius (unequal except at strength 1.0).

## Variants

| Variant | Meaning here |
|---|---|
| original | Equal strength-scaled small pentagons; white-on-black vs black-on-white backgrounds. |
| original_control | `apply_control_modification`: background pentagons not drawn and the left small pentagon recolored black — two identical black pentagons on white, no illusion. |
| perturbed | Left small pentagon strength-scaled, right fixed at default; backgrounds kept. Handled in `define_elements`; `apply_perturbation` is a no-op. |
| perturbed_control | Perturbed radii with backgrounds removed and both small pentagons black. |
| with_guide | `add_visual_guides`: two dashed red horizontal lines across the full width at the top and bottom vertices of the left small pentagon (computed from its actual vertex geometry). |

## Constructor parameters

| Parameter | Default | Sweep value | Meaning |
|---|---|---|---|
| `DEFAULT_SMALL_RADIUS` | 60 | 40 | Small pentagon circumradius in px at strength 1.0. |

Fixed by the class: background pentagon radius 100 px, 5 sides, -90 degree rotation, 512x256 white canvas, centers at width/4 and 3*width/4. The class defines `strength_levels=[0.4 ... 1.6]`, but the published sweep (`size.yaml`) uses 51 strengths from 0.5 to 1.5 with 1.0 excluded for perturbed.

## Benchmark question

Non-control images:

> "Are the left white pentagon and the right black pentagon equal in size?"

Control images (both small pentagons are black):

> "Are the left black pentagon and the right black pentagon equal in size?"

Correct answer: `1` (yes) for original images, `0` (no) for perturbed images.
