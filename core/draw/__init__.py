"""Low-level drawing primitives.

All functions operate in place on float32 RGB numpy arrays with values in
[0, 1] and shape (height, width, 3), and also return the array.
"""

from .add_arrowed_line import add_arrowed_line
from .add_circle import add_circle
from .add_color_bar import add_color_bar
from .add_curved_line import add_curved_line
from .add_letter import add_letter, add_text
from .add_polygon import add_polygon
from .add_rectangle import add_rectangle
from .add_rotated_rectangle_sr import add_rotated_rectangle_sr, generate_checkerboard_pattern
from .calculate_grad import (
    calculate_gradient,
    calculate_perceptual_gradient_gamma,
    calculate_perceptual_gradient_lab,
    lab_to_rgb,
    rgb_to_lab,
)
from .color_converter import hsb_to_rgb, hsl_to_rgb, rgb_to_hsb, rgb_to_hsl

# OpenCV is only required when add_rotated_rectangle_sr is actually called
# (lazy import inside the function); importing this package works without it.

__all__ = [
    "add_arrowed_line",
    "add_circle",
    "add_color_bar",
    "add_curved_line",
    "add_letter",
    "add_text",
    "add_polygon",
    "add_rectangle",
    "add_rotated_rectangle_sr",
    "generate_checkerboard_pattern",
    "calculate_gradient",
    "calculate_perceptual_gradient_gamma",
    "calculate_perceptual_gradient_lab",
    "lab_to_rgb",
    "rgb_to_lab",
    "hsb_to_rgb",
    "hsl_to_rgb",
    "rgb_to_hsb",
    "rgb_to_hsl",
]
