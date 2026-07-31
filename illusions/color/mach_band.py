"""Mach Band Illusion (color, VI-Probe case 16).

The Mach Band illusion is a visual phenomenon where perceived brightness/color bands
appear at the boundaries between gradually changing shades, even though no such bands
exist in the actual stimulus.

Classic setup:
- Series of vertical stripes with gradually changing colors (black → green)
- Each stripe has uniform color internally
- At boundaries, viewers perceive exaggerated "bright bands" and "dark bands"
- This is due to lateral inhibition in the visual system

Variations:
- Control: Add gaps between stripes to eliminate the illusion
- Original: Smooth gradient stripes without borders
- Perturbed: Add semi-transparent white borders to modify the illusion effect

Strength system:
- Controls border width, transparency, or both (configurable)
- Allows studying how border properties affect the Mach Band illusion
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_rectangle, calculate_perceptual_gradient_lab
from core.template import IllusionTemplate


class MachBandIllusion(IllusionTemplate):
    """
    Mach Band Illusion Generator

    Generates the Mach Band illusion with:
    - Vertical stripes with LAB perceptual gradient (black → green)
    - Optional semi-transparent borders (perturbed variation)
    - Configurable border control mode (width, alpha, or both)

    Strength parameter controls border properties based on mode:
    - 'border_width': border_width = DEFAULT_BORDER_WIDTH × strength
    - 'border_alpha': border_alpha = DEFAULT_BORDER_ALPHA × strength
    - 'both': both properties scale with strength
    """

    def __init__(self,
                 start_color=(0, 0, 0),  # Black
                 end_color=(0, 1, 0),  # Green
                 num_stripes=16,
                 border_control_mode='border_width',  # 'border_width', 'border_alpha', or 'both'
                 default_border_width=3,
                 default_border_alpha=0.1,
                 border_color=(1, 1, 1),
                 ):
        """
        Initialize Mach Band Illusion generator.

        Args:
            start_color: Starting color of gradient (default: black)
            end_color: Ending color of gradient (default: green)
            num_stripes: Number of vertical stripes (default: 16)
            border_control_mode: What strength controls ('border_width', 'border_alpha', 'both')
            default_border_width: Base border width in pixels (default: 3)
            default_border_alpha: Base border transparency (default: 0.1)
        """
        self.start_color = start_color
        self.end_color = end_color
        self.num_stripes = num_stripes
        self.border_control_mode = border_control_mode
        self.default_border_width = default_border_width
        self.default_border_alpha = default_border_alpha

        # Control modification
        self.stripes_offset = 2  # Gaps between stripes in control condition

        # Border configuration
        self.border_color = border_color  # White

        super().__init__(
            illusion_name="mach_band",
            width=512,
            height=256,
            strength_levels=[0.5, 0.75, 1.0, 1.25, 1.5],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Mach Band illusion elements.

        For Original variation:
            - No borders (border_width=0)
        For Perturbed variation:
            - Borders controlled by strength

        Args:
            strength: Controls border properties
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing stripe and border parameters
        """
        self.strength = strength

        # Generate perceptually uniform gradient colors using LAB color space
        stripe_colors = calculate_perceptual_gradient_lab(
            self.start_color,
            self.end_color,
            self.num_stripes# + 1
        )

        # Calculate stripe dimensions
        stripe_width = self.width // self.num_stripes

        # Calculate border properties based on variation and strength
        if is_original:
            # Original: no borders
            border_width = 0
            border_alpha = 0
        else:
            # Perturbed: borders controlled by strength
            if self.border_control_mode == 'border_width':
                border_width = self.default_border_width * strength
                border_alpha = self.default_border_alpha
            elif self.border_control_mode == 'border_alpha':
                border_width = self.default_border_width
                border_alpha = self.default_border_alpha * strength
            else:  # 'both'
                border_width = self.default_border_width * strength
                border_alpha = self.default_border_alpha * strength

        elements = {
            # Stripe parameters
            'stripe_colors': stripe_colors,
            'stripe_width': stripe_width,
            'border_width': border_width,
            'border_alpha': border_alpha,
            'border_color': self.border_color,

            # Control flag
            'stripes_offset': 0,  # Control will set this to self.stripes_offset
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Mach Band illusion on the canvas.

        Draws vertical stripes with gradually changing colors from black to green,
        optionally with semi-transparent borders.

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        stripe_colors = elements['stripe_colors']
        stripe_width = elements['stripe_width']
        border_width = elements['border_width']
        border_alpha = elements['border_alpha']
        border_color = elements['border_color']
        stripes_offset = elements['stripes_offset']

        # Draw each stripe
        for i in range(self.num_stripes):
            # Calculate stripe position
            stripe_start_x = i * stripe_width
            rect_center_x = stripe_start_x + stripe_width // 2
            rect_center_y = self.height // 2

            # Calculate stripe width (with offset for control condition)
            actual_stripe_width = stripe_width - stripes_offset

            # Draw stripe
            image = add_rectangle(
                image,
                rect_color=stripe_colors[i],
                rect_center=(rect_center_x, rect_center_y),
                rect_width=actual_stripe_width,
                rect_height=self.height,
                antialias=False,  # Sharp edges for Mach Band effect
                border_width=int(border_width),
                border_color=border_color,
                border_alpha=border_alpha
            )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal gradient color bar at the top as visual guide.

        Shows the complete gradient from start_color to end_color using LAB interpolation,
        helping viewers understand the actual smooth gradient.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with gradient bar added at top
        """
        # Generate full gradient for visual guide
        gradient_bar_height = 30
        gradient = calculate_perceptual_gradient_lab(
            self.start_color,
            self.end_color,
            self.width
        )

        # Add gradient bar at the top
        # gradient is shape (width, 3), we need (height, width, 3)
        gradient_bar = np.tile(gradient[np.newaxis, :, :], (gradient_bar_height, 1, 1))

        # Overlay at top of image
        image[0:gradient_bar_height, :, :] = gradient_bar

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by adding gaps between stripes.

        The gaps eliminate the Mach Band illusion by removing direct adjacency
        between different shades.

        Args:
            elements: Original elements

        Returns:
            Modified elements with stripe gaps
        """
        elements['stripes_offset'] = self.stripes_offset
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version with borders.

        The perturbation logic is already handled in define_elements(),
        so this method doesn't need to modify anything.

        Args:
            elements: Elements with perturbation already applied

        Returns:
            Unmodified elements
        """
        # Perturbation logic is already handled in define_elements()
        return elements
