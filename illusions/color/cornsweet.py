"""Cornsweet Illusion (color, VI-Probe case 13). Two identical gray circles on a perceptually uniform LAB gradient background appear different in brightness."""

import colorsys
from typing import Any, Dict, Tuple

import numpy as np

from core.draw import (
    add_circle,
    add_color_bar,
    calculate_perceptual_gradient_lab,
)
from core.template import IllusionTemplate


class CornsweetIllusion(IllusionTemplate):
    """
    Cornsweet Illusion Generator - Case 2

    Generates the Cornsweet illusion with:
    - Perceptually uniform gradient background (LAB space)
    - Two circles with identical gray color
    - Color perception influenced by background gradient

    Strength parameter controls circle color via two modes:
    - 'hue': Add base hue to gray, then rotate based on strength [0-2]
    - 'lightness': Directly scale gray lightness value
    """

    def __init__(self,
                 DEFAULT_GRAY=0.65,
                 strength_mode='lightness',  # 'hue' or 'lightness'
                 base_hue=180,  # Cyan base hue for gray (degrees)
                 base_saturation=0.3,
                 GRADIENT_LEFT_COLOR=(0, 0, 0),
                 GRADIENT_RIGHT_COLOR=(1, 1, 1)):  # Saturation to add for hue visibility
        """
        Initialize Cornsweet Illusion generator.

        Args:
            DEFAULT_GRAY: Base gray value [0-1] for circles (default: 0.65)
            strength_mode: 'hue' for hue rotation, 'lightness' for brightness scaling
            base_hue: Base hue in degrees [0-360] to add to gray before rotation
            base_saturation: Saturation [0-1] to add for hue mode
        """
        self.DEFAULT_GRAY = DEFAULT_GRAY
        self.strength_mode = strength_mode
        self.base_hue = base_hue
        self.base_saturation = base_saturation

        # Circle configuration
        self.CIRCLE_RADIUS_RATIO = 1 / 30  # radius = WIDTH // 30
        self.LEFT_CIRCLE_X_RATIO = 1 / 4
        self.RIGHT_CIRCLE_X_RATIO = 3 / 4

        # Gradient configuration
        self.GRADIENT_LEFT_COLOR = GRADIENT_LEFT_COLOR  # Black
        self.GRADIENT_RIGHT_COLOR = GRADIENT_RIGHT_COLOR  # White

        super().__init__(
            illusion_name="cornsweet_case2",
            width=512,
            height=256,
            strength_levels=[0.5, 0.75, 1.0, 1.25, 1.5],
            background_color=(0.0, 0.0, 0.0),  # Black background (will be overridden by gradient)
        )

    def _calculate_circle_color(self, strength: float) -> Tuple[float, float, float]:
        """
        Calculate circle color based on strength and mode.

        Args:
            strength: Scaling/rotation factor

        Returns:
            RGB tuple (r, g, b) in range [0, 1]
        """
        if self.strength_mode == 'hue':
            # Hue rotation mode
            # Convert gray to HSL with base hue and saturation
            h = self.base_hue / 360  # Normalize to [0, 1]
            l = self.DEFAULT_GRAY
            s = self.base_saturation

            # Apply hue rotation: strength 0→-180°, 1→0°, 2→+180°
            hue_rotation_degrees = (strength - 1.0) * 360
            h_degrees = h * 360
            h_new_degrees = (h_degrees + hue_rotation_degrees) % 360
            h_new = h_new_degrees / 360

            # Convert HLS to RGB
            r, g, b = colorsys.hls_to_rgb(h_new, l, s)
            return (r, g, b)

        else:  # lightness mode
            # Direct lightness scaling



            gray_value = self.DEFAULT_GRAY * strength
            gray_value = max(0.0, min(1.0, gray_value))  # Clamp to [0, 1]
            return (gray_value, gray_value, gray_value)

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Cornsweet illusion elements.

        For Original variation:
            - Both circles have the same color (determined by strength)
        For Perturbed variation:
            - Left circle varies with strength
            - Right circle fixed at default (strength=1.0)

        Args:
            strength: Controls circle color
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing circles and gradient parameters
        """
        self.strength = strength

        # Calculate circle colors
        if is_original:
            # Original: Both circles same color, vary with strength
            circle_color = self._calculate_circle_color(strength)
            left_circle_color = circle_color
            right_circle_color = circle_color
        else:
            # Perturbed: Left varies, right fixed
            left_circle_color = self._calculate_circle_color(strength)
            right_circle_color = self._calculate_circle_color(1.0)

        # Calculate positions
        center_y = self.height // 2
        left_center_x = int(self.width * self.LEFT_CIRCLE_X_RATIO)   # WIDTH // 4
        right_center_x = int(self.width * self.RIGHT_CIRCLE_X_RATIO) # 3 * WIDTH // 4
        circle_radius = int(self.width * self.CIRCLE_RADIUS_RATIO)   # WIDTH // 30

        elements = {
            # Left circle
            'circle_left': {
                'center': (left_center_x, center_y),
                'radius': circle_radius,
                'color': left_circle_color,
            },

            # Right circle
            'circle_right': {
                'center': (right_center_x, center_y),
                'radius': circle_radius,
                'color': right_circle_color,
            },

            # Gradient background parameters
            'draw_gradient': True,  # Control will set to False
            'gradient_left_color': self.GRADIENT_LEFT_COLOR,
            'gradient_right_color': self.GRADIENT_RIGHT_COLOR,
            'gradient_width': self.width,

            # Store for later use
            'circle_radius': circle_radius,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Cornsweet illusion on the canvas.

        Order of drawing:
        1. Gradient background (if enabled)
        2. Left circle
        3. Right circle

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw gradient background (if enabled)
        if elements.get('draw_gradient', True):
            left_color = elements['gradient_left_color']
            right_color = elements['gradient_right_color']
            gradient_width = elements['gradient_width']

            # Generate perceptually uniform gradient using LAB color space
            gradient = calculate_perceptual_gradient_lab(
                left_color, right_color, gradient_width
            )

            # Fill canvas with gradient
            image[:, :gradient_width, :] = gradient

        # Draw left circle
        circle_left = elements['circle_left']
        image = add_circle(
            image,
            circle_color=circle_left['color'],
            circle_center=circle_left['center'],
            circle_radius=circle_left['radius'],
            antialias=True
        )

        # Draw right circle
        circle_right = elements['circle_right']
        image = add_circle(
            image,
            circle_color=circle_right['color'],
            circle_center=circle_right['center'],
            circle_radius=circle_right['radius'],
            antialias=True
        )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add color bar between circles as visual guide.

        The color bar uses the LEFT circle's color (no gradient) to help
        compare the two circles.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with color bar added
        """
        circle_left = elements['circle_left']
        circle_right = elements['circle_right']
        circle_radius = elements['circle_radius']

        # Color bar uses LEFT circle color (same start and end = no gradient)
        bar_color = circle_left['color']

        # Width is circle radius / 1.5 (from notebook)
        bar_width = circle_radius / 1.5

        image = add_color_bar(
            image_numpy=image,
            start_color=bar_color,
            end_color=bar_color,  # Same color = no gradient
            start_pos=circle_left['center'],
            end_pos=circle_right['center'],
            bar_width=bar_width,
            antialiasing=False,
            border_width=0
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing gradient background.

        In the control condition, circles are shown on uniform background,
        making it clear they are the same color (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no gradient
        """
        elements['draw_gradient'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version with left circle varying, right fixed.

        The perturbation logic is already handled in define_elements(),
        so this method doesn't need to modify anything.

        Args:
            elements: Elements with perturbation already applied

        Returns:
            Unmodified elements
        """
        # Perturbation logic is already handled in define_elements()
        return elements
