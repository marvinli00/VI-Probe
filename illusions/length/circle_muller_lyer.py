"""Circle Muller-Lyer Illusion (length, VI-Probe case 2).

A variation of the classic Müller-Lyer illusion that uses circles instead of arrows
at the ends of lines to create the same length perception illusion.

Classic setup:
- Two horizontal lines of equal length
- Top line: circles positioned inward (inside the line endpoints)
- Bottom line: circles positioned outward (outside the line endpoints)
- The line with inward circles appears shorter than the line with outward circles

Variations:
- Control: Lines without circles (no illusion effect)
- Original: Classic Circle Müller-Lyer with circles, both lines change length together
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


class CircleMullerLyerIllusion(IllusionTemplate):
    """
    Circle Müller-Lyer Illusion Generator

    Generates a variation of the Müller-Lyer illusion with two horizontal lines:
    - Top line (Line 1) with inward-positioned circle endpoints
    - Bottom line (Line 2) with outward-positioned circle endpoints

    The strength parameter controls line length:
    - strength = -1.0: minimum line length (200 pixels)
    - strength =  0.0: default line length (300 pixels)
    - strength = +1.0: maximum line length (400 pixels)

    Circle radius is fixed at 20 pixels and does not change with strength.

    Line length is calculated using linear interpolation:
        length = MIN + (MAX - MIN) * (strength + 1) / 2
    """

    def __init__(self, DEFAULT_LINE_LENGTH = 300):
        # Line length parameters
        self.DEFAULT_LINE_LENGTH = DEFAULT_LINE_LENGTH  # pixels (strength = 0.0)

        # Circle parameters (fixed)
        CIRCLE_RADIUS = 20  # pixels (fixed for all strengths)
        CIRCLE_FILLED = False  # Hollow circles

        self.DEFAULT_LINE_LENGTH = DEFAULT_LINE_LENGTH
        self.CIRCLE_RADIUS = CIRCLE_RADIUS
        self.CIRCLE_FILLED = CIRCLE_FILLED

        super().__init__(
            illusion_name="circle_muller_lyer",
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
        Define Circle Müller-Lyer illusion elements.

        For Original variation:
            - Both lines have the same length (determined by strength)
        For Perturbed variation:
            - Line 1 has default length (strength = 0)
            - Line 2 has length determined by strength parameter

        Args:
            strength: Controls line length (-1.0 to 1.0)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing line and guide bar parameters
        """
        self.strength = strength
        if is_original:
            # Both lines have the same length based on strength
            line_length = self._calculate_line_length(strength)
        else:
            # Calculate line length at default strength for perturbed version
            line_length = self.DEFAULT_LINE_LENGTH

        # Calculate start and end positions to center the lines
        # Lines are horizontally centered in the image
        line_1_start_x = (self.width - line_length) // 2
        line_1_end_x = line_1_start_x + line_length

        line_2_start_x = (self.width - line_length) // 2
        line_2_end_x = line_2_start_x + line_length

        elements = {
            # Top line: inward-positioned circles (○──○)
            'line_top': {
                'start': (line_1_start_x, self.height // 4),
                'end': (line_1_end_x, self.height // 4),
                'color': (0, 0, 0),  # Black
                'width': 2,
                'circle_start': 'in',  # Circle positioned inward
                'circle_end': 'in',
                'circle_radius': self.CIRCLE_RADIUS,
                'circle_filled': self.CIRCLE_FILLED,
            },

            # Bottom line: outward-positioned circles (──)
            #                                          ○  ○
            'line_bottom': {
                'start': (line_2_start_x, self.height * 3 // 4),
                'end': (line_2_end_x, self.height * 3 // 4),
                'color': (0, 0, 0),  # Black
                'width': 2,
                'circle_start': 'out',  # Circle positioned outward
                'circle_end': 'out',
                'circle_radius': self.CIRCLE_RADIUS,
                'circle_filled': self.CIRCLE_FILLED,
            },

            # Visual guide bars (vertical dashed lines at default line endpoints)
            # These show where the default (strength=0) line endpoints would be
            'guide_bars': [
                {
                    'name': 'left_guide',
                    'start': (line_1_start_x, 0),
                    'end': (line_1_start_x, self.height),
                    'color': (1, 0, 0),  # Red
                    'width': 1,
                    'dashed': True,
                },
                {
                    'name': 'right_guide',
                    'start': (line_1_end_x, 0),
                    'end': (line_1_end_x, self.height),
                    'color': (1, 0, 0),  # red
                    'width': 1,
                    'dashed': True,
                }
            ]
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Circle Müller-Lyer illusion on the canvas.

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw top line with inward circles
        image = add_arrowed_line(
            image,
            line_color=elements['line_top']['color'],
            start_point=elements['line_top']['start'],
            end_point=elements['line_top']['end'],
            line_width=elements['line_top']['width'],
            arrow_length=0,  # No arrows, only circles
            circle_start=elements['line_top']['circle_start'],
            circle_end=elements['line_top']['circle_end'],
            circle_radius=elements['line_top']['circle_radius'],
            circle_filled=elements['line_top']['circle_filled'],
        )

        # Draw bottom line with outward circles
        image = add_arrowed_line(
            image,
            line_color=elements['line_bottom']['color'],
            start_point=elements['line_bottom']['start'],
            end_point=elements['line_bottom']['end'],
            line_width=elements['line_bottom']['width'],
            arrow_length=0,  # No arrows, only circles
            circle_start=elements['line_bottom']['circle_start'],
            circle_end=elements['line_bottom']['circle_end'],
            circle_radius=elements['line_bottom']['circle_radius'],
            circle_filled=elements['line_bottom']['circle_filled'],
        )

        return image


    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide bar positions based on current line lengths.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide bar positions
        """
        # Default line length at strength = 0
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
        Create control condition by removing circles.

        In the control condition, both lines have no circles,
        making it clear they are the same length (no illusion).

        Both lines still change length together based on strength parameter.

        Args:
            elements: Original elements

        Returns:
            Modified elements with no circles
        """
        elements['line_top']['circle_radius'] = 0
        elements['line_bottom']['circle_radius'] = 0
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

        # Will change the length of Line 2
        calculate_length = self._calculate_line_length(self.strength)

        # Fix Line 2 at strength-based length
        line_2_start_x = (self.width - calculate_length) // 2
        line_2_end_x = line_2_start_x + calculate_length
        elements['line_bottom']['start'] = (line_2_start_x, self.height * 3 // 4)
        elements['line_bottom']['end'] = (line_2_end_x, self.height * 3 // 4)

        # Line 1 keeps the default length from define_elements()
        # (no modification needed, already set correctly)

        return elements
