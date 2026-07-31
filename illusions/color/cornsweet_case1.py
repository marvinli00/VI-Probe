"""Cornsweet Illusion Case 1 (color, VI-Probe case 19). Two uniform color regions with opposing gradients at the center boundary appear different in brightness although they are identical."""

import colorsys
from typing import Any, Dict, Tuple

import numpy as np

from core.draw import add_color_bar
from core.template import IllusionTemplate


class CornsweetIllusionCase1(IllusionTemplate):
    """
    Cornsweet Illusion Generator - Case 1

    Generates the Cornsweet illusion with:
    - Two uniform color regions (left and right halves)
    - Opposing gradients at center boundary
    - Color perception influenced by edge gradients

    Strength parameter controls color difference between regions:
    - 1.0: Both regions identical (classic illusion)
    - < 1.0: Left region darker
    - > 1.0: Right region lighter
    """

    def __init__(self,
                 DEFAULT_GRAY=0.5,
                 left_base_color=(0.5, 0.5, 0.5),
                 right_base_color=(0.5, 0.5, 0.5),
                 strength_mode='lightness',  # 'hue' or 'lightness'
                 base_hue=180,  # Cyan base hue for hue mode (degrees)
                 base_saturation=0.3,  # Saturation for hue mode
                 GRADIENT_WIDTH=100,
                 GRADIENT_CONTRAST=0.3,
                 CONTROL_GRADIENT_CONTRAST=0.05,
                 CONTROL_GRADIENT_WIDTH=5):
        """
        Initialize Cornsweet Illusion Case 1 generator.

        Args:
            DEFAULT_GRAY: Base gray value [0-1] for regions (default: 0.5, kept for backward compatibility)
            left_base_color: Base color for left region, RGB tuple [0-1] (default: (0.5, 0.5, 0.5))
            right_base_color: Base color for right region, RGB tuple [0-1] (default: (0.5, 0.5, 0.5))
            strength_mode: 'hue' for hue rotation, 'lightness' for brightness scaling
            base_hue: Base hue in degrees [0-360] for hue mode (default: 180)
            base_saturation: Saturation [0-1] for hue mode (default: 0.3)
            GRADIENT_WIDTH: Width of gradient zone in pixels (default: 100)
            GRADIENT_CONTRAST: Gradient contrast for illusion [0-0.5] (default: 0.3)
            CONTROL_GRADIENT_CONTRAST: Minimal gradient for control condition (default: 0.05)
            CONTROL_GRADIENT_WIDTH: Minimal gradient width for control (default: 5)
        """
        self.DEFAULT_GRAY = DEFAULT_GRAY
        self.left_base_color = left_base_color
        self.right_base_color = right_base_color
        self.strength_mode = strength_mode
        self.base_hue = base_hue
        self.base_saturation = base_saturation
        self.GRADIENT_WIDTH = GRADIENT_WIDTH
        self.GRADIENT_CONTRAST = GRADIENT_CONTRAST
        self.CONTROL_GRADIENT_CONTRAST = CONTROL_GRADIENT_CONTRAST
        self.CONTROL_GRADIENT_WIDTH = CONTROL_GRADIENT_WIDTH

        super().__init__(
            illusion_name="cornsweet_case1",
            width=512,
            height=512,
            strength_levels=[0.5, 0.75, 1.0, 1.25, 1.5],
            background_color=(0.0, 0.0, 0.0),  # Will be overridden by regions
        )

    def _calculate_colors(self, strength: float, is_original: bool) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Calculate left and right region colors based on strength and mode.

        Args:
            strength: Scaling/rotation factor
            is_original: Whether this is the original variation

        Returns:
            (left_color, right_color) as RGB tuples in range [0, 1]
        """
        if is_original:
            # Original: Both regions use the same left_base_color
            left_color = self.left_base_color
            right_color = self.left_base_color
        else:
            # Perturbed: Left fixed, right varies with strength
            left_color = self.left_base_color

            # Apply strength transformation to right color based on mode
            if self.strength_mode == 'hue':
                # Hue rotation mode
                # Convert right_base_color to HSL
                r, g, b = self.right_base_color
                h, l, s = colorsys.rgb_to_hls(r, g, b)

                # Apply hue rotation: strength 0→-180°, 1→0°, 2→+180°
                hue_rotation_degrees = (strength - 1.0) * 360
                h_degrees = h * 360
                h_new_degrees = (h_degrees + hue_rotation_degrees) % 360
                h_new = h_new_degrees / 360

                # Convert back to RGB
                r_new, g_new, b_new = colorsys.hls_to_rgb(h_new, l, s)
                right_color = (r_new, g_new, b_new)

            else:  # lightness mode
                # Direct lightness scaling
                right_color = tuple(
                    max(0.0, min(1.0, c * strength))
                    for c in self.right_base_color
                )

        return left_color, right_color

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Cornsweet illusion elements.

        For Original variation:
            - Both regions have the same color (strength doesn't affect it)
        For Perturbed variation:
            - Left region fixed at DEFAULT_GRAY
            - Right region varies with strength

        Args:
            strength: Controls color difference (perturbed only)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing region colors and gradient parameters
        """
        self.strength = strength

        # Calculate colors
        left_color, right_color = self._calculate_colors(strength, is_original)

        elements = {
            # Region colors
            'left_color': left_color,
            'right_color': right_color,

            # Gradient parameters
            'gradient_width': self.GRADIENT_WIDTH,
            'gradient_contrast': self.GRADIENT_CONTRAST,
            'reverse_polarity': False,

            # Store for later use
            'half_width': self.width // 2,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Cornsweet illusion on the canvas.

        Drawing order:
        1. Fill left region with uniform color
        2. Fill right region with uniform color
        3. Draw opposing gradients at center boundary

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        left_color = np.array(elements['left_color'])
        right_color = np.array(elements['right_color'])
        half_width = elements['half_width']
        grad_w = int(elements['gradient_width'])
        gradient_contrast = elements['gradient_contrast']
        reverse_polarity = elements.get('reverse_polarity', False)

        # Fill left region with base color
        image[:, :half_width, :] = left_color

        # Fill right region with base color
        image[:, half_width:, :] = right_color

        # Determine gradient direction
        if reverse_polarity:
            left_gradient_modifier = gradient_contrast
            right_gradient_modifier = -gradient_contrast
        else:
            left_gradient_modifier = -gradient_contrast
            right_gradient_modifier = gradient_contrast

        # Create left side gradient (from base color to edge)
        for i in range(grad_w):
            x = half_width - grad_w + i
            if 0 <= x < self.width:
                # Calculate gradient coefficient (0 to 1)
                t = i / (grad_w - 1) if grad_w > 1 else 0
                # Apply gradient
                gradient_value = left_color + left_gradient_modifier * t
                gradient_value = np.clip(gradient_value, 0, 1)
                image[:, x, :] = gradient_value

        # Create right side gradient (from edge to base color)
        for i in range(grad_w):
            x = half_width + i
            if 0 <= x < self.width:
                # Calculate gradient coefficient (1 to 0)
                t = 1 - (i / (grad_w - 1) if grad_w > 1 else 0)
                # Apply gradient
                gradient_value = right_color + right_gradient_modifier * t
                gradient_value = np.clip(gradient_value, 0, 1)
                image[:, x, :] = gradient_value

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add color bar as visual guide.

        The color bar shows a gradient from left color to right color,
        helping to verify whether the regions are actually the same color.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with color bar added
        """
        left_color = elements['left_color']
        right_color = elements['right_color']
        half_width = elements['half_width']

        # Bar dimensions
        bar_width = min(40, self.height // 10)
        bar_height = self.height

        # Position: horizontal bar across center
        bar_y_start = 0
        bar_y_end = bar_height
        bar_x_start = self.width // 4  # 1/4 from left
        bar_x_end = 3 * self.width // 4  # 3/4 from left

        # Start and end positions for the color bar
        start_pos = (bar_x_start, self.height // 2)
        end_pos = (bar_x_end, self.height // 2)

        image = add_color_bar(
            image_numpy=image,
            start_color=left_color,
            end_color=left_color,
            start_pos=start_pos,
            end_pos=end_pos,
            bar_width=bar_width,
            antialiasing=False,
            border_width=0
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by minimizing gradient.

        In the control condition, the gradient is nearly removed,
        making it clear the regions are the same color (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with minimal gradient
        """
        elements['gradient_contrast'] = self.CONTROL_GRADIENT_CONTRAST
        elements['gradient_width'] = self.CONTROL_GRADIENT_WIDTH
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version with different left/right colors.

        The perturbation logic is already handled in define_elements(),
        so this method doesn't need to modify anything.

        Args:
            elements: Elements with perturbation already applied

        Returns:
            Unmodified elements
        """
        # Perturbation logic is already handled in define_elements()
        return elements
