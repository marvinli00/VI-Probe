"""Circle Ponzo Illusion (length, VI-Probe case 12).

Circle version of the Ponzo illusion - two equal-sized circles appear different
sizes due to converging lines creating depth cues.

Classic setup:
- Two converging lines creating perspective (vanishing point beyond right edge)
- Left circle: At wide end (appears smaller)
- Right circle: At narrow end (appears larger)
- Both circles are actually the same size

Variations:
- Control: Remove converging lines (no illusion, circles appear equal)
- Original: Classic Circle Ponzo with both circles varying equally
- Perturbed: Right circle size varies, left circle fixed

Strength levels (0.4 to 1.6): Control circle radius via scaling
- strength = 0.4: radius = 40% of default (16px)
- strength = 1.0: radius = 100% of default (40px)
- strength = 1.6: radius = 160% of default (64px)
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_circle
from core.template import IllusionTemplate


class CirclePonzoIllusion(IllusionTemplate):
    """
    Circle Ponzo Illusion Generator

    Generates the circle version of the Ponzo illusion with:
    - Two circles between converging lines
    - Left circle at wide end (appears smaller)
    - Right circle at narrow end (appears larger)
    - Both circles are actually the same size

    The strength parameter controls circle radius via scaling:
    - strength = 0.4: radius = DEFAULT * 0.4
    - strength = 1.0: radius = DEFAULT * 1.0
    - strength = 1.6: radius = DEFAULT * 1.6

    Circle radius calculation:
        radius = DEFAULT_CIRCLE_RADIUS * strength
    """

    def __init__(self, DEFAULT_CIRCLE_RADIUS=40):
        self.DEFAULT_CIRCLE_RADIUS = DEFAULT_CIRCLE_RADIUS  # 40px

        # Color configuration
        self.BLACK = (0, 0, 0)
        self.WHITE = (1, 1, 1)

        # Converging lines configuration
        self.VANISH_POINT_OFFSET = 100  # Beyond right edge
        self.TOP_LINE_START = (50, 30)
        self.BOTTOM_LINE_START = (50, None)  # HEIGHT - 30, calculated in __init__
        self.LINE_COLOR = self.BLACK
        self.LINE_WIDTH = 2

        # Circle positions
        self.LEFT_CIRCLE_X_RATIO = 1 / 3   # x = WIDTH / 3
        self.RIGHT_CIRCLE_X_RATIO = 2 / 3  # x = WIDTH * 2 / 3

        super().__init__(
            illusion_name="circle_ponzo",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

        # Update bottom line start y after height is set
        self.BOTTOM_LINE_START = (50, self.height - 30)

    def _calculate_circle_radius(self, strength: float) -> int:
        """
        Calculate circle radius from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default radius, 1.5 = 150% of default)

        Returns:
            Circle radius in pixels
        """
        radius = self.DEFAULT_CIRCLE_RADIUS * strength
        return int(round(radius))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Circle Ponzo illusion elements.

        For Original variation:
            - Both circles have the same radius (determined by strength)
        For Perturbed variation:
            - Left circle fixed at default radius
            - Right circle radius varies with strength

        Args:
            strength: Controls circle radius (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing converging lines and circles
        """
        self.strength = strength

        # Calculate circle radii
        if is_original:
            circle_radius = self._calculate_circle_radius(strength)
            left_circle_radius = circle_radius
            right_circle_radius = circle_radius
        else:
            # Perturbed: left fixed at default, right varies
            left_circle_radius = self.DEFAULT_CIRCLE_RADIUS
            right_circle_radius = self._calculate_circle_radius(strength)

        # Calculate positions
        center_y = self.height // 2
        left_circle_x = int(self.width * self.LEFT_CIRCLE_X_RATIO)   # WIDTH // 3
        right_circle_x = int(self.width * self.RIGHT_CIRCLE_X_RATIO) # WIDTH * 2 // 3

        # Vanishing point (beyond right edge)
        vanish_x = self.width + self.VANISH_POINT_OFFSET
        vanish_y = center_y

        elements = {
            # Top converging line
            'line_top': {
                'start': self.TOP_LINE_START,
                'end': (vanish_x, vanish_y),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            },

            # Bottom converging line
            'line_bottom': {
                'start': self.BOTTOM_LINE_START,
                'end': (vanish_x, vanish_y),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            },

            # Left circle
            'circle_left': {
                'center': (left_circle_x, center_y),
                'radius': left_circle_radius,
                'color': self.BLACK,
            },

            # Right circle
            'circle_right': {
                'center': (right_circle_x, center_y),
                'radius': right_circle_radius,
                'color': self.BLACK,
            },

            # Visual guide lines (aligned with right circle)
            'guide_lines': {
                'top_y': center_y - right_circle_radius,
                'bottom_y': center_y + right_circle_radius,
            },

            # Flag to control whether converging lines should be drawn
            'draw_converging_lines': True,

            # Store parameters for later use
            'left_circle_radius': left_circle_radius,
            'right_circle_radius': right_circle_radius,
            'center_y': center_y,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Circle Ponzo illusion on the canvas.

        Order of drawing:
        1. Converging lines (if enabled)
        2. Circles

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw converging lines first (if enabled)
        if elements.get('draw_converging_lines', True):
            # Top converging line
            line_top = elements['line_top']
            image = add_arrowed_line(
                image,
                line_color=line_top['color'],
                start_point=line_top['start'],
                end_point=line_top['end'],
                line_width=line_top['width'],
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
            )

            # Bottom converging line
            line_bottom = elements['line_bottom']
            image = add_arrowed_line(
                image,
                line_color=line_bottom['color'],
                start_point=line_bottom['start'],
                end_point=line_bottom['end'],
                line_width=line_bottom['width'],
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
            )

        # Draw circles
        # Left circle
        circle_left = elements['circle_left']
        image = add_circle(
            image,
            circle_color=circle_left['color'],
            circle_center=circle_left['center'],
            circle_radius=circle_left['radius'],
        )

        # Right circle
        circle_right = elements['circle_right']
        image = add_circle(
            image,
            circle_color=circle_right['color'],
            circle_center=circle_right['center'],
            circle_radius=circle_right['radius'],
        )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide line positions based on current right circle.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide line positions
        """
        center_y = elements['center_y']
        right_radius = elements['right_circle_radius']

        elements['guide_lines']['top_y'] = center_y - right_radius
        elements['guide_lines']['bottom_y'] = center_y + right_radius

        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal guide lines spanning the full width.

        Two dashed horizontal lines are drawn:
        - Top line: At the top edge of the right circle
        - Bottom line: At the bottom edge of the right circle

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
        Create control condition by removing converging lines.

        In the control condition, only the two circles are shown,
        making it clear they are the same size (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no converging lines
        """
        # Disable drawing of converging lines
        elements['draw_converging_lines'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by varying only the right circle radius.

        The perturbation logic:
        - Left circle: Fixed at default radius
        - Right circle: Radius varies with strength parameter

        This is already handled in define_elements() when is_original=False,
        so this method doesn't need to modify anything.

        Args:
            elements: Original elements (with left fixed, right variable)

        Returns:
            Unmodified elements (perturbation logic already applied)
        """
        # Perturbation logic is already handled in define_elements()
        # No additional modifications needed
        return elements
