"""Ehrenstein Illusion (orientation, VI-Probe case 29).

Radial lines emanating from a central point make the perfectly straight
edges of two squares appear to curve inward.
"""

from typing import Any, Dict, Tuple

import numpy as np

from core.draw import add_arrowed_line, add_curved_line
from core.template import IllusionTemplate


class EhrensteinIllusion(IllusionTemplate):
    """
    Ehrenstein Illusion Generator

    Generates the Ehrenstein illusion using radial lines that make straight
    edges appear to curve inward.

    The strength parameter controls radial line length:
    - strength = 0.5: Short lines (weak illusion)
    - strength = 1.0: Standard lines (strong illusion)
    - strength = 1.5: Long lines (very strong illusion)
    """

    def __init__(self, NUM_LINES = 24):
        # Image dimensions
        WIDTH = 512
        HEIGHT = 512

        # Radial lines configuration
        self.NUM_LINES = NUM_LINES  # Number of radial lines (every 15 degrees)
        self.BASE_LINE_LENGTH = 180  # Base length of radial lines
        self.LINE_WIDTH = 2  # Width of radial lines
        self.LINE_COLOR = (0.6, 0.6, 0.6)  # Gray color for radial lines

        # Left square configuration
        self.SQUARE_SIZE = 80  # Side length of square
        self.SQUARE_OFFSET_X = -80  # Offset from center (left side)
        self.SQUARE_LINE_WIDTH = 3
        self.SQUARE_COLOR = (0, 0, 0)  # Black

        # Right square configuration
        self.SQUARE_RIGHT_SIZE = 80  # Side length of right square (same as left)
        self.SQUARE_RIGHT_OFFSET_X = 80  # Offset from center (right side)
        self.SQUARE_RIGHT_LINE_WIDTH = 3
        self.SQUARE_RIGHT_COLOR = (0, 0, 0)  # Black

        super().__init__(
            illusion_name="ehrenstein_illusion",
            width=WIDTH,
            height=HEIGHT,
            strength_levels=[0.5, 0.8, 1.0, 1.2, 1.5],  # Line length multipliers
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Ehrenstein illusion elements.

        Args:
            strength:
                - Original mode: Controls radial line count (0.5=12, 1.0=24, 1.5=36)
                - Perturbed mode: Controls edge curvature depth in pixels
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing radial lines and shapes
        """
        self.strength = strength

        # Center position
        center_x = self.width // 2
        center_y = self.height // 2

        # Determine number of radial lines and curvature based on mode
        if is_original:
            # Original mode: strength controls line count
            num_lines = self.NUM_LINES# int(12 + strength * 12)  # 12-36 lines
            curvature = 0  # No curvature in original mode
        else:
            # Perturbed mode: fixed line count, strength controls curvature
            num_lines = self.NUM_LINES  # Fixed 24 lines
            # Curvature formula: (strength - 1.0) * 30
            # strength = 0.5 → -15px (inward/concave)
            # strength = 1.0 → 0px (straight)
            # strength = 1.5 → +15px (outward/convex)
            curvature = (strength - 1.0) * 30

        # Fixed radial line length
        line_length = self.BASE_LINE_LENGTH

        # Generate radial lines (evenly distributed around 360°)
        radial_lines = []
        for i in range(num_lines):
            angle = (360 / num_lines) * i  # Degrees
            angle_rad = np.radians(angle)

            # Calculate line endpoints (from center outward)
            end_x = center_x + line_length * np.cos(angle_rad)
            end_y = center_y + line_length * np.sin(angle_rad)

            radial_lines.append({
                'start': (center_x, center_y),
                'end': (int(end_x), int(end_y)),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            })

        # Left square configuration
        square_center_x = center_x + self.SQUARE_OFFSET_X
        square_center_y = center_y

        # Right square configuration
        square_right_center_x = center_x + self.SQUARE_RIGHT_OFFSET_X
        square_right_center_y = center_y

        elements = {
            'radial_lines': radial_lines,
            'square': {
                'center': (square_center_x, square_center_y),
                'size': self.SQUARE_SIZE,
                'color': self.SQUARE_COLOR,
                'width': self.SQUARE_LINE_WIDTH,
                'is_curved': False,  # Will be set to True in perturbation
                'curvature': curvature,  # Inward curve depth (pixels)
            },
            'square_right': {
                'center': (square_right_center_x, square_right_center_y),
                'size': self.SQUARE_RIGHT_SIZE,
                'color': self.SQUARE_RIGHT_COLOR,
                'width': self.SQUARE_RIGHT_LINE_WIDTH,
                'is_curved': False,  # Will be set to True in perturbation
                'curvature': curvature,  # Inward curve depth (pixels)
            },
            'draw_radial_lines': True,  # Flag to control radial line drawing
            'center_x': center_x,
            'center_y': center_y,
            'line_length': line_length,
            'num_lines': num_lines,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Ehrenstein illusion on the canvas.

        Order of drawing:
        1. Radial lines (if enabled)
        2. Square (hollow, only border)
        3. Circle (hollow, only border)

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw radial lines first (so shapes are on top)
        if elements.get('draw_radial_lines', True):
            for line in elements['radial_lines']:
                image = add_arrowed_line(
                    image,
                    line_color=line['color'],
                    start_point=line['start'],
                    end_point=line['end'],
                    line_width=line['width'],
                    arrow_start='none',
                    arrow_end='none',
                    antialias=True,
                )

        # Draw left square (hollow - only border, straight or curved)
        square = elements['square']
        image = self._draw_square_border(
            image,
            center=square['center'],
            size=square['size'],
            color=square['color'],
            line_width=square['width'],
            is_curved=square.get('is_curved', False),
            curvature=square.get('curvature', 0)
        )

        # Draw right square (hollow - only border, straight or curved)
        square_right = elements['square_right']
        image = self._draw_square_border(
            image,
            center=square_right['center'],
            size=square_right['size'],
            color=square_right['color'],
            line_width=square_right['width'],
            is_curved=square_right.get('is_curved', False),
            curvature=square_right.get('curvature', 0)
        )

        return image

    def _draw_square_border(self, image: np.ndarray,
                           center: Tuple[int, int],
                           size: int,
                           color: Tuple[float, float, float],
                           line_width: int,
                           is_curved: bool = False,
                           curvature: float = 0) -> np.ndarray:
        """
        Draw a square border (hollow square), straight or curved.

        Args:
            image: Current image
            center: Center position (x, y)
            size: Side length of square
            color: Line color
            line_width: Border width
            is_curved: Whether to draw curved edges (inward concave)
            curvature: Depth of inward curve in pixels (for Ehrenstein illusion)

        Returns:
            Image with square border drawn
        """
        cx, cy = center
        half_size = size // 2

        # Calculate corner positions
        top_left = (cx - half_size, cy - half_size)
        top_right = (cx + half_size, cy - half_size)
        bottom_left = (cx - half_size, cy + half_size)
        bottom_right = (cx + half_size, cy + half_size)

        # Define four edges
        edges = [
            (top_left, top_right),      # Top edge (horizontal)
            (top_right, bottom_right),  # Right edge (vertical)
            (bottom_right, bottom_left),# Bottom edge (horizontal)
            (bottom_left, top_left),    # Left edge (vertical)
        ]

        # Draw each edge (straight or curved)
        for i, (start, end) in enumerate(edges):
            if not is_curved or curvature == 0:
                # Draw straight edge
                image = add_arrowed_line(
                    image,
                    line_color=color,
                    start_point=start,
                    end_point=end,
                    line_width=line_width,
                    arrow_start='none',
                    arrow_end='none',
                    antialias=True,
                )
            else:
                # Draw curved edge (inward concave curve)
                # Horizontal edges (top, bottom) curve inward vertically
                # Vertical edges (left, right) curve inward horizontally
                is_horizontal = (i == 0 or i == 2)  # Top or bottom edge
                image = self._draw_curved_edge(
                    image,
                    start=start,
                    end=end,
                    color=color,
                    line_width=line_width,
                    curvature=curvature,
                    is_horizontal=is_horizontal,
                    center=center
                )

        return image

    def _draw_curved_edge(self, image: np.ndarray,
                         start: Tuple[int, int],
                         end: Tuple[int, int],
                         color: Tuple[float, float, float],
                         line_width: int,
                         curvature: float,
                         is_horizontal: bool,
                         center: Tuple[int, int]) -> np.ndarray:
        """
        Draw a curved edge for the square (parabolic inward curve).

        Similar to Hering illusion curved lines.

        Args:
            image: Current image
            start: Starting point
            end: Ending point
            color: Line color
            line_width: Line width
            curvature: Depth of curve in pixels
            is_horizontal: Whether this is a horizontal edge
            center: Square center (to determine inward direction)

        Returns:
            Image with curved edge drawn
        """
        # Generate smooth curve points
        num_points = 200
        points = []

        if is_horizontal:
            # Horizontal edge: interpolate x, curve y inward
            x_start, y_start = start
            x_end, _ = end
            x_values = np.linspace(x_start, x_end, num_points)

            # Determine curve direction (toward center for positive curvature)
            # If edge is above center, curve downward (positive)
            # If edge is below center, curve upward (negative)
            curve_direction = 1 if y_start < center[1] else -1

            # Support negative curvature (curves outward/convex)
            curve_sign = 1 if curvature >= 0 else -1
            abs_curvature = abs(curvature)

            for x in x_values:
                # Parabolic curve: maximum at center, 0 at ends
                t = (x - x_start) / (x_end - x_start)
                offset = abs_curvature * (1 - (2*t - 1)**2)
                y = y_start + curve_direction * curve_sign * offset
                points.append((x, y))
        else:
            # Vertical edge: interpolate y, curve x inward
            x_start, y_start = start
            _, y_end = end
            y_values = np.linspace(y_start, y_end, num_points)

            # Determine curve direction (toward center for positive curvature)
            # If edge is left of center, curve rightward (positive)
            # If edge is right of center, curve leftward (negative)
            curve_direction = 1 if x_start < center[0] else -1

            # Support negative curvature (curves outward/convex)
            curve_sign = 1 if curvature >= 0 else -1
            abs_curvature = abs(curvature)

            for y in y_values:
                # Parabolic curve: maximum at center, 0 at ends
                t = (y - y_start) / (y_end - y_start)
                offset = abs_curvature * (1 - (2*t - 1)**2)
                x = x_start + curve_direction * curve_sign * offset
                points.append((x, y))

        # Draw the curved edge
        image = add_curved_line(
            image,
            line_color=color,
            points=points,
            line_width=line_width,
            antialias=True
        )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add visual guide by drawing a semi-transparent white rectangle.

        Draws a semi-transparent white rectangle around both squares to partially
        mask the radial lines, making it easier to see that the square edges
        are actually straight.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide rectangles added
        """
        PADDING = 60  # Padding around square (pixels)
        ALPHA = 0.9  # Transparency (0.9 = 90% opaque)
        WHITE_COLOR = np.array([1.0, 1.0, 1.0])  # White

        # Process left square
        square = elements['square']
        cx, cy = square['center']
        square_size = square['size']

        # Calculate rectangle bounds for left square
        half_width = (square_size + 2 * PADDING) // 2
        half_height = (square_size + 2 * PADDING) // 2

        # Calculate pixel ranges
        y_min = max(0, cy - half_height)
        y_max = min(self.height, cy + half_height)
        x_min = max(0, cx - half_width)
        x_max = min(self.width, cx + half_width)

        # Apply alpha blending for left square
        image[y_min:y_max, x_min:x_max] = (
            ALPHA * WHITE_COLOR + (1 - ALPHA) * image[y_min:y_max, x_min:x_max]
        )

        # Process right square
        square_right = elements['square_right']
        cx_right, cy_right = square_right['center']
        square_right_size = square_right['size']

        # Calculate rectangle bounds for right square
        half_width_right = (square_right_size + 2 * PADDING) // 2
        half_height_right = (square_right_size + 2 * PADDING) // 2

        # Calculate pixel ranges
        y_min_right = max(0, cy_right - half_height_right)
        y_max_right = min(self.height, cy_right + half_height_right)
        x_min_right = max(0, cx_right - half_width_right)
        x_max_right = min(self.width, cx_right + half_width_right)

        # Apply alpha blending for right square
        image[y_min_right:y_max_right, x_min_right:x_max_right] = (
            ALPHA * WHITE_COLOR + (1 - ALPHA) * image[y_min_right:y_max_right, x_min_right:x_max_right]
        )

        # Redraw the left square on top of the semi-transparent rectangle
        image = self._draw_square_border(
            image,
            center=square['center'],
            size=square['size'],
            color=square['color'],
            line_width=square['width'],
            is_curved=square.get('is_curved', False),
            curvature=square.get('curvature', 0)
        )

        # Redraw the right square on top of the semi-transparent rectangle
        image = self._draw_square_border(
            image,
            center=square_right['center'],
            size=square_right['size'],
            color=square_right['color'],
            line_width=square_right['width'],
            is_curved=square_right.get('is_curved', False),
            curvature=square_right.get('curvature', 0)
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing all radial lines.

        In the control condition, all radial lines are removed, eliminating
        the illusion effect entirely.

        Args:
            elements: Original elements

        Returns:
            Modified elements with no radial lines
        """
        # Remove all radial lines by disabling drawing
        elements['draw_radial_lines'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version with actually curved square edges.

        Enables the curved edge rendering with the curvature already
        calculated in define_elements().

        Args:
            elements: Original elements (with curvature parameter set)

        Returns:
            Modified elements with curved edges enabled
        """
        # Enable curved edges for both squares
        elements['square']['is_curved'] = True
        elements['square_right']['is_curved'] = True
        return elements
