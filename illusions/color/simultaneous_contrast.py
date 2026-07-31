"""Simultaneous Contrast Illusion (color, VI-Probe case 14).

Two small rectangles of identical color appear different because they sit on
contrasting background rectangles.
"""

import colorsys
from typing import Any, Dict, Tuple

import numpy as np

from core.draw import (
    add_color_bar,
    add_rectangle,
    hsb_to_rgb,
    rgb_to_hsb,
)
from core.template import IllusionTemplate


class SimultaneousContrastIllusion(IllusionTemplate):
    """
    Simultaneous Contrast Illusion Generator - Case 1

    Generates the Simultaneous Contrast illusion with:
    - Two large background rectangles (pink and dark blue)
    - Two small rectangles with identical color (olive green)
    - Color perception influenced by background contrast

    Strength parameter controls small rectangle color via two modes:
    - 'hue': Rotate hue of olive green based on strength [0-2]
    - 'lightness': Directly scale lightness value
    """

    def __init__(self,
                 DEFAULT_COLOR=(0.65, 0.65, 0.35),  # Olive green
                 strength_mode='lightness',  # 'hue' or 'lightness',
                 LEFT_BG_COLOR = (0.5, 0.5, 0.5),  # Pink
                RIGHT_BG_COLOR = (0.752, 0.752, 0.752),  # Dark blue
                #  mode =<strength_mode>
                 ):
        """
        Initialize Simultaneous Contrast Illusion generator.

        Args:
            DEFAULT_COLOR: Base color for small rectangles (default: olive green)
            strength_mode: 'hue' for hue rotation, 'lightness' for brightness scaling
        """
        self.DEFAULT_COLOR = DEFAULT_COLOR
        self.strength_mode = strength_mode

        # Background rectangles configuration
        self.LEFT_BG_COLOR = LEFT_BG_COLOR
        self.RIGHT_BG_COLOR = RIGHT_BG_COLOR
        self.BG_RECT_WIDTH = 256
        self.BG_RECT_HEIGHT = 256

        # Small rectangles configuration (1/3 of background size)
        self.SMALL_RECT_SIZE_RATIO = 1 / 3

        super().__init__(
            illusion_name="simultaneous_contrast_case1",
            width=512,
            height=256,
            strength_levels=[0.5, 0.75, 1.0, 1.25, 1.5],
            background_color=(0.0, 0.0, 0.0),  # Black background
        )

    def _calculate_small_rect_color(self, strength: float) -> Tuple[float, float, float]:
        """
        Calculate small rectangle color based on strength and mode.

        Args:
            strength: Scaling/rotation factor

        Returns:
            RGB tuple (r, g, b) in range [0, 1]
        """
        if self.strength_mode == 'hue':
            # Hue rotation mode - directly rotate the olive green hue
            r, g, b = self.DEFAULT_COLOR
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            #apply to a base
            s = s+0.3
            s = min(1.0, max(0.0, s))
            # Apply hue rotation: strength 0→-180°, 1→0°, 2→+180°
            hue_rotation_degrees = (strength - 1.0) * 360
            h_degrees = h * 360
            h_new_degrees = (h_degrees + hue_rotation_degrees) % 360
            h_new = h_new_degrees / 360

            # Convert back to RGB with rotated hue
            r, g, b = colorsys.hls_to_rgb(h_new, l, s)
            return (r, g, b)

        else:  # lightness mode
            h, s, b = rgb_to_hsb(self.DEFAULT_COLOR)
            b_new = b * strength
            assert b_new <= 1.0, f"b_new: {b_new} is greater than 1.0"
            assert b_new >= 0.0, f"b_new: {b_new} is less than 0.0"
            r, g, b = hsb_to_rgb((h, s, b_new))
            return (r, g, b)
            # Direct lightness scaling
            # r, g, b = self.DEFAULT_COLOR
            # r_new = r * strength
            # g_new = g * strength
            # b_new = b * strength
            # # Clamp to [0, 1]
            # r_new = max(0.0, min(1.0, r_new))
            # g_new = max(0.0, min(1.0, g_new))
            # b_new = max(0.0, min(1.0, b_new))
            # return (r_new, g_new, b_new)

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Simultaneous Contrast illusion elements.

        For Original variation:
            - Both small rectangles have the same color (determined by strength)
        For Perturbed variation:
            - Left rectangle fixed at default (strength=1.0)
            - Right rectangle varies with strength

        Args:
            strength: Controls small rectangle color
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing background and small rectangle parameters
        """
        self.strength = strength

        # Calculate small rectangle colors
        if is_original:
            # Original: Both rectangles same color, vary with strength
            small_rect_color = self._calculate_small_rect_color(strength)
            left_small_color = small_rect_color
            right_small_color = small_rect_color
        else:
            # Perturbed: Right fixed, left varies
            left_small_color = self._calculate_small_rect_color(strength)
            right_small_color = self._calculate_small_rect_color(1.0)

        # Calculate positions and sizes
        center_y = self.height // 2  # 128
        left_bg_center_x = self.width // 4  # 128
        right_bg_center_x = 3 * self.width // 4  # 384

        small_rect_width = int(self.BG_RECT_WIDTH * self.SMALL_RECT_SIZE_RATIO)
        small_rect_height = int(self.BG_RECT_HEIGHT * self.SMALL_RECT_SIZE_RATIO)

        elements = {
            # Background rectangles
            'bg_left': {
                'center': (left_bg_center_x, center_y),
                'width': self.BG_RECT_WIDTH,
                'height': self.BG_RECT_HEIGHT,
                'color': self.LEFT_BG_COLOR,
            },
            'bg_right': {
                'center': (right_bg_center_x, center_y),
                'width': self.BG_RECT_WIDTH,
                'height': self.BG_RECT_HEIGHT,
                'color': self.RIGHT_BG_COLOR,
            },

            # Small rectangles
            'small_left': {
                'center': (left_bg_center_x, center_y),
                'width': small_rect_width,
                'height': small_rect_height,
                'color': left_small_color,
            },
            'small_right': {
                'center': (right_bg_center_x, center_y),
                'width': small_rect_width,
                'height': small_rect_height,
                'color': right_small_color,
            },

            # Control flag
            'draw_backgrounds': True,  # Control will set to False
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Simultaneous Contrast illusion on the canvas.

        Order of drawing:
        1. Background rectangles (if enabled)
        2. Small rectangles

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw background rectangles (if enabled)
        if elements.get('draw_backgrounds', True):
            # Left background
            bg_left = elements['bg_left']
            image = add_rectangle(
                image,
                rect_color=bg_left['color'],
                rect_center=bg_left['center'],
                rect_width=bg_left['width'],
                rect_height=bg_left['height'],
                antialias = False,
            )

            # Right background
            bg_right = elements['bg_right']
            image = add_rectangle(
                image,
                rect_color=bg_right['color'],
                rect_center=bg_right['center'],
                rect_width=bg_right['width'],
                rect_height=bg_right['height'],
                antialias = False,
            )

        # Draw small rectangles
        small_left = elements['small_left']
        image = add_rectangle(
            image,
            rect_color=small_left['color'],
            rect_center=small_left['center'],
            rect_width=small_left['width'],
            rect_height=small_left['height'],
            antialias = False,
        )

        small_right = elements['small_right']
        image = add_rectangle(
            image,
            rect_color=small_right['color'],
            rect_center=small_right['center'],
            rect_width=small_right['width'],
            rect_height=small_right['height'],
            antialias = False,
        )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add color bar between small rectangles as visual guide.

        The color bar connects the two small rectangles to help compare colors.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with color bar added
        """
        small_left = elements['small_left']
        small_right = elements['small_right']

        # Color bar parameters
        bar_width = 10

        image = add_color_bar(
            image_numpy=image,
            start_color=small_left['color'],
            end_color=small_left['color'],  # Same color = no gradient
            start_pos=small_left['center'],
            end_pos=small_right['center'],
            bar_width=bar_width,
            antialiasing=True,
            border_width=0  # No border
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing background rectangles.

        In the control condition, small rectangles are shown on uniform black background,
        making it clear they are the same color (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no backgrounds
        """
        elements['draw_backgrounds'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version with left rectangle fixed, right varies.

        The perturbation logic is already handled in define_elements(),
        so this method doesn't need to modify anything.

        Args:
            elements: Elements with perturbation already applied

        Returns:
            Unmodified elements
        """
        # Perturbation logic is already handled in define_elements()
        return elements
