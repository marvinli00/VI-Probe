"""Ponzo Illusion (length, VI-Probe case 3). Converging lines (suggesting
perspective/depth) make identical-length horizontal lines appear different lengths."""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line
from core.template import IllusionTemplate


class PonzoIllusion(IllusionTemplate):
    """
    Ponzo Illusion Generator (Classical Version)

    Generates the classic Ponzo illusion with:
    - Two converging lines creating perspective effect
    - Two horizontal lines that appear different lengths due to depth perception

    The strength parameter controls horizontal line length:
    - strength = -1.0: minimum line length (60 pixels)
    - strength =  0.0: default line length (80 pixels)
    - strength = +1.0: maximum line length (100 pixels)

    Converging line parameters are fixed and do not change with strength.

    Line length is calculated using linear interpolation:
        length = MIN + (MAX - MIN) * (strength + 1) / 2
    """

    def __init__(self, DEFAULT_LINE_LENGTH=80):
        self.DEFAULT_LINE_LENGTH = DEFAULT_LINE_LENGTH  # pixels (strength = 0.0)

        # Converging line parameters (fixed)
        self.CONVERGE_BOTTOM_WIDTH = 150  # Width at bottom of converging lines
        self.CONVERGE_TOP_WIDTH = 40      # Width at top (narrower for perspective)
        self.CONVERGE_LINE_WIDTH = 2      # Line thickness

        # Horizontal line positions
        self.TOP_LINE_Y_RATIO = 1 / 4      # Top line at 1/4 height (appears farther)
        self.BOTTOM_LINE_Y_RATIO = 3 / 4   # Bottom line at 3/4 height (appears closer)
        self.HORIZONTAL_LINE_WIDTH = 2     # Line thickness


        super().__init__(
            illusion_name="ponzo_classical",
            width=512,
            height=256,
            strength_levels=[0.4,0.6,0.8,1.0,1.2,1.4,1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_line_length(self, strength: float) -> int:
        """
        Calculate horizontal line length from strength using linear interpolation.

        Args:
            strength: Strength value from -1.0 to 1.0

        Returns:
            Line length in pixels
        """
        # Linear interpolation: length = min + (max - min) * normalized_strength
        # normalized_strength maps [-1, 1] to [0, 1]
        # normalized = (strength + 1.0) / 2.0
        length = self.DEFAULT_LINE_LENGTH*strength
        #self.MIN_LINE_LENGTH + (self.MAX_LINE_LENGTH - self.MIN_LINE_LENGTH) * normalized
        return int(round(length))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Ponzo illusion elements.

        For Original variation:
            - Both horizontal lines have the same length (determined by strength)
        For Perturbed variation:
            - Bottom line has default length (strength = 0)
            - Top line has length determined by strength parameter

        Args:
            strength: Controls horizontal line length (-1.0 to 1.0)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing converging lines, horizontal lines, and guide bars
        """
        self.strength = strength

        if is_original:
            # Both lines have the same length based on strength
            line_length = self._calculate_line_length(strength)
        else:
            # Perturbed: calculate default length (will be modified in apply_perturbation)
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
            # Converging lines (left and right)
            'converge_left': {
                'start': (center_x - self.CONVERGE_BOTTOM_WIDTH // 2, self.height - 10),
                'end': (center_x - self.CONVERGE_TOP_WIDTH // 2, 10),
                'color': (0, 0, 0),  # Black
                'width': self.CONVERGE_LINE_WIDTH,
            },
            'converge_right': {
                'start': (center_x + self.CONVERGE_BOTTOM_WIDTH // 2, self.height - 10),
                'end': (center_x + self.CONVERGE_TOP_WIDTH // 2, 10),
                'color': (0, 0, 0),  # Black
                'width': self.CONVERGE_LINE_WIDTH,
            },

            # Top horizontal line (appears farther away / longer)
            'line_top': {
                'start': (top_line_start_x, top_line_y),
                'end': (top_line_end_x, top_line_y),
                'color': (0, 0, 0),  # Black
                'width': self.HORIZONTAL_LINE_WIDTH,
            },

            # Bottom horizontal line (appears closer / shorter)
            'line_bottom': {
                'start': (bottom_line_start_x, bottom_line_y),
                'end': (bottom_line_end_x, bottom_line_y),
                'color': (0, 0, 0),  # Black
                'width': self.HORIZONTAL_LINE_WIDTH,
            },

            # Visual guide bars (vertical dashed lines at top line endpoints)
            'guide_bars': [
                {
                    'name': 'left_guide',
                    'start': (top_line_start_x, 0),
                    'end': (top_line_start_x, self.height),
                    'color': (1, 0, 0),  #  Red
                    'width': 1,
                    'dashed': True,
                },
                {
                    'name': 'right_guide',
                    'start': (top_line_end_x, 0),
                    'end': (top_line_end_x, self.height),
                    'color': (1, 0, 0),  #  Red
                    'width': 1,
                    'dashed': True,
                }
            ],

            # Flag to control whether converging lines should be drawn
            'draw_converging_lines': True,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Ponzo illusion on the canvas.

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw converging lines first (if enabled)
        if elements.get('draw_converging_lines', True):
            # Left converging line
            image = add_arrowed_line(
                image,
                line_color=elements['converge_left']['color'],
                start_point=elements['converge_left']['start'],
                end_point=elements['converge_left']['end'],
                line_width=elements['converge_left']['width'],
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
            )

            # Right converging line
            image = add_arrowed_line(
                image,
                line_color=elements['converge_right']['color'],
                start_point=elements['converge_right']['start'],
                end_point=elements['converge_right']['end'],
                line_width=elements['converge_right']['width'],
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
            )

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
        Create control condition by removing converging lines.

        In the control condition, only the horizontal lines are shown,
        making it clear they are the same length (no perspective illusion).

        Both lines still change length together based on strength parameter.

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
        Create perturbed version by fixing Bottom line and only changing Top line.

        The perturbation logic:
        - Bottom line: Fixed at default length (strength = 0)
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
