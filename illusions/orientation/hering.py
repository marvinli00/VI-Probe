"""Hering Illusion (orientation, VI-Probe case 19).

Radial background lines make two straight horizontal test lines appear to
bow outward (convex curvature) even though they are perfectly straight.
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_curved_line
from core.template import IllusionTemplate


class HeringIllusion(IllusionTemplate):
    """
    Hering Illusion Generator

    Generates the classic Hering illusion with:
    - Radial lines emanating from center
    - Two horizontal test lines (upper and lower)
    - Lines appear curved but are actually straight (in original mode)

    The strength parameter has dual meaning:
    - Original mode: Controls radial line density (num_lines = 32 * strength)
    - Perturbed mode: Controls actual curve amplitude (amplitude = 15 * (strength - 1.0))
      - strength = 1.0: Straight lines (baseline)
      - strength > 1.0: Outward bow (convex)
      - strength < 1.0: Inward bow (concave)
    """

    def __init__(self, DEFAULT_NUM_RADIAL_LINES: int = 32):
        # Image is square for radial symmetry
        WIDTH = 512
        HEIGHT = 512

        # Radial lines configuration
        self.DEFAULT_NUM_RADIAL_LINES = DEFAULT_NUM_RADIAL_LINES
        self.CENTER_X = WIDTH // 2
        self.CENTER_Y = HEIGHT // 2
        self.RADIAL_COLOR = (0, 0, 0)  # Black
        self.RADIAL_WIDTH = 1

        # Test lines configuration
        self.UPPER_LINE_Y = HEIGHT // 3 + 25
        self.LOWER_LINE_Y = HEIGHT * 2 // 3 - 25
        self.LINE_START_X = 25
        self.LINE_END_X = WIDTH - 25
        self.TEST_LINE_COLOR = (0, 0, 0)  # Black
        self.TEST_LINE_WIDTH = 3

        # Curve configuration (for perturbed mode)
        self.DEFAULT_CURVE_AMPLITUDE = 15  # pixels

        super().__init__(
            illusion_name="hering_illusion",
            width=WIDTH,
            height=HEIGHT,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Hering illusion elements in their base state.

        This method always defines test lines as STRAIGHT. Perturbation
        (curvature) will be applied later in apply_perturbation().

        For Original variation:
            - Radial line count varies with strength (num = 32 * strength)
        For Perturbed variation:
            - Radial line count is fixed at 32
            - Curve amplitude = 15 * (strength - 1.0)
              - strength=1.0 → amplitude=0 (straight, baseline)
              - strength>1.0 → amplitude>0 (outward bow)
              - strength<1.0 → amplitude<0 (inward bow)

        Args:
            strength: Controls radial density (original) or curve amplitude (perturbed)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing radial lines and test lines parameters
        """
        self.strength = strength

        if is_original:
            # Original: Variable radial density based on strength
            num_radial_lines = int(self.DEFAULT_NUM_RADIAL_LINES * strength)
            # Curve amplitude not used (lines stay straight)
            curve_amplitude = 0
        else:
            # Perturbed: Fixed radial density, calculate curve amplitude
            # strength=1.0 → straight (amplitude=0)
            # strength>1.0 → outward bow (amplitude>0)
            # strength<1.0 → inward bow (amplitude<0)
            num_radial_lines = self.DEFAULT_NUM_RADIAL_LINES
            curve_amplitude = self.DEFAULT_CURVE_AMPLITUDE * (strength - 1.0)

        elements = {
            # Radial lines configuration
            'radial_lines': {
                'num_lines': num_radial_lines,
                'center': (self.CENTER_X, self.CENTER_Y),
                'color': self.RADIAL_COLOR,
                'width': self.RADIAL_WIDTH,
                'draw': True,  # Control will set to False
            },

            # Test lines configuration - ALWAYS STRAIGHT initially
            'test_lines': {
                'upper': {
                    'y': self.UPPER_LINE_Y,
                    'start_x': self.LINE_START_X,
                    'end_x': self.LINE_END_X,
                    'color': self.TEST_LINE_COLOR,
                    'width': self.TEST_LINE_WIDTH,
                    'is_curved': False,  # Always straight in base definition
                    'curve_amplitude': 0,  # Will be set by apply_perturbation()
                    'curve_direction': -1,  # Upward bow (when curved)
                },
                'lower': {
                    'y': self.LOWER_LINE_Y,
                    'start_x': self.LINE_START_X,
                    'end_x': self.LINE_END_X,
                    'color': self.TEST_LINE_COLOR,
                    'width': self.TEST_LINE_WIDTH,
                    'is_curved': False,  # Always straight in base definition
                    'curve_amplitude': 0,  # Will be set by apply_perturbation()
                    'curve_direction': +1,  # Downward bow (when curved)
                },
            },

            # Store curve amplitude for apply_perturbation()
            'curve_amplitude': curve_amplitude,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Hering illusion on the canvas.

        Order of drawing:
        1. Radial lines (if enabled)
        2. Upper test line
        3. Lower test line

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw radial lines (if enabled)
        if elements['radial_lines']['draw']:
            radial_config = elements['radial_lines']
            num_lines = radial_config['num_lines']
            center = radial_config['center']

            # Calculate max distance to reach any edge
            max_dist = np.sqrt(self.width**2 + self.height**2)

            for i in range(num_lines):
                angle = np.radians(i * 360 / num_lines)
                end_x = int(center[0] + max_dist * np.cos(angle))
                end_y = int(center[1] + max_dist * np.sin(angle))

                image = add_arrowed_line(
                    image,
                    line_color=radial_config['color'],
                    start_point=center,
                    end_point=(end_x, end_y),
                    line_width=radial_config['width'],
                    arrow_start='none',
                    arrow_end='none',
                    antialias=True
                )

        # Draw test lines
        for line_key in ['upper', 'lower']:
            line_config = elements['test_lines'][line_key]
            image = self._draw_test_line(image, line_config)

        return image

    def _draw_test_line(self, image: np.ndarray, line_config: Dict[str, Any]) -> np.ndarray:
        """
        Draw a test line (straight or curved).

        Args:
            image: Current image
            line_config: Line configuration dictionary

        Returns:
            Image with line drawn
        """
        y_pos = line_config['y']
        start_x = line_config['start_x']
        end_x = line_config['end_x']
        color = line_config['color']
        width = line_config['width']
        is_curved = line_config['is_curved']

        if not is_curved:
            # Draw straight line
            image = add_arrowed_line(
                image,
                line_color=color,
                start_point=(start_x, y_pos),
                end_point=(end_x, y_pos),
                line_width=width,
                arrow_start='none',
                arrow_end='none',
                antialias=True
            )
        else:
            # Draw curved line using smooth antialiased curve rendering
            curve_amplitude = line_config['curve_amplitude']
            curve_direction = line_config['curve_direction']

            # Generate curve points (500 points for smooth curve)
            # IMPORTANT: Keep floating-point coordinates for subpixel precision
            # The int() conversion will happen in add_curved_line after supersampling
            num_points = 500
            x_values = np.linspace(start_x, end_x, num_points)

            points = []
            for x in x_values:
                # Calculate parabolic offset: maximum at center, 0 at ends
                t = (x - start_x) / (end_x - start_x)
                offset = curve_amplitude * (1 - (2*t - 1)**2)

                # Apply curve direction: -1 for upward, +1 for downward
                # Keep as float for subpixel accuracy (no int() here!)
                y = y_pos + curve_direction * offset
                points.append((x, y))

            # Draw entire curve in one operation with supersampling antialiasing
            image = add_curved_line(
                image,
                line_color=color,
                points=points,
                line_width=width,
                antialias=True
            )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add visual guide rectangle to show test line boundaries.

        Draws one large semi-transparent rectangle covering both test lines,
        from the upper line to the lower line, to help viewers see whether
        lines are truly straight or curved.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide rectangle added
        """
        GUIDE_COLOR = (0.7, 0.8, 1.0)  # Light blue
        GUIDE_ALPHA = 1  # Moderate transparency (more visible than 0.1)

        # Get upper and lower line configurations
        upper_line = elements['test_lines']['upper']
        lower_line = elements['test_lines']['lower']

        # Rectangle boundaries: one large rectangle covering both lines
        x1 = int(upper_line['start_x'])  # Left edge (upper line start)
        x2 = int(upper_line['end_x'])    # Right edge (upper line end)
        y1 = int(upper_line['y'])        # Top edge (upper line position)
        y2 = int(lower_line['y'])        # Bottom edge (lower line position)

        # Draw one large semi-transparent rectangle
        image = self._add_transparent_rect(
            image, x1, y1, x2, y2,
            GUIDE_COLOR, GUIDE_ALPHA
        )

        return image

    def _add_transparent_rect(self, image: np.ndarray,
                             x1: int, y1: int, x2: int, y2: int,
                             color: tuple, alpha: float) -> np.ndarray:
        """
        Add a semi-transparent rectangle to the image.

        Uses alpha blending: result = background * (1 - alpha) + foreground * alpha

        Args:
            image: Input image
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            color: RGB color tuple (0-1 range)
            alpha: Transparency (0=fully transparent, 1=fully opaque)

        Returns:
            Modified image with rectangle drawn
        """
        H, W = image.shape[:2]

        # Boundary checking
        x1 = max(0, int(x1))
        x2 = min(W, int(x2))
        y1 = max(0, int(y1))
        y2 = min(H, int(y2))

        if x1 >= x2 or y1 >= y2:
            return image

        # Alpha blending
        color_array = np.array(color, dtype=np.float32)
        image[y1:y2, x1:x2, :] = (
            image[y1:y2, x1:x2, :] * (1 - alpha) +
            color_array * alpha
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing radial lines.

        In the control condition, test lines are shown without radial background,
        making it clear whether they are straight or curved (no illusion effect).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no radial lines
        """
        elements['radial_lines']['draw'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply perturbation by making test lines curved.

        This method modifies the straight lines defined in define_elements()
        to have parabolic curvature. The curve amplitude is determined by
        the strength parameter (stored in elements['curve_amplitude']).

        Perturbation effects:
        - Upper line: Curves upward (convex, curve_direction=-1)
        - Lower line: Curves downward (convex, curve_direction=+1)
        - Both curves have amplitude = 15 * strength pixels at center

        Args:
            elements: Elements with straight test lines from define_elements()

        Returns:
            Modified elements with curved test lines
        """
        # Get the stored curve amplitude
        curve_amplitude = elements.get('curve_amplitude', 0)

        # Apply curvature to upper test line
        elements['test_lines']['upper']['is_curved'] = True
        elements['test_lines']['upper']['curve_amplitude'] = curve_amplitude

        # Apply curvature to lower test line
        elements['test_lines']['lower']['is_curved'] = True
        elements['test_lines']['lower']['curve_amplitude'] = curve_amplitude

        return elements
