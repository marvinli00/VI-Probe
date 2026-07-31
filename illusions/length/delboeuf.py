"""Delboeuf Illusion (length, VI-Probe case 8).

The Delboeuf illusion demonstrates how surrounding context affects size perception:
two identical inner circles appear to be different sizes depending on the size of
the outer rings.

Classic setup:
- Left circle: Inner circle surrounded by large outer ring (2x radius) → appears smaller
- Right circle: Inner circle surrounded by smaller outer ring (1.5x radius) → appears larger
- Both inner circles are actually the same size

Variations:
- Control: Only inner circles (no outer rings, no illusion)
- Original: Classic Delboeuf with both inner circles varying in size
- Perturbed: Right inner circle varies, left inner circle fixed

Strength levels (0.4 to 1.6): Control inner circle radius via scaling
- strength = 0.4: inner radius = 40% of default (10px)
- strength = 1.0: inner radius = 100% of default (25px)
- strength = 1.6: inner radius = 160% of default (40px)
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_circle
from core.template import IllusionTemplate


class DelboeufIllusion(IllusionTemplate):
    """
    Delboeuf Illusion Generator

    Generates the classic Delboeuf illusion with:
    - Two inner circles that appear different sizes due to outer ring context
    - Left inner circle surrounded by large outer ring (2x radius)
    - Right inner circle surrounded by smaller outer ring (1.5x radius)

    The strength parameter controls inner circle radius via scaling:
    - strength = 0.4: inner_radius = DEFAULT * 0.4
    - strength = 1.0: inner_radius = DEFAULT * 1.0
    - strength = 1.6: inner_radius = DEFAULT * 1.6

    Outer ring sizes maintain proportional relationship to inner circles.

    Circle radius calculation:
        inner_radius = DEFAULT_INNER_RADIUS * strength
        left_outer_radius = inner_radius * 2
        right_outer_radius = inner_radius * 1.5
    """

    def __init__(self, DEFAULT_INNER_RADIUS=25):
        self.DEFAULT_INNER_RADIUS = DEFAULT_INNER_RADIUS  # pixels (strength = 1.0)

        # Circle colors (black on white)
        self.INNER_CIRCLE_COLOR = (0, 0, 0)  # Black filled circles
        self.OUTER_RING_COLOR = (0, 0, 0)    # Black hollow rings

        # Left circle configuration (large outer ring)
        self.LEFT_CENTER_X_RATIO = 1 / 4      # x = WIDTH / 4
        self.LEFT_OUTER_RADIUS_RATIO = 2.0    # Outer ring = 2x inner radius

        # Right circle configuration (smaller outer ring)
        self.RIGHT_CENTER_X_RATIO = 3 / 4     # x = 3 * WIDTH / 4
        self.RIGHT_OUTER_RADIUS_RATIO = 1.3   # Outer ring = 1.5x inner radius

        super().__init__(
            illusion_name="delboeuf",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_inner_radius(self, strength: float) -> int:
        """
        Calculate inner circle radius from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default radius, 1.5 = 150% of default)

        Returns:
            Inner circle radius in pixels
        """
        radius = self.DEFAULT_INNER_RADIUS * strength
        return int(round(radius))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Delboeuf illusion elements.

        For Original variation:
            - Both inner circles have the same radius (determined by strength)
            - Outer rings maintain proportional relationship
        For Perturbed variation:
            - Right inner circle radius varies with strength
            - Left inner circle radius fixed at default

        Args:
            strength: Controls inner circle radius (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing inner circles and outer rings
        """
        self.strength = strength

        # Calculate inner circle radii
        if is_original:
            inner_radius = self._calculate_inner_radius(strength)
            left_inner_radius = inner_radius
            right_inner_radius = inner_radius
        else:
            # Perturbed: left fixed at default, right varies
            left_inner_radius = self.DEFAULT_INNER_RADIUS
            right_inner_radius = self.DEFAULT_INNER_RADIUS

        # Calculate outer ring radii (proportional to inner circles)
        left_outer_radius = int(left_inner_radius * self.LEFT_OUTER_RADIUS_RATIO)
        right_outer_radius = int(right_inner_radius * self.RIGHT_OUTER_RADIUS_RATIO)

        # Circle positions
        left_center_x = int(self.width * self.LEFT_CENTER_X_RATIO)   # 128px
        right_center_x = int(self.width * self.RIGHT_CENTER_X_RATIO) # 384px
        center_y = self.height // 2  # 128px (vertical center)

        elements = {
            # Left inner circle (with large outer ring)
            'circle_left_inner': {
                'center': (left_center_x, center_y),
                'radius': left_inner_radius,
                'color': self.INNER_CIRCLE_COLOR,
            },

            # Left outer ring (hollow)
            'circle_left_outer': {
                'center': (left_center_x, center_y),
                'radius': left_outer_radius,
                'color': self.OUTER_RING_COLOR,
                'hollow': True,
            },

            # Right inner circle (with smaller outer ring)
            'circle_right_inner': {
                'center': (right_center_x, center_y),
                'radius': right_inner_radius,
                'color': self.INNER_CIRCLE_COLOR,
            },

            # Right outer ring (hollow)
            'circle_right_outer': {
                'center': (right_center_x, center_y),
                'radius': right_outer_radius,
                'color': self.OUTER_RING_COLOR,
                'hollow': True,
            },

            # Visual guide lines (horizontal lines at top and bottom of left inner circle)
            'guide_lines': {
                'top_y': center_y - left_inner_radius,
                'bottom_y': center_y + left_inner_radius,
            },

            # Flag to control whether outer rings should be drawn
            'draw_outer_rings': True,

            # Store parameters for later use
            'left_inner_radius': left_inner_radius,
            'right_inner_radius': right_inner_radius,
            'center_y': center_y,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Delboeuf illusion on the canvas.

        Order of drawing:
        1. Left outer ring (if enabled)
        2. Right outer ring (if enabled)
        3. Left inner circle
        4. Right inner circle

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw outer rings first (if enabled)
        if elements.get('draw_outer_rings', True):
            # Draw left outer ring (hollow)
            image = add_circle(
                image,
                circle_color=elements['circle_left_outer']['color'],
                circle_center=elements['circle_left_outer']['center'],
                circle_radius=elements['circle_left_outer']['radius'],
                hollow=True,
            )

            # Draw right outer ring (hollow)
            image = add_circle(
                image,
                circle_color=elements['circle_right_outer']['color'],
                circle_center=elements['circle_right_outer']['center'],
                circle_radius=elements['circle_right_outer']['radius'],
                hollow=True,
            )

        # Draw inner circles on top
        # Left inner circle
        image = add_circle(
            image,
            circle_color=elements['circle_left_inner']['color'],
            circle_center=elements['circle_left_inner']['center'],
            circle_radius=elements['circle_left_inner']['radius'],
        )

        # Right inner circle
        image = add_circle(
            image,
            circle_color=elements['circle_right_inner']['color'],
            circle_center=elements['circle_right_inner']['center'],
            circle_radius=elements['circle_right_inner']['radius'],
        )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide line positions based on current left inner circle.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide line positions
        """
        center_y = elements['center_y']
        left_radius = elements['left_inner_radius']

        elements['guide_lines']['top_y'] = center_y - left_radius
        elements['guide_lines']['bottom_y'] = center_y + left_radius

        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal guide lines spanning the full width.

        Two dashed horizontal lines are drawn:
        - Top line: At the top edge of the left inner circle
        - Bottom line: At the bottom edge of the left inner circle

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide lines added
        """
        elements = self.update_visual_guides(elements)

        guide_color = (0.5, 0.5, 0.5)  # Gray
        guide_width = 1

        # Top horizontal guide line
        image = add_arrowed_line(
            image,
            line_color=guide_color,
            start_point=(0, elements['guide_lines']['top_y']),
            end_point=(self.width, elements['guide_lines']['top_y']),
            line_width=guide_width,
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
            dashed=True,
        )

        # Bottom horizontal guide line
        image = add_arrowed_line(
            image,
            line_color=guide_color,
            start_point=(0, elements['guide_lines']['bottom_y']),
            end_point=(self.width, elements['guide_lines']['bottom_y']),
            line_width=guide_width,
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
            dashed=True,
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing outer rings.

        In the control condition, only the two inner circles are shown,
        making it clear they are the same size (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no outer rings
        """
        # Disable drawing of outer rings
        elements['draw_outer_rings'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by varying only the right inner circle.

        The perturbation logic:
        - Left inner circle: Fixed at default radius
        - Right inner circle: Radius varies with strength parameter

        This is opposite to Ebbinghaus (which varies left, fixes right).

        Args:
            elements: Original elements (with both circles at default radius)

        Returns:
            Modified elements with right circle variable, left circle fixed
        """
        # Calculate new radius for right inner circle
        new_right_radius = self._calculate_inner_radius(self.strength)

        # Update right inner circle radius
        elements['circle_right_inner']['radius'] = new_right_radius
        elements['right_inner_radius'] = new_right_radius

        # Update right outer ring radius (maintain proportional relationship)
        new_right_outer_radius = int(new_right_radius * self.RIGHT_OUTER_RADIUS_RATIO)
        elements['circle_right_outer']['radius'] = new_right_outer_radius

        # Left inner circle and outer ring keep the default radius (no modification needed)

        return elements
