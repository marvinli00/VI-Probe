# Adding a new illusion

Every illusion is a subclass of `IllusionTemplate` (`core/template.py`). The base class
owns the canvas, the six variant types, file naming and the strength sweep; your subclass
only describes *what to draw*.

## The contract

```python
from typing import Any, Dict

from core.template import IllusionTemplate
from core.draw import add_arrowed_line, add_rectangle


class MyIllusion(IllusionTemplate):
    def __init__(self, DEFAULT_LINE_LENGTH: int = 200):
        self.DEFAULT_LINE_LENGTH = DEFAULT_LINE_LENGTH
        super().__init__(
            illusion_name="my_illusion",
            width=512, height=256,                 # the published canvas size
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),
        )

    # 1. REQUIRED — geometry/colors for a given strength, as a plain dict
    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        length = self.DEFAULT_LINE_LENGTH * strength
        return {"line_1": {"start": (100, 100), "end": (100 + length, 100),
                           "color": (0, 0, 0), "width": 2}}

    # 2. REQUIRED — draw the elements onto the float32 [0,1] RGB canvas
    def generate_illusion(self, image, elements):
        line = elements["line_1"]
        return add_arrowed_line(image, line["color"], line["start"], line["end"],
                                line_width=line["width"])

    # 3. OPTIONAL — guide bars/markers for the *_with_guide variants
    def add_visual_guides(self, image, elements):
        return image

    # 4. OPTIONAL — neutralize the illusion (the matched control)
    def apply_control_modification(self, elements):
        return elements

    # 5. OPTIONAL — the physically-changed version (ground truth flips)
    def apply_perturbation(self, elements):
        return elements
```

Semantics of the variants:

| Variant | Meaning |
|---|---|
| `original` | the illusion as classically drawn — the two targets ARE equal/straight/aligned |
| `original_control` | same scene with the illusion-inducing context neutralized |
| `perturbed` | targets are *physically* different, scaled by `strength` |
| `perturbed_control` | perturbed targets without the inducing context |
| `*_with_guide` | guide bars/markers added so the true relation is visually checkable |

Strength is multiplicative around 1.0 (published sweep: 0.5–1.5; 1.0 = "equal", excluded
from the perturbed sweep).

## Rendering

```python
illusion = MyIllusion()
illusion.set_variation(perturbed=True, visual_guide=True)
image = illusion.generate(strength=1.2, save=False)      # np.float32 (H, W, 3) in [0, 1]

illusion.set_output_dir("output")                        # optional; this is the default
illusion.generate_all()                                  # all variants x strength levels
```

Files are written to `output/my_illusion/<variant>/strength_pos1p2.png`.

## Drawing primitives

`core.draw` operates on float [0, 1] RGB numpy arrays, anti-aliased:
`add_arrowed_line`, `add_rectangle`, `add_circle`, `add_polygon`, `add_curved_line`,
`add_color_bar`, `add_letter` / `add_text`,
`add_rotated_rectangle_sr` + `generate_checkerboard_pattern` (OpenCV-backed super-resolution),
plus color utilities (`hsl_to_rgb`, `hsb_to_rgb`, `rgb_to_hsl`, `rgb_to_hsb`) and perceptual
gradients (`calculate_perceptual_gradient_lab`).

## Registering

Add an `IllusionSpec` entry in `illusions/registry.py` (module path, class,
category, and — only for published cases — case number and legacy names). `python main.py --list`
and the sweep pick it up from there. To include it in a sweep, add the class to a
config under `configs/sweeps/` with its constructor params and question.

## Determinism

Generators must be deterministic given their constructor args — avoid unseeded RNG.
If randomness is needed, take a `seed` constructor parameter (see `ChubbIllusion` for the
pattern and why: its historical unseeded noise makes the published Chubb images the only
ones that cannot be regenerated pixel-exactly).
