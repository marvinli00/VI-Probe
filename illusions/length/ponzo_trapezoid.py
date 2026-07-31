"""Ponzo Trapezoid Illusion (length, VI-Probe case 4). A filled gray trapezoid
background (suggesting perspective/depth) makes identical-length horizontal lines
appear different lengths."""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line
from core.template import IllusionTemplate


class PonzoTrapezoidIllusion(IllusionTemplate):
    """
    Ponzo Illusion Generator (Trapezoid Version)

    Generates the Ponzo illusion with:
    - A filled gray trapezoid creating perspective effect
    - Two horizontal lines that appear different lengths due to depth perception

    The strength parameter controls horizontal line length via scaling:
    - strength = 0.4: line_length = DEFAULT * 0.4
    - strength = 1.0: line_length = DEFAULT * 1.0 (standard)
    - strength = 1.6: line_length = DEFAULT * 1.6

    Trapezoid parameters are fixed and do not change with strength.

    Line length calculation:
        length = DEFAULT_LINE_LENGTH * strength
    """

    def __init__(self, DEFAULT_LINE_LENGTH=80):
        self.DEFAULT_LINE_LENGTH = DEFAULT_LINE_LENGTH  # pixels (strength = 1.0)

        # Trapezoid parameters (fixed)
        self.TRAP_BOTTOM_WIDTH = 150  # Width at bottom
        self.TRAP_TOP_WIDTH = 40      # Width at top (narrower for perspective)
        self.TRAP_COLOR = (0.7, 0.7, 0.7)  # Gray fill
        self.TRAP_TOP_Y = 10          # Top edge Y position
        self.TRAP_BOTTOM_Y = None     # Will be set to height - 10 in define_elements

        # Horizontal line positions
        self.TOP_LINE_Y_RATIO = 1 / 4      # Top line at 1/4 height (appears farther)
        self.BOTTOM_LINE_Y_RATIO = 3 / 4   # Bottom line at 3/4 height (appears closer)
        self.HORIZONTAL_LINE_WIDTH = 2     # Line thickness
        self.HORIZONTAL_LINE_COLOR = (0, 0, 0)  # Black

        super().__init__(
            illusion_name="ponzo_trapezoid",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_line_length(self, strength: float) -> int:
        """
        Calculate horizontal line length from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default length, 1.5 = 150% of default)

        Returns:
            Line length in pixels
        """
        length = self.DEFAULT_LINE_LENGTH * strength
        return int(round(length))

    def _draw_filled_trapezoid(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw a filled trapezoid using scanline method.

        For each horizontal scanline (row), calculate the width of the trapezoid
        at that height using linear interpolation, then fill the pixels.

        Args:
            image: Current image
            elements: Element parameters containing trapezoid info

        Returns:
            Image with trapezoid drawn
        """
        if not elements.get('draw_trapezoid', True):
            return image

        trap = elements['trapezoid']
        top_y = trap['top_y']
        bottom_y = trap['bottom_y']
        top_width = trap['top_width']
        bottom_width = trap['bottom_width']
        color = trap['color']
        center_x = self.width // 2

        # Fill trapezoid using scanline approach
        for y in range(top_y, bottom_y + 1):
            # Linear interpolation: t goes from 0 (top) to 1 (bottom)
            if bottom_y != top_y:
                t = (y - top_y) / (bottom_y - top_y)
            else:
                t = 0

            # Calculate width at this y position
            current_width = top_width + t * (bottom_width - top_width)

            # Calculate left and right x positions
            left_x = int(center_x - current_width / 2)
            right_x = int(center_x + current_width / 2)

            # Fill the scanline
            # Color is in 0-1 range, need to convert for float32 image
            image[y, left_x:right_x] = np.array(color)

        return image

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Ponzo trapezoid illusion elements.

        For Original variation:
            - Both horizontal lines have the same length (determined by strength)
        For Perturbed variation:
            - Bottom line has default length (strength = 1.0)
            - Top line has length determined by strength parameter

        Args:
            strength: Controls horizontal line length (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing trapezoid, horizontal lines, and guide bars
        """
        self.strength = strength

        if is_original:
            # Both lines have the same length based on strength
            line_length = self._calculate_line_length(strength)
        else:
            # Perturbed: use default length (will be modified in apply_perturbation)
            line_length = self.DEFAULT_LINE_LENGTH

        center_x = self.width // 2

        # Calculate horizontal line positions (centered)
        top_line_y = int(self.height * self.TOP_LINE_Y_RATIO)
        bottom_line_y = int(self.height * self.BOTTOM_LINE_Y_RATIO)

        # Horizontal line coordinates (centered)
        top_line_start_x = center_x - line_length // 2
        top_line_end_x = center_x + line_length // 2

        bottom_line_start_x = center_x - line_length // 2
        bottom_line_end_x = center_x + line_length // 2

        elements = {
            # Trapezoid background
            'trapezoid': {
                'top_y': self.TRAP_TOP_Y,
                'bottom_y': self.height - 10,  # TRAP_BOTTOM_Y
                'top_width': self.TRAP_TOP_WIDTH,
                'bottom_width': self.TRAP_BOTTOM_WIDTH,
                'color': self.TRAP_COLOR,
            },

            # Top horizontal line (appears farther away / longer)
            'line_top': {
                'start': (top_line_start_x, top_line_y),
                'end': (top_line_end_x, top_line_y),
                'color': self.HORIZONTAL_LINE_COLOR,
                'width': self.HORIZONTAL_LINE_WIDTH,
            },

            # Bottom horizontal line (appears closer / shorter)
            'line_bottom': {
                'start': (bottom_line_start_x, bottom_line_y),
                'end': (bottom_line_end_x, bottom_line_y),
                'color': self.HORIZONTAL_LINE_COLOR,
                'width': self.HORIZONTAL_LINE_WIDTH,
            },

            # Visual guide bars (vertical dashed lines at top line endpoints)
            'guide_bars': [
                {
                    'name': 'left_guide',
                    'start': (top_line_start_x, 0),
                    'end': (top_line_start_x, self.height),
                    'color': (1,0,0),  # Red
                    'width': 1,
                    'dashed': True,
                },
                {
                    'name': 'right_guide',
                    'start': (top_line_end_x, 0),
                    'end': (top_line_end_x, self.height),
                    'color': (1, 0, 0),  # Red
                    'width': 1,
                    'dashed': True,
                }
            ],

            # Flag to control whether trapezoid should be drawn
            'draw_trapezoid': True,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Ponzo trapezoid illusion on the canvas.

        Order of drawing:
        1. Filled trapezoid (background)
        2. Top horizontal line
        3. Bottom horizontal line

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw filled trapezoid first (if enabled)
        image = self._draw_filled_trapezoid(image, elements)

        # Draw top horizontal line
        image = add_arrowed_line(
            image,
            line_color=elements['line_top']['color'],
            start_point=elements['line_top']['start'],
            end_point=elements['line_top']['end'],
            line_width=elements['line_top']['width'],
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
        )

        # Draw bottom horizontal line
        image = add_arrowed_line(
            image,
            line_color=elements['line_bottom']['color'],
            start_point=elements['line_bottom']['start'],
            end_point=elements['line_bottom']['end'],
            line_width=elements['line_bottom']['width'],
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
        )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide bar positions based on current top line length.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide bar positions
        """
        # Use top line endpoints for guide bars
        line_start_x = elements["line_top"]['start'][0]
        line_end_x = elements["line_top"]['end'][0]

        # Update guide bar positions
        elements['guide_bars'][0]['start'] = (line_start_x, 0)
        elements['guide_bars'][0]['end'] = (line_start_x, self.height)

        elements['guide_bars'][1]['start'] = (line_end_x, 0)
        elements['guide_bars'][1]['end'] = (line_end_x, self.height)

        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add vertical guide bars to show top line endpoints.

        The dashed vertical lines show where the top line endpoints are,
        helping viewers compare the two horizontal line lengths.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide bars added
        """
        elements = self.update_visual_guides(elements)
        for guide in elements['guide_bars']:
            image = add_arrowed_line(
                image,
                line_color=guide['color'],
                start_point=guide['start'],
                end_point=guide['end'],
                line_width=guide['width'],
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
                dashed=guide['dashed'],
            )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing trapezoid.

        In the control condition, only the horizontal lines are shown,
        making it clear they are the same length (no perspective illusion).

        Both lines still change length together based on strength parameter.

        Args:
            elements: Original elements

        Returns:
            Modified elements with no trapezoid
        """
        # Disable drawing of trapezoid
        elements['draw_trapezoid'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by fixing Bottom line and only changing Top line.

        The perturbation logic:
        - Bottom line: Fixed at default length (strength = 1.0)
        - Top line: Length varies with strength parameter

        This creates length inequality to test if the illusion still works
        with different actual lengths.

        Args:
            elements: Original elements (with both lines at default length)

        Returns:
            Modified elements with Bottom line fixed, Top line variable
        """

        # Calculate the new length for top line based on strength
        calculate_length = self._calculate_line_length(self.strength)

        center_x = self.width // 2
        top_line_y = int(self.height * self.TOP_LINE_Y_RATIO)

        # Modify Top line to have strength-based length
        top_line_start_x = center_x - calculate_length // 2
        top_line_end_x = center_x + calculate_length // 2

        elements['line_top']['start'] = (top_line_start_x, top_line_y)
        elements['line_top']['end'] = (top_line_end_x, top_line_y)

        # Bottom line keeps the default length from define_elements()
        # (no modification needed, already set correctly)

        return elements
