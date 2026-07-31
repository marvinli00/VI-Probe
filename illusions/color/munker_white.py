"""Munker-White Illusion (color, VI-Probe case 15).

Two vertical rectangles of identical color appear different because
alternating black/white stripe patterns overlay them differently.
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


class MunkerWhiteIllusion(IllusionTemplate):
    """
    Munker-White Illusion Generator - Case 1

    Generates the Munker-White illusion with:
    - Alternating black and white horizontal stripes
    - Two vertical rectangles with identical color (olive green)
    - Color perception influenced by overlapping stripe patterns

    Strength parameter controls vertical rectangle color via two modes:
    - 'hue': Rotate hue of olive green based on strength [0-2]
    - 'lightness': Directly scale lightness value
    """

    def __init__(self,
                 DEFAULT_COLOR=(0.65, 0.65, 0.35),  # Olive green
                 strength_mode='lightness',  # 'hue' or 'lightness',
                 BLACK_STRIPE_COLOR=(0, 0, 0),
                 WHITE_STRIPE_COLOR=(1, 1, 1),
                 ):
        """
        Initialize Munker-White Illusion generator.

        Args:
            DEFAULT_COLOR: Base color for vertical rectangles (default: olive green)
            strength_mode: 'hue' for hue rotation, 'lightness' for brightness scaling
        """
        self.DEFAULT_COLOR = DEFAULT_COLOR
        self.strength_mode = strength_mode

        # Stripe configuration
        self.NUM_ALTERNATIONS = 4  # 8 pairs of black/white stripes
        self.BLACK_STRIPE_COLOR = BLACK_STRIPE_COLOR
        self.WHITE_STRIPE_COLOR = WHITE_STRIPE_COLOR

        # Vertical rectangle configuration
        self.RECT_WIDTH_RATIO = 1 / 4  # Width = WIDTH // 4

        super().__init__(
            illusion_name="munker_white_case1",
            width=512,
            height=256,
            strength_levels=[0.5, 0.75, 1.0, 1.25, 1.5],
            background_color=(0.0, 0.0, 0.0),  # Black background
        )

    def _calculate_rect_color(self, strength: float) -> Tuple[float, float, float]:
        """
        Calculate vertical rectangle color based on strength and mode.

        Args:
            strength: Scaling/rotation factor

        Returns:
            RGB tuple (r, g, b) in range [0, 1]
        """
        if self.strength_mode == 'hue':
            # Hue rotation mode - directly rotate the olive green hue
            r, g, b = self.DEFAULT_COLOR
            h, l, s = colorsys.rgb_to_hls(r, g, b)

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
            # # Direct lightness scaling
            # r, g, b = self.DEFAULT_COLOR
            # r_new = r * strength
            # g_new = g * strength
            # b_new = b * strength
            # # Clamp to [0, 1]
            # r_new = max(0.0, min(1.0, r_new))
            # g_new = max(0.0, min(1.0, g_new))
            # b_new = max(0.0, min(1.0, b_new))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Munker-White illusion elements.

        For Original variation:
            - Both vertical rectangles have the same color (determined by strength)
        For Perturbed variation:
            - Left rectangle fixed at default (strength=1.0)
            - Right rectangle varies with strength

        Args:
            strength: Controls vertical rectangle color
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing stripe and rectangle parameters
        """
        self.strength = strength

        # Calculate vertical rectangle colors
        if is_original:
            # Original: Both rectangles same color, vary with strength
            rect_color = self._calculate_rect_color(strength)
            left_rect_color = rect_color
            right_rect_color = rect_color
        else:
            # Perturbed: Right fixed, left varies
            left_rect_color = self._calculate_rect_color(strength)
            right_rect_color = self._calculate_rect_color(1.0)

        # Calculate stripe dimensions
        alternation_height = self.height // self.NUM_ALTERNATIONS  # 32px
        stripe_height = alternation_height // 2  # 16px
        # Calculate rectangle dimensions
        rect_width = int(self.width * self.RECT_WIDTH_RATIO)  # 128px
        rect_height = self.height  # 256px

        # Calculate rectangle positions
        left_center_x = self.width // 4  # 128
        right_center_x = 3 * self.width // 4  # 384
        center_y = self.height // 2  # 128

        elements = {
            # Stripe parameters
            'stripe_height': stripe_height,
            'alternation_height': alternation_height,
            'black_color': self.BLACK_STRIPE_COLOR,
            'white_color': self.WHITE_STRIPE_COLOR,

            # Vertical rectangles
            'left_rect': {
                'center': (left_center_x, center_y),
                'width': rect_width,
                'height': rect_height,
                'color': left_rect_color,
            },
            'right_rect': {
                'center': (right_center_x, center_y),
                'width': rect_width,
                'height': rect_height,
                'color': right_rect_color,
            },

            # Control flag
            'draw_stripes': True,  # Control will set to False
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Munker-White illusion on the canvas.

        Drawing order is CRITICAL for creating the illusion:
        1. Black stripes (full width) - background layer
        2. Left vertical rectangle
        3. White stripes (full width) - overlays left rectangle
        4. Right vertical rectangle
        5. Black stripes (right half width) - overlays right rectangle

        This creates different overlay patterns:
        - Left rect: covered by white stripes → appears darker
        - Right rect: covered by black stripes → appears brighter

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        alternation_height = elements['alternation_height']
        stripe_height = elements['stripe_height']
        black_color = elements['black_color']
        if elements.get('draw_stripes', True):
            # Step 1: Draw black stripes (full width)
            for i in range(self.NUM_ALTERNATIONS):
                alternation_start_y = i * alternation_height
                rect_center_x = self.width // 2
                rect_center_y = alternation_start_y + stripe_height // 2

                image = add_rectangle(
                    image,
                    rect_color=black_color,
                    rect_center=(rect_center_x, rect_center_y),
                    rect_width=self.width,
                    rect_height=stripe_height,
                    antialias=False
                )

        # Step 2: Draw left vertical rectangle
        left_rect = elements['left_rect']
        image = add_rectangle(
            image,
            rect_color=left_rect['color'],
            rect_center=left_rect['center'],
            rect_width=left_rect['width'],
            rect_height=left_rect['height'],
            antialias=False
        )

        if elements.get('draw_stripes', True):
            # Step 3: Draw white stripes (full width) - overlays left rectangle
            white_color = elements['white_color']

            for i in range(self.NUM_ALTERNATIONS):
                alternation_start_y = i * alternation_height
                rect_center_x = self.width // 2
                rect_center_y = alternation_start_y + stripe_height + stripe_height // 2

                image = add_rectangle(
                    image,
                    rect_color=white_color,
                    rect_center=(rect_center_x, rect_center_y),
                    rect_width=self.width,
                    rect_height=stripe_height,
                    antialias=False
                )

        # Step 4: Draw right vertical rectangle
        right_rect = elements['right_rect']
        image = add_rectangle(
            image,
            rect_color=right_rect['color'],
            rect_center=right_rect['center'],
            rect_width=right_rect['width'],
            rect_height=right_rect['height'],
            antialias=False
        )

        if elements.get('draw_stripes', True):
            # Step 5: Draw black stripes (right half width) - overlays right rectangle
            for i in range(self.NUM_ALTERNATIONS):
                alternation_start_y = i * alternation_height
                rect_center_x = self.width // 2 + self.width // 4  # Right side
                rect_center_y = alternation_start_y + stripe_height // 2
                if i == 0:
                    image = add_rectangle(
                        image,
                        rect_color=black_color,
                        rect_center=(rect_center_x, rect_center_y-1),
                        rect_width=self.width // 2,
                        rect_height=stripe_height,
                        antialias=False
                    )
                else:
                    image = add_rectangle(
                        image,
                        rect_color=black_color,
                        rect_center=(rect_center_x, rect_center_y),
                        rect_width=self.width // 2,
                        rect_height=stripe_height - 2,
                        antialias=False
                    )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add color bar between vertical rectangles as visual guide.

        The color bar uses LEFT rectangle's color (no gradient) to help
        compare the two rectangles.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with color bar added
        """
        left_rect = elements['left_rect']
        right_rect = elements['right_rect']

        # Color bar uses LEFT rectangle color (same start and end = no gradient)
        bar_color = left_rect['color']
        bar_width = 40

        image = add_color_bar(
            image_numpy=image,
            start_color=bar_color,
            end_color=bar_color,  # Same color = no gradient
            start_pos=left_rect['center'],
            end_pos=right_rect['center'],
            bar_width=bar_width,
            antialiasing=False,
            border_width=0  # No border
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing stripe patterns.

        In the control condition, vertical rectangles are shown on uniform black background,
        making it clear they are the same color (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no stripes
        """
        elements['draw_stripes'] = False
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
