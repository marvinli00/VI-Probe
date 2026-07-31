"""Poggendorff Illusion (orientation, VI-Probe case 27).

The Poggendorff illusion demonstrates misperception of collinearity when a diagonal line
is interrupted by parallel occluding bars. The two segments of the diagonal line appear
misaligned, even though they are perfectly collinear.

Classic setup:
- Two parallel vertical bars (black rectangles) acting as occluders
- A diagonal line (red) passing behind the occluders
- The line segments appear misaligned, but are actually continuous

Variations:
- Control: Remove occluders (no illusion, line appears continuous)
- Original: Classic Poggendorff with diagonal line interrupted by occluders
- Perturbed: Right segment actually offset downward by 15px (breaking collinearity)

Strength levels (0.4 to 1.6): Control diagonal line angle
- strength = 0.4: angle = 20 degrees
- strength = 1.0: angle = 30 degrees (default)
- strength = 1.6: angle = 40 degrees
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_rectangle
from core.template import IllusionTemplate


class PoggendorffIllusion(IllusionTemplate):
    """
    Poggendorff Illusion Generator

    Generates the classic Poggendorff illusion with:
    - Two parallel vertical bars as occluders
    - A diagonal line interrupted by the occluders
    - Optional confusion line for comparison

    The strength parameter controls the diagonal angle:
    - strength = 0.4: angle = 20 degrees
    - strength = 1.0: angle = 30 degrees
    - strength = 1.6: angle = 40 degrees

    Angle calculation:
        angle = 20 + strength * 25
    """

    def __init__(self, vertical_offset = 0):
        self.vertical_offset = vertical_offset
        # Occluder configuration (two parallel vertical bars)
        self.OCCLUDER_SPACING = 60        # Distance between two parallel lines
        self.OCCLUDER_LINE_WIDTH = 3      # Width of occluding lines
        self.OCCLUDER_LENGTH = 300        # Length of occluding lines
        self.OCCLUDER_COLOR = (0, 0, 0)   # Black

        # Diagonal line configuration
        self.DEFAULT_ANGLE = 45           # Default angle in degrees
        self.DIAGONAL_COLOR = (1, 0, 0)   # Red
        self.DIAGONAL_WIDTH = 3           # Width of diagonal line
        self.DIAGONAL_LENGTH = 400        # Total length of diagonal line

        # Confusion line configuration (for comparison)
        self.CONFUSION_COLOR = (0, 0, 1)  # Blue
        self.CONFUSION_OFFSET = 20        # Vertical offset from main diagonal

        # Perturbation configuration
        self.PERTURB_OFFSET = 15          # pixels to offset right segment

        # Visual guide configuration
        self.GUIDE_COLOR = (1, 1, 1)      # White
        self.GUIDE_WIDTH = 1              # Thin guide lines
        self.GUIDE_EXTENSION = 100        # Extension length beyond diagonal

        super().__init__(
            illusion_name="poggendorff",
            width=512,
            height=512,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_angle(self, strength: float) -> float:
        """
        Calculate diagonal angle from strength.

        Args:
            strength: Scaling factor (0.4 to 1.6)

        Returns:
            Angle in degrees
        """
        # Linear mapping: strength 0.4→20°, 1.0→30°, 1.6→40°
        angle = 20 + strength * 25
        return angle

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Poggendorff illusion elements.

        Args:
            strength: Controls diagonal angle
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing all line positions and parameters
        """
        self.strength = strength

        # Calculate diagonal angle
        if is_original:
            # Original mode: strength controls angle
            angle_deg = self._calculate_angle(strength)
        else:
            # Perturbed mode: use fixed default angle (45 degrees)
            angle_deg = self.DEFAULT_ANGLE
        angle_rad = np.radians(angle_deg)

        # Center positions
        center_x = self.width // 2
        center_y = self.height // 2

        # Two parallel vertical lines (occluders)
        left_line_x = center_x - self.OCCLUDER_SPACING // 2
        right_line_x = center_x + self.OCCLUDER_SPACING // 2
        occluder_top_y = center_y - self.OCCLUDER_LENGTH // 2
        occluder_bottom_y = center_y + self.OCCLUDER_LENGTH // 2

        # Diagonal line - one continuous line from lower-left to upper-right
        diagonal_start_x = center_x - self.DIAGONAL_LENGTH // 2 * np.cos(angle_rad)
        diagonal_start_y = center_y + self.DIAGONAL_LENGTH // 2 * np.sin(angle_rad) + self.vertical_offset
        diagonal_end_x = center_x + self.DIAGONAL_LENGTH // 2 * np.cos(angle_rad)
        diagonal_end_y = center_y - self.DIAGONAL_LENGTH // 2 * np.sin(angle_rad) + self.vertical_offset

        # Calculate where diagonal crosses the occluders
        t_right = (right_line_x - diagonal_start_x) / (diagonal_end_x - diagonal_start_x)
        cross_y_right = diagonal_start_y + t_right * (diagonal_end_y - diagonal_start_y)

        # Calculate where diagonal crosses the left occluder (for confusion line)
        t_left = (left_line_x - diagonal_start_x) / (diagonal_end_x - diagonal_start_x)
        cross_y_left = diagonal_start_y + t_left * (diagonal_end_y - diagonal_start_y)

        elements = {
            # Occluder rectangle (black bar in the middle)
            'occluder': {
                'center': ((left_line_x + right_line_x) // 2, (occluder_top_y + occluder_bottom_y) // 2),
                'width': right_line_x - left_line_x,
                'height': occluder_bottom_y - occluder_top_y,
                'color': self.OCCLUDER_COLOR,
            },

            # Main diagonal line
            'diagonal': {
                'start': (int(diagonal_start_x), int(diagonal_start_y)),
                'end': (int(diagonal_end_x), int(diagonal_end_y)),
                'color': self.DIAGONAL_COLOR,
                'width': self.DIAGONAL_WIDTH,
            },

            # Left part of diagonal (for perturbed mode)
            'diagonal_left': {
                'start': (int(diagonal_start_x), int(diagonal_start_y)),
                'end': (int(right_line_x), int(cross_y_right)),
                'color': self.DIAGONAL_COLOR,
                'width': self.DIAGONAL_WIDTH,
            },

            # Right part of diagonal (for perturbed mode)
            'diagonal_right': {
                'start': (int(right_line_x), int(cross_y_right)),
                'end': (int(diagonal_end_x), int(diagonal_end_y)),
                'color': (0, 0, 0),  # Black for right segment
                'width': self.DIAGONAL_WIDTH,
            },

            # Confusion line (blue reference line above, ends at left occluder)
            'confusion_line': {
                'start': (int(diagonal_start_x), int(diagonal_start_y) - self.CONFUSION_OFFSET),
                'end': (int(left_line_x), int(cross_y_left) - self.CONFUSION_OFFSET),
                'color': self.CONFUSION_COLOR,
                'width': self.DIAGONAL_WIDTH,
            },

            # Flags and parameters
            'draw_occluder': True,
            'is_perturbed': False,
            'angle_deg': angle_deg,
            'angle_rad': angle_rad,
            'center_x': center_x,
            'center_y': center_y,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Poggendorff illusion on the canvas.

        Order of drawing:
        1. Diagonal line (split into left red + right black segments)
        2. Confusion line (blue reference)
        3. Occluder rectangle (if enabled, drawn on top)

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw diagonal line as split segments (left red, right black)
        # All modes use red-black split segments
        # Draw left part (red)
        # Adjust the right endpoint to retract 5 pixels along the diagonal
        angle_rad = elements['angle_rad']
        red_end_x = elements['diagonal_left']['end'][0] - 5 * np.cos(angle_rad)
        red_end_y = elements['diagonal_left']['end'][1] + 5 * np.sin(angle_rad)

        image = add_arrowed_line(
            image,
            line_color=elements['diagonal_left']['color'],
            start_point=elements['diagonal_left']['start'],
            end_point=(int(red_end_x), int(red_end_y)),
            line_width=elements['diagonal_left']['width'],
            arrow_start='none',
            arrow_end='none',
            antialias=True,
        )

        # Draw right part (black)
        image = add_arrowed_line(
            image,
            line_color=elements['diagonal_right']['color'],
            start_point=elements['diagonal_right']['start'],
            end_point=elements['diagonal_right']['end'],
            line_width=elements['diagonal_right']['width'],
            arrow_start='none',
            arrow_end='none',
            antialias=True,
        )

        # Draw occluder rectangle (on top, if enabled)
        if elements.get('draw_occluder', True):
            image = add_rectangle(
                image,
                rect_color=elements['occluder']['color'],
                rect_center=elements['occluder']['center'],
                rect_width=elements['occluder']['width'],
                rect_height=elements['occluder']['height'],
            )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add visual guide lines to show the true diagonal alignment.

        Extends the diagonal line with dashed lines: red on the left, black on the right.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with visual guides added
        """
        # Get diagonal parameters
        diagonal = elements['diagonal']
        angle_rad = elements['angle_rad']

        # Calculate extended line endpoints
        extension = self.GUIDE_EXTENSION
        start_x, start_y = diagonal['start']
        end_x, end_y = diagonal['end']

        # Extend at start
        guide_start_x = start_x - extension * np.cos(angle_rad)
        guide_start_y = start_y + extension * np.sin(angle_rad)

        # Extend at end
        guide_end_x = end_x + extension * np.cos(angle_rad)
        guide_end_y = end_y - extension * np.sin(angle_rad)

        # Calculate the x-coordinate of the right edge of occluder (color split point)
        occluder = elements['occluder']
        occluder_center_x = occluder['center'][0]
        occluder_width = occluder['width']
        right_edge_x = occluder_center_x + occluder_width / 2

        # Calculate the intersection point where the guide line crosses the right edge
        # Using parametric line equation: x = x1 + t*(x2-x1), y = y1 + t*(y2-y1)
        # Solve for t when x = right_edge_x
        t = (right_edge_x - guide_start_x) / (guide_end_x - guide_start_x)
        intersection_y = guide_start_y + t * (guide_end_y - guide_start_y)

        # Draw left segment (red dashed line)
        image = add_arrowed_line(
            image,
            line_color=(1, 0, 0),  # Red
            start_point=(int(guide_start_x), int(guide_start_y)),
            end_point=(int(right_edge_x), int(intersection_y)),
            line_width=self.GUIDE_WIDTH,
            arrow_start='none',
            arrow_end='none',
            dashed=True,
            dash_length=10,
            gap_length=5,
            antialias=True,
        )

        # Draw right segment (red dashed line)
        image = add_arrowed_line(
            image,
            line_color=(1, 0, 0),  # Red
            start_point=(int(right_edge_x), int(intersection_y)),
            end_point=(int(guide_end_x), int(guide_end_y)),
            line_width=self.GUIDE_WIDTH,
            arrow_start='none',
            arrow_end='none',
            dashed=True,
            dash_length=10,
            gap_length=5,
            antialias=True,
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing the occluder.

        In the control condition, the occluder is hidden, making it clear
        the diagonal line is continuous (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with occluder disabled
        """
        # Disable drawing of occluder
        elements['draw_occluder'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by vertically offsetting the right segment.

        The right segment is shifted vertically based on strength:
        - strength = 0.5: 40 pixels upward
        - strength = 1.0: no offset
        - strength = 1.5: 40 pixels downward

        Args:
            elements: Original elements

        Returns:
            Modified elements with right segment offset
        """
        # Enable perturbation flag
        elements['is_perturbed'] = True

        # Calculate vertical offset from strength
        # Formula: vertical_offset = (strength - 1.0) * 80
        # strength = 0.5 → -40 (upward), 1.0 → 0, 1.5 → +40 (downward)
        vertical_offset = (self.strength - 1.0) * 80

        # Offset the right diagonal segment vertically
        elements['diagonal_right']['start'] = (
            elements['diagonal_right']['start'][0],
            elements['diagonal_right']['start'][1] + vertical_offset
        )
        elements['diagonal_right']['end'] = (
            elements['diagonal_right']['end'][0],
            elements['diagonal_right']['end'][1] + vertical_offset
        )

        return elements
