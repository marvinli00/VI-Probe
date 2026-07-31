"""Irradiation Pentagon Illusion (length, VI-Probe case 11). Pentagon version of the Irradiation illusion - light pentagons appear larger than dark pentagons of the same physical size."""

from typing import Any, Dict, Tuple

import numpy as np

from core.draw import add_arrowed_line, add_polygon
from core.template import IllusionTemplate


class IrradiationPentagonIllusion(IllusionTemplate):
    """
    Irradiation Pentagon Illusion Generator

    Generates the pentagon version of the Irradiation illusion with:
    - White small pentagon on black large pentagon (appears larger)
    - Black small pentagon on white large pentagon (appears smaller)
    - Both small pentagons are actually the same size

    The strength parameter controls small pentagon radius via scaling:
    - strength = 0.4: radius = DEFAULT * 0.4
    - strength = 1.0: radius = DEFAULT * 1.0
    - strength = 1.6: radius = DEFAULT * 1.6

    Background pentagons are fixed at 100px radius.

    Pentagon radius calculation:
        small_radius = DEFAULT_SMALL_RADIUS * strength
        background_radius = 100 (fixed)
    """

    def __init__(self, DEFAULT_SMALL_RADIUS=60):
        self.DEFAULT_SMALL_RADIUS = DEFAULT_SMALL_RADIUS  # 60px
        self.BACKGROUND_RADIUS = 100  # Fixed size for background pentagons

        # Color configuration
        self.BLACK = (0, 0, 0)
        self.WHITE = (1, 1, 1)

        # Pentagon configuration
        self.NUM_SIDES = 5
        self.ROTATION_ANGLE = -90  # Top vertex points up

        # Left side configuration (white on black)
        self.LEFT_CENTER_X_RATIO = 1 / 4  # x = WIDTH / 4

        # Right side configuration (black on white)
        self.RIGHT_CENTER_X_RATIO = 3 / 4  # x = 3 * WIDTH / 4

        super().__init__(
            illusion_name="irradiation_pentagon",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_small_radius(self, strength: float) -> int:
        """
        Calculate small pentagon radius from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default radius, 1.5 = 150% of default)

        Returns:
            Small pentagon radius in pixels
        """
        radius = self.DEFAULT_SMALL_RADIUS * strength
        return int(round(radius))

    def _calculate_pentagon_bounds(self, center_x: int, center_y: int, radius: int) -> Tuple[int, int]:
        """
        Calculate top and bottom y-coordinates of a pentagon.

        Uses polar coordinates to find vertices of a regular pentagon with
        rotation_angle=-90 (top vertex points up).

        Args:
            center_x: Pentagon center x coordinate
            center_y: Pentagon center y coordinate
            radius: Pentagon radius

        Returns:
            Tuple of (top_y, bottom_y) - the minimum and maximum y coordinates
        """
        vertices_y = []
        for i in range(self.NUM_SIDES):
            angle = i * (2 * np.pi / self.NUM_SIDES) + np.radians(self.ROTATION_ANGLE)
            vertex_y = center_y - radius * np.sin(angle)
            vertices_y.append(vertex_y)

        return (int(min(vertices_y)), int(max(vertices_y)))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Irradiation Pentagon illusion elements.

        For Original variation:
            - Both small pentagons have the same radius (determined by strength)
        For Perturbed variation:
            - Left small pentagon radius varies with strength
            - Right small pentagon fixed at default radius

        Args:
            strength: Controls small pentagon radius (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing background pentagons and small pentagons
        """
        self.strength = strength

        # Calculate small pentagon radii
        if is_original:
            small_radius = self._calculate_small_radius(strength)
            left_small_radius = small_radius
            right_small_radius = small_radius
        else:
            # Perturbed: right fixed at default, left varies
            left_small_radius = self._calculate_small_radius(strength)
            right_small_radius = self.DEFAULT_SMALL_RADIUS

        # Calculate positions
        center_y = self.height // 2
        left_center_x = int(self.width * self.LEFT_CENTER_X_RATIO)   # 128px
        right_center_x = int(self.width * self.RIGHT_CENTER_X_RATIO) # 384px

        elements = {
            # Left background pentagon (black, fixed radius)
            'pentagon_left_background': {
                'center': (left_center_x, center_y),
                'radius': self.BACKGROUND_RADIUS,
                'color': self.BLACK,
                'num_sides': self.NUM_SIDES,
                'rotation_angle': self.ROTATION_ANGLE,
            },

            # Right background pentagon (white with black border, fixed radius)
            'pentagon_right_background': {
                'center': (right_center_x, center_y),
                'radius': self.BACKGROUND_RADIUS,
                'color': self.WHITE,
                'num_sides': self.NUM_SIDES,
                'rotation_angle': self.ROTATION_ANGLE,
                'border_width': 1,
                'border_color': self.BLACK,
            },

            # Left small pentagon (white)
            'pentagon_left_small': {
                'center': (left_center_x, center_y),
                'radius': left_small_radius,
                'color': self.WHITE,
                'num_sides': self.NUM_SIDES,
                'rotation_angle': self.ROTATION_ANGLE,
            },

            # Right small pentagon (black)
            'pentagon_right_small': {
                'center': (right_center_x, center_y),
                'radius': right_small_radius,
                'color': self.BLACK,
                'num_sides': self.NUM_SIDES,
                'rotation_angle': self.ROTATION_ANGLE,
            },

            # Visual guide lines (calculate from left small pentagon)
            'guide_lines': {},

            # Flag to control whether background pentagons should be drawn
            'draw_backgrounds': True,

            # Store parameters for later use
            'left_small_radius': left_small_radius,
            'right_small_radius': right_small_radius,
            'center_y': center_y,
            'left_center_x': left_center_x,
            'right_center_x': right_center_x,
        }

        # Calculate guide line positions from left small pentagon bounds
        top_y, bottom_y = self._calculate_pentagon_bounds(left_center_x, center_y, left_small_radius)
        elements['guide_lines'] = {
            'top_y': top_y,
            'bottom_y': bottom_y,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Irradiation Pentagon illusion on the canvas.

        Order of drawing:
        1. Background pentagons (if enabled)
        2. Small pentagons

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw background pentagons first (if enabled)
        if elements.get('draw_backgrounds', True):
            # Left background pentagon (black)
            bg_left = elements['pentagon_left_background']
            image = add_polygon(
                image,
                polygon_color=bg_left['color'],
                center=bg_left['center'],
                radius=bg_left['radius'],
                num_sides=bg_left['num_sides'],
                rotation_angle=bg_left['rotation_angle'],
            )

            # Right background pentagon (white with border)
            bg_right = elements['pentagon_right_background']
            image = add_polygon(
                image,
                polygon_color=bg_right['color'],
                center=bg_right['center'],
                radius=bg_right['radius'],
                num_sides=bg_right['num_sides'],
                rotation_angle=bg_right['rotation_angle'],
                border_width=bg_right.get('border_width'),
                border_color=bg_right.get('border_color'),
            )

        # Draw small pentagons on top
        # Left small pentagon (white)
        small_left = elements['pentagon_left_small']
        image = add_polygon(
            image,
            polygon_color=small_left['color'],
            center=small_left['center'],
            radius=small_left['radius'],
            num_sides=small_left['num_sides'],
            rotation_angle=small_left['rotation_angle'],
        )

        # Right small pentagon (black)
        small_right = elements['pentagon_right_small']
        image = add_polygon(
            image,
            polygon_color=small_right['color'],
            center=small_right['center'],
            radius=small_right['radius'],
            num_sides=small_right['num_sides'],
            rotation_angle=small_right['rotation_angle'],
        )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide line positions based on current left small pentagon.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide line positions
        """
        left_center_x = elements['left_center_x']
        center_y = elements['center_y']
        left_radius = elements['left_small_radius']

        # Recalculate pentagon bounds
        top_y, bottom_y = self._calculate_pentagon_bounds(left_center_x, center_y, left_radius)
        elements['guide_lines']['top_y'] = top_y
        elements['guide_lines']['bottom_y'] = bottom_y

        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal guide lines spanning the full width.

        Two dashed horizontal lines are drawn:
        - Top line: At the top vertex of the left small pentagon
        - Bottom line: At the bottom vertex of the left small pentagon

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide lines added
        """
        elements = self.update_visual_guides(elements)

        guide_color = (1, 0, 0)  # Red
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
        Create control condition by removing background pentagons.

        In the control condition, both small pentagons are shown as black on white background,
        making it clear they are the same size (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no background pentagons
        """
        # Disable drawing of background pentagons
        elements['draw_backgrounds'] = False

        # Change left small pentagon to black (instead of white)
        elements['pentagon_left_small']['color'] = self.BLACK

        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by varying only the left small pentagon radius.

        The perturbation logic:
        - Left small pentagon: Radius varies with strength parameter
        - Right small pentagon: Fixed at default radius

        This is already handled in define_elements() when is_original=False,
        so this method doesn't need to modify anything.

        Args:
            elements: Original elements (with right fixed, left variable)

        Returns:
            Unmodified elements (perturbation logic already applied)
        """
        # Perturbation logic is already handled in define_elements()
        # No additional modifications needed
        return elements
