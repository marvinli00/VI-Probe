"""Ebbinghaus Illusion (length, VI-Probe case 6). Two identical central circles appear different sizes depending on the size of the surrounding circles (Titchener Circles)."""

from typing import Any, Dict, List, Tuple

import numpy as np

from core.draw import add_arrowed_line, add_circle
from core.template import IllusionTemplate


class EbbinghausIllusion(IllusionTemplate):
    """
    Ebbinghaus Illusion Generator

    Generates the classic Ebbinghaus (Titchener Circles) illusion with:
    - Two central circles that appear different sizes due to context
    - Left circle surrounded by small circles
    - Right circle surrounded by large circles

    The strength parameter controls central circle radius via scaling:
    - strength = 0.4: central_radius = DEFAULT * 0.4
    - strength = 1.0: central_radius = DEFAULT * 1.0
    - strength = 1.6: central_radius = DEFAULT * 1.6

    Surrounding circle sizes are fixed and do not change with strength.

    Circle radius calculation:
        central_radius = DEFAULT_CENTER_RADIUS * strength
    """

    def __init__(self, DEFAULT_CENTER_RADIUS=25):
        self.DEFAULT_CENTER_RADIUS = DEFAULT_CENTER_RADIUS  # pixels (strength = 1.0)

        # Circle colors
        self.CENTER_CIRCLE_COLOR = (0.9, 0.5, 0.22)      # Orange
        self.SURROUNDING_CIRCLE_COLOR = (0.57, 0.64, 0.72)  # Blue-gray

        # Left circle configuration (surrounded by small circles)
        self.LEFT_CENTER_X_RATIO = 1 / 4      # x = WIDTH / 4
        self.LEFT_SMALL_CIRCLE_RADIUS = DEFAULT_CENTER_RADIUS / 2  # 12.5px
        self.LEFT_SMALL_CIRCLE_COUNT = 8

        # Right circle configuration (surrounded by large circles)
        self.RIGHT_CENTER_X_RATIO = 3 / 4     # x = 3 * WIDTH / 4
        self.RIGHT_LARGE_CIRCLE_RADIUS = DEFAULT_CENTER_RADIUS * 1.3  # 32.5px
        self.RIGHT_LARGE_CIRCLE_COUNT = 6

        # Distance multiplier for surrounding circles
        self.SURROUNDING_DISTANCE_FACTOR = 1.3  # Multiplier for spacing

        super().__init__(
            illusion_name="ebbinghaus",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_center_radius(self, strength: float) -> int:
        """
        Calculate central circle radius from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default radius, 1.5 = 150% of default)

        Returns:
            Central circle radius in pixels
        """
        radius = self.DEFAULT_CENTER_RADIUS * strength
        return int(round(radius))

    def _calculate_surrounding_positions(self, center_x: int, center_y: int,
                                        center_radius: int, surrounding_radius: int,
                                        num_circles: int) -> List[Tuple[int, int]]:
        """
        Calculate positions for surrounding circles arranged in a circle.

        Args:
            center_x: Central circle x coordinate
            center_y: Central circle y coordinate
            center_radius: Central circle radius
            surrounding_radius: Surrounding circle radius
            num_circles: Number of surrounding circles

        Returns:
            List of (x, y) positions for surrounding circles
        """
        positions = []
        distance = self.SURROUNDING_DISTANCE_FACTOR * (center_radius + surrounding_radius)

        for i in range(num_circles):
            angle = 2 * np.pi / num_circles * i
            x = int(center_x + distance * np.cos(angle))
            y = int(center_y + distance * np.sin(angle))
            positions.append((x, y))

        return positions

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Ebbinghaus illusion elements.

        For Original variation:
            - Both central circles have the same radius (determined by strength)
        For Perturbed variation:
            - Left central circle radius varies with strength
            - Right central circle radius fixed at default

        Args:
            strength: Controls central circle radius (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing central circles and surrounding circles
        """
        self.strength = strength

        # Calculate central circle radius
        if is_original:
            center_radius = self._calculate_center_radius(strength)
            left_center_radius = center_radius
            right_center_radius = center_radius
        else:
            # Perturbed: use default radius initially
            left_center_radius = self.DEFAULT_CENTER_RADIUS
            right_center_radius = self.DEFAULT_CENTER_RADIUS

        # Central circle positions
        left_center_x = int(self.width * self.LEFT_CENTER_X_RATIO)   # 128px
        right_center_x = int(self.width * self.RIGHT_CENTER_X_RATIO) # 384px
        center_y = self.height // 2  # 128px (vertical center)

        # Calculate surrounding circle positions
        left_surrounding_positions = self._calculate_surrounding_positions(
            left_center_x, center_y,
            left_center_radius,
            self.LEFT_SMALL_CIRCLE_RADIUS,
            self.LEFT_SMALL_CIRCLE_COUNT
        )

        right_surrounding_positions = self._calculate_surrounding_positions(
            right_center_x, center_y,
            right_center_radius,
            self.RIGHT_LARGE_CIRCLE_RADIUS,
            self.RIGHT_LARGE_CIRCLE_COUNT
        )

        elements = {
            # Left central circle (surrounded by small circles)
            'circle_left_center': {
                'center': (left_center_x, center_y),
                'radius': left_center_radius,
                'color': self.CENTER_CIRCLE_COLOR,
            },

            # Left surrounding small circles
            'circle_left_surrounding': {
                'positions': left_surrounding_positions,
                'radius': self.LEFT_SMALL_CIRCLE_RADIUS,
                'color': self.SURROUNDING_CIRCLE_COLOR,
            },

            # Right central circle (surrounded by large circles)
            'circle_right_center': {
                'center': (right_center_x, center_y),
                'radius': right_center_radius,
                'color': self.CENTER_CIRCLE_COLOR,
            },

            # Right surrounding large circles
            'circle_right_surrounding': {
                'positions': right_surrounding_positions,
                'radius': self.RIGHT_LARGE_CIRCLE_RADIUS,
                'color': self.SURROUNDING_CIRCLE_COLOR,
            },

            # Visual guide lines (horizontal lines at top and bottom of left circle)
            'guide_lines': {
                'top_y': center_y - left_center_radius,
                'bottom_y': center_y + left_center_radius,
            },

            # Flag to control whether surrounding circles should be drawn
            'draw_surrounding_circles': True,

            # Store parameters for later use
            'left_center_radius': left_center_radius,
            'right_center_radius': right_center_radius,
            'center_y': center_y,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Ebbinghaus illusion on the canvas.

        Order of drawing:
        1. Left surrounding circles (if enabled)
        2. Right surrounding circles (if enabled)
        3. Left central circle
        4. Right central circle

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw surrounding circles first (so central circles appear on top)
        if elements.get('draw_surrounding_circles', True):
            # Draw left surrounding small circles
            for pos in elements['circle_left_surrounding']['positions']:
                image = add_circle(
                    image,
                    circle_color=elements['circle_left_surrounding']['color'],
                    circle_center=pos,
                    circle_radius=elements['circle_left_surrounding']['radius'],
                )

            # Draw right surrounding large circles
            for pos in elements['circle_right_surrounding']['positions']:
                image = add_circle(
                    image,
                    circle_color=elements['circle_right_surrounding']['color'],
                    circle_center=pos,
                    circle_radius=elements['circle_right_surrounding']['radius'],
                )

        # Draw central circles on top
        # Left central circle
        image = add_circle(
            image,
            circle_color=elements['circle_left_center']['color'],
            circle_center=elements['circle_left_center']['center'],
            circle_radius=elements['circle_left_center']['radius'],
        )

        # Right central circle
        image = add_circle(
            image,
            circle_color=elements['circle_right_center']['color'],
            circle_center=elements['circle_right_center']['center'],
            circle_radius=elements['circle_right_center']['radius'],
        )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide line positions based on current left central circle.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide line positions
        """
        center_y = elements['center_y']
        left_radius = elements['left_center_radius']

        elements['guide_lines']['top_y'] = center_y - left_radius
        elements['guide_lines']['bottom_y'] = center_y + left_radius

        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal guide lines spanning the full width.

        Two dashed horizontal lines are drawn:
        - Top line: At the top edge of the left central circle
        - Bottom line: At the bottom edge of the left central circle

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
        Create control condition by removing surrounding circles.

        In the control condition, only the two central circles are shown,
        making it clear they are the same size (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no surrounding circles
        """
        # Disable drawing of surrounding circles
        elements['draw_surrounding_circles'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by varying only the left central circle.

        The perturbation logic:
        - Left central circle: Radius varies with strength parameter
        - Right central circle: Fixed at default radius

        This tests whether the illusion persists with different actual sizes.

        Args:
            elements: Original elements (with both circles at default radius)

        Returns:
            Modified elements with left circle variable, right circle fixed
        """
        # Calculate new radius for left central circle
        new_left_radius = self._calculate_center_radius(self.strength)

        # Update left central circle radius
        elements['circle_left_center']['radius'] = new_left_radius
        elements['left_center_radius'] = new_left_radius

        # Recalculate left surrounding circle positions
        left_center_x, left_center_y = elements['circle_left_center']['center']
        left_surrounding_positions = self._calculate_surrounding_positions(
            left_center_x, left_center_y,
            new_left_radius,
            self.LEFT_SMALL_CIRCLE_RADIUS,
            self.LEFT_SMALL_CIRCLE_COUNT
        )
        elements['circle_left_surrounding']['positions'] = left_surrounding_positions

        # Right central circle keeps the default radius (no modification needed)

        return elements
