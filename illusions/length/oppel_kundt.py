"""Oppel-Kundt Illusion (length, VI-Probe case 9).

The Oppel-Kundt illusion demonstrates that a horizontal distance divided by multiple
vertical lines appears longer than an equal undivided distance.

Classic setup:
- Three tall vertical boundary lines divide the space into two segments
- Left segment: Empty (no subdivision lines)
- Right segment: Filled with intermediate vertical lines (appears longer)
- Both segments are actually the same length

Variations:
- Control: Remove subdivision lines (no illusion, segments appear equal)
- Original: Classic Oppel-Kundt with both segments varying equally with strength
- Perturbed: Right segment length varies, left segment fixed

Strength levels (0.4 to 1.6): Control segment length via scaling
- strength = 0.4: segment = 40% of default (77px)
- strength = 1.0: segment = 100% of default (192px)
- strength = 1.6: segment = 160% of default (307px)
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_letter
from core.template import IllusionTemplate


class OppelKundtIllusion(IllusionTemplate):
    """
    Oppel-Kundt Illusion Generator

    Generates the classic Oppel-Kundt illusion with:
    - Two horizontal segments of equal length
    - Left segment: undivided (empty)
    - Right segment: divided by vertical lines (appears longer)

    The strength parameter controls segment length via scaling:
    - strength = 0.4: segment_length = DEFAULT * 0.4
    - strength = 1.0: segment_length = DEFAULT * 1.0
    - strength = 1.6: segment_length = DEFAULT * 1.6

    Segment length calculation:
        segment_length = DEFAULT_SEGMENT_LENGTH * strength
    """

    def __init__(self, DEFAULT_SEGMENT_LENGTH=192):
        # For 512px width, default segment is WIDTH // 8 * 3 = 192px
        self.DEFAULT_SEGMENT_LENGTH = DEFAULT_SEGMENT_LENGTH

        # Line configuration
        self.LINE_COLOR = (0, 0, 0)       # Black
        self.LINE_WIDTH = 2               # Line thickness
        self.TICK_HEIGHT = 100            # Height of tall vertical boundary lines

        # Subdivision configuration
        self.NUM_DIVISIONS = 8            # Number of divisions in right segment
        # This creates 7 intermediate lines + 2 boundary lines = 9 total lines

        # Visual guide configuration
        self.GUIDE_TICK_HEIGHT = 20       # Height of short guide markers
        self.GUIDE_Y = 10                 # Y position of guide markers

        super().__init__(
            illusion_name="oppel_kundt",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_segment_length(self, strength: float) -> int:
        """
        Calculate segment length from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default length, 1.5 = 150% of default)

        Returns:
            Segment length in pixels
        """
        length = self.DEFAULT_SEGMENT_LENGTH * strength
        return int(round(length))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Oppel-Kundt illusion elements.

        For Original variation:
            - Both left and right segments have equal length (determined by strength)
        For Perturbed variation:
            - Left segment fixed at default length
            - Right segment length varies with strength

        Args:
            strength: Controls segment length (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing boundary lines and subdivision lines
        """
        self.strength = strength

        # Calculate segment lengths
        if is_original:
            segment_length = self._calculate_segment_length(strength)
            left_segment_length = segment_length
            right_segment_length = segment_length
        else:
            # Perturbed: left fixed at default, right varies
            left_segment_length = self.DEFAULT_SEGMENT_LENGTH
            right_segment_length = self._calculate_segment_length(strength)

        # Calculate positions
        center_x = self.width // 2
        center_y = self.height // 2

        # Three boundary line x-positions
        left_boundary_x = center_x - left_segment_length
        center_boundary_x = center_x
        right_boundary_x = center_x + right_segment_length

        # Y positions for tall boundary lines
        boundary_top_y = center_y - self.TICK_HEIGHT // 2
        boundary_bottom_y = center_y + self.TICK_HEIGHT // 2

        text_height = 10
        text_offset = 15

        elements = {
            # Left boundary line
            'line_left_boundary': {
                'start': (left_boundary_x, boundary_top_y),
                'end': (left_boundary_x, boundary_bottom_y),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            },


            'line_left_letter':{
                'center': (left_boundary_x, boundary_bottom_y + text_offset),
                'letter': 'A',
                'height': text_height,
                'letter_color': self.LINE_COLOR,
            },


            # Center boundary line
            'line_center_boundary': {
                'start': (center_boundary_x, boundary_top_y),
                'end': (center_boundary_x, boundary_bottom_y),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            },

            'line_center_letter':{
                'center': (center_boundary_x, boundary_bottom_y + text_offset),
                'letter': 'B',
                'height': text_height,
                'letter_color': self.LINE_COLOR,
            },

            # Right boundary line
            'line_right_boundary': {
                'start': (right_boundary_x, boundary_top_y),
                'end': (right_boundary_x, boundary_bottom_y),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            },

            'line_right_letter':{
                'center': (right_boundary_x, boundary_bottom_y + text_offset),
                'letter': 'C',
                'height': text_height,
                'letter_color': self.LINE_COLOR,
            },

            # Right segment subdivision lines
            'subdivision_lines': [],

            # Flag to control whether subdivision lines should be drawn
            'draw_subdivisions': True,

            # Store parameters for later use
            'left_segment_length': left_segment_length,
            'right_segment_length': right_segment_length,
            'left_boundary_x': left_boundary_x,
            'center_boundary_x': center_boundary_x,
            'right_boundary_x': right_boundary_x,
            'boundary_top_y': boundary_top_y,
            'boundary_bottom_y': boundary_bottom_y,
            'center_y': center_y,
        }

        # Calculate subdivision line positions for right segment
        # Create intermediate lines (NUM_DIVISIONS - 1 lines between center and right boundary)
        for i in range(1, self.NUM_DIVISIONS):
            offset = right_segment_length // self.NUM_DIVISIONS
            x = center_boundary_x + offset * i
            elements['subdivision_lines'].append({
                'start': (x, boundary_top_y),
                'end': (x, boundary_bottom_y),
                'color': self.LINE_COLOR,
                'width': self.LINE_WIDTH,
            })

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Oppel-Kundt illusion on the canvas.

        Order of drawing:
        1. Three boundary lines (left, center, right)
        2. Subdivision lines in right segment (if enabled)

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw three boundary lines
        for line_key in ['line_left_boundary', 'line_center_boundary', 'line_right_boundary']:
            line = elements[line_key]
            image = add_arrowed_line(
                image,
                line_color=line['color'],
                start_point=line['start'],
                end_point=line['end'],
                line_width=line['width'],
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
                antialias=False,
            )

        for letter_key in ['line_left_letter','line_center_letter', 'line_right_letter']:
            letter = elements[letter_key]
            image = add_letter(
                image,
                letter=letter['letter'],
                center=letter['center'],
                height=letter['height'],
                letter_color=letter['letter_color'],
            )
        # Draw subdivision lines in right segment (if enabled)
        if elements.get('draw_subdivisions', True):
            for line in elements['subdivision_lines']:
                image = add_arrowed_line(
                    image,
                    line_color=line['color'],
                    start_point=line['start'],
                    end_point=line['end'],
                    line_width=line['width'],
                    arrow_start='none',
                    arrow_end='none',
                    arrow_length=0,
                    antialias=False,
                )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update visual guide positions based on current segment lengths.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide positions
        """
        # Visual guides are positioned at the three boundary lines
        # No need to update if boundary positions are already stored
        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add visual guide markers to show segment boundaries.

        Three short vertical markers are drawn at the top:
        - Left boundary marker
        - Center boundary marker
        - Right boundary marker
        Plus one horizontal line connecting all three markers.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with visual guides added
        """
        guide_top_y = self.GUIDE_Y
        guide_bottom_y = self.GUIDE_Y + self.GUIDE_TICK_HEIGHT
        guide_middle_y = self.GUIDE_Y + self.GUIDE_TICK_HEIGHT // 2

        # Three short vertical markers
        for boundary_key, x_key in [
            ('left', 'left_boundary_x'),
            ('center', 'center_boundary_x'),
            ('right', 'right_boundary_x')
        ]:
            x = elements[x_key]
            image = add_arrowed_line(
                image,
                line_color=self.LINE_COLOR,
                start_point=(x, guide_top_y),
                end_point=(x, guide_bottom_y),
                line_width=self.LINE_WIDTH,
                arrow_start='none',
                arrow_end='none',
                arrow_length=0,
                antialias=False,
            )

        # Horizontal connecting line
        image = add_arrowed_line(
            image,
            line_color=self.LINE_COLOR,
            start_point=(elements['left_boundary_x'], guide_middle_y),
            end_point=(elements['right_boundary_x'], guide_middle_y),
            line_width=self.LINE_WIDTH,
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
            antialias=False,
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing subdivision lines.

        In the control condition, only the three boundary lines are shown,
        making it clear both segments are equal (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no subdivision lines
        """
        # Disable drawing of subdivision lines
        elements['draw_subdivisions'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by varying only the right segment length.

        The perturbation logic:
        - Left segment: Fixed at default length
        - Right segment: Length varies with strength parameter

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
