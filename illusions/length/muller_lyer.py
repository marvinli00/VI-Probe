"""Muller-Lyer Illusion (length, VI-Probe case 1).

The Müller-Lyer illusion demonstrates how arrow-like tails at the ends of lines
can make identical-length lines appear to be different lengths.

Classic setup:
- Two horizontal lines of equal length
- Top line: outward-pointing arrows (fins) at both ends
- Bottom line: inward-pointing arrows (fins) at both ends
- The line with outward arrows appears longer than the line with inward arrows

Variations:
- Control: Lines without arrows (no illusion effect)
- Original: Classic Müller-Lyer with arrows, both lines change length together
- Perturbed: Only Line 2 length changes, Line 1 stays at default length

Strength levels (-1.0 to 1.0): Control line segment length
- -1.0: Shortest lines
-  0.0: Default/medium length lines
- +1.0: Longest lines
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line
from core.template import IllusionTemplate


class MullerLyerIllusion(IllusionTemplate):
    """
    Müller-Lyer Illusion Generator

    Generates the classic Müller-Lyer illusion with two horizontal lines:
    - Top line (Line 1) with outward-pointing arrow fins
    - Bottom line (Line 2) with inward-pointing arrow fins

    The strength parameter controls line length:
    - strength = -1.0: minimum line length (200 pixels)
    - strength =  0.0: default line length (300 pixels)
    - strength = +1.0: maximum line length (400 pixels)

    Line length is calculated using linear interpolation:
        length = MIN + (MAX - MIN) * (strength + 1) / 2
    """

    def __init__(self, DEFAULT_LINE_LENGTH=300):
        # Line length parameters
        self.DEFAULT_LINE_LENGTH = DEFAULT_LINE_LENGTH  # pixels (strength = 0.0)

        # Arrow parameters
        ARROW_LENGTH = 20  # pixels (fixed for all strengths)
        ARROW_ANGLE = 30  # degrees

        self.ARROW_LENGTH = ARROW_LENGTH
        self.ARROW_ANGLE = ARROW_ANGLE

        super().__init__(
            illusion_name="muller_lyer",
            width=512,
            height=256,
            strength_levels=[0.4,0.6,0.8,1.0,1.2,1.4,1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_line_length(self, strength: float) -> int:
        """
        Calculate line length from strength using linear interpolation.

        Args:
            strength: Strength value from -1.0 to 1.0

        Returns:
            Line length in pixels
        """
        # Linear interpolation: length = min + (max - min) * normalized_strength
        # normalized_strength maps [-1, 1] to [0, 1]
        # normalized = (strength + 1.0) / 2.0
        # length = self.MIN_LINE_LENGTH + (self.MAX_LINE_LENGTH - self.MIN_LINE_LENGTH) * normalized
        length = self.DEFAULT_LINE_LENGTH*strength
        return int(round(length))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Müller-Lyer illusion elements.

        For Original variation:
            - Both lines have the same length (determined by strength)
        For Perturbed variation:
            - Line 1 has default length (strength = 0)
            - Line 2 has length determined by strength parameter

        Args:
            strength: Controls line length (-1.0 to 1.0)

        Returns:
            Dictionary containing line and guide bar parameters
        """
        self.strength = strength
        if is_original:
            # Both lines have the same length based on strength
            line_length = self._calculate_line_length(strength)
        else:
            # Calculate line length based on strength, always make the same length unless changed in perturbation
            line_length = self.DEFAULT_LINE_LENGTH

        # Calculate start and end positions to center the lines
        # Lines are horizontally centered in the image
        line_1_start_x = (self.width - line_length) // 2
        line_1_end_x = line_1_start_x + line_length

        line_2_start_x = (self.width - line_length) // 2
        line_2_end_x = line_2_start_x + line_length

        elements = {
            # Top line: outward-pointing arrows (>─<)
            'line_top': {
                'start': (line_1_start_x, self.height // 4),
                'end': (line_1_end_x, self.height // 4),
                'color': (0, 0, 0),  # Black
                'width': 2,
                'arrow_start': 'out',  # Arrow points outward from line
                'arrow_end': 'out',
                'arrow_length': self.ARROW_LENGTH,
                'arrow_angle': self.ARROW_ANGLE,
            },

            # Bottom line: inward-pointing arrows (─><─)
            'line_bottom': {
                'start': (line_2_start_x, self.height * 3 // 4),
                'end': (line_2_end_x, self.height * 3 // 4),
                'color': (0, 0, 0),  # Black
                'width': 2,
                'arrow_start': 'in',  # Arrow points inward toward line
                'arrow_end': 'in',
                'arrow_length': self.ARROW_LENGTH,
                'arrow_angle': self.ARROW_ANGLE,
            },

            # Visual guide bars (vertical dashed lines at default line endpoints)
            # These show where the default (strength=0) line endpoints would be
            'guide_bars': [
                {
                    'name': 'left_guide',
                    'start': (line_1_start_x, 0),
                    'end': (line_1_start_x, self.height),
                    'color': (1, 0, 0),  # Gray
                    'width': 1,
                    'dashed': True,
                },
                {
                    'name': 'right_guide',
                    'start': (line_1_end_x, 0),
                    'end': (line_1_end_x, self.height),
                    'color': (1, 0, 0),  # Gray
                    'width': 1,
                    'dashed': True,
                }
            ]
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Müller-Lyer illusion on the canvas.

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw top line with outward arrows
        image = add_arrowed_line(
            image,
            line_color=elements['line_top']['color'],
            start_point=elements['line_top']['start'],
            end_point=elements['line_top']['end'],
            line_width=elements['line_top']['width'],
            arrow_start=elements['line_top']['arrow_start'],
            arrow_end=elements['line_top']['arrow_end'],
            arrow_length=elements['line_top']['arrow_length'],
            arrow_angle=elements['line_top']['arrow_angle'],
        )

        # Draw bottom line with inward arrows
        image = add_arrowed_line(
            image,
            line_color=elements['line_bottom']['color'],
            start_point=elements['line_bottom']['start'],
            end_point=elements['line_bottom']['end'],
            line_width=elements['line_bottom']['width'],
            arrow_start=elements['line_bottom']['arrow_start'],
            arrow_end=elements['line_bottom']['arrow_end'],
            arrow_length=elements['line_bottom']['arrow_length'],
            arrow_angle=elements['line_bottom']['arrow_angle'],
        )

        return image


    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide bar positions based on current line lengths.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide bar positions
        """        # Default line length at strength = 0
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
        Add vertical guide bars to show default line endpoints.

        The dashed vertical lines show where the default-length (strength=0)
        line endpoints would be, helping viewers compare line lengths.

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
        Create control condition by removing arrows.

        In the control condition, both lines have no arrows,
        making it clear they are the same length (no illusion).

        Both lines still change length together based on strength parameter.

        Args:
            elements: Original elements

        Returns:
            Modified elements with no arrows
        """
        elements['line_top']['arrow_length'] = 0
        elements['line_bottom']['arrow_length'] = 0
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by fixing Line 1 and only changing Line 2.

        The perturbation logic:
        - Line 1 (top): Fixed at default length (strength = 0)
        - Line 2 (bottom): Length varies with strength parameter

        This creates length inequality to test if the illusion still works
        with different actual lengths.

        Args:
            elements: Original elements (with both lines at strength-based length)

        Returns:
            Modified elements with Line 1 fixed, Line 2 variable
        """

        #will hcange the linegth 2
        calculate_length = self._calculate_line_length(self.strength)

        # Fix Line 1 at default length
        default_length = calculate_length
        line_2_start_x = (self.width - default_length) // 2
        line_2_end_x = line_2_start_x + default_length
        elements['line_bottom']['start'] = (line_2_start_x, self.height * 3 // 4)
        elements['line_bottom']['end'] = (line_2_end_x, self.height * 3 // 4)

        # Line 2 keeps the strength-based length from define_elements()
        # (no modification needed, already set correctly)

        return elements
