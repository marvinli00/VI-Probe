"""Poggendorff Horizontal Illusion (orientation, VI-Probe case 28).

The Poggendorff illusion demonstrates misperception of collinearity when a diagonal line
is interrupted by parallel occluding bars. The two segments of the diagonal line appear
misaligned, even though they are perfectly collinear.

Horizontal Version Setup:
- Two parallel HORIZONTAL bars (black rectangles) acting as occluders
- A diagonal line (red) passing behind the occluders
- The line segments appear misaligned, but are actually continuous

Variations:
- Control: Remove occluders (no illusion, line appears continuous)
- Original: Classic Poggendorff with diagonal line interrupted by occluders
- Perturbed: Upper segment actually offset rightward by 15px (breaking collinearity)

Strength levels (0.4 to 1.6): Control diagonal line angle
- strength = 0.4: angle = 20 degrees
- strength = 1.0: angle = 30 degrees (default)
- strength = 1.6: angle = 40 degrees
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_rectangle
from core.template import IllusionTemplate


class PoggendorffHorizontalIllusion(IllusionTemplate):
    """
    Poggendorff Horizontal Illusion Generator

    Generates the Poggendorff illusion with HORIZONTAL occluders:
    - Two parallel horizontal bars as occluders
    - A diagonal line interrupted by the occluders
    - Optional confusion line for comparison

    The strength parameter controls the diagonal angle:
    - strength = 0.4: angle = 20 degrees
    - strength = 1.0: angle = 30 degrees
    - strength = 1.6: angle = 40 degrees

    Angle calculation:
        angle = 20 + strength * 25
    """

    def __init__(self, horizontal_offset=0):
        self.horizontal_offset = horizontal_offset

        # Occluder configuration (two parallel HORIZONTAL bars)
        self.OCCLUDER_SPACING = 60        # Vertical distance between two parallel horizontal bars
        self.OCCLUDER_LINE_WIDTH = 3      # Width of occluding lines
        self.OCCLUDER_LENGTH = 300        # Horizontal length of occluding bars
        self.OCCLUDER_COLOR = (0, 0, 0)   # Black

        # Diagonal line configuration
        self.DEFAULT_ANGLE = 30           # Default angle in degrees
        self.DIAGONAL_COLOR = (1, 0, 0)   # Red
        self.DIAGONAL_WIDTH = 3           # Width of diagonal line
        self.DIAGONAL_LENGTH = 400        # Total length of diagonal line

        # Confusion line configuration (for comparison)
        self.CONFUSION_COLOR = (0, 0, 1)  # Blue
        self.CONFUSION_OFFSET = 20        # Horizontal offset from main diagonal (left side)

        # Perturbation configuration
        self.PERTURB_OFFSET = 15          # pixels to offset upper segment (rightward)

        # Visual guide configuration
        self.GUIDE_COLOR = (1, 1, 1)      # White
        self.GUIDE_WIDTH = 1              # Thin guide lines
        self.GUIDE_EXTENSION = 100        # Extension length beyond diagonal

        super().__init__(
            illusion_name="poggendorff_horizontal",
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
        Define Poggendorff illusion elements (HORIZONTAL version).

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
            # Perturbed mode: use fixed default angle (30 degrees)
            angle_deg = self.DEFAULT_ANGLE
        angle_rad = np.radians(angle_deg)

        # Center positions
        center_x = self.width // 2
        center_y = self.height // 2

        # Two parallel HORIZONTAL lines (occluders)
        top_line_y = center_y - self.OCCLUDER_SPACING // 2
        bottom_line_y = center_y + self.OCCLUDER_SPACING // 2
        occluder_left_x = center_x - self.OCCLUDER_LENGTH // 2
        occluder_right_x = center_x + self.OCCLUDER_LENGTH // 2

        # Diagonal line - one continuous line from lower-left to upper-right
        diagonal_start_x = center_x - self.DIAGONAL_LENGTH // 2 * np.cos(angle_rad) + self.horizontal_offset
        diagonal_start_y = center_y + self.DIAGONAL_LENGTH // 2 * np.sin(angle_rad)
        diagonal_end_x = center_x + self.DIAGONAL_LENGTH // 2 * np.cos(angle_rad) + self.horizontal_offset
        diagonal_end_y = center_y - self.DIAGONAL_LENGTH // 2 * np.sin(angle_rad)

        # Calculate where diagonal crosses the HORIZONTAL occluders
        # For horizontal line at y = bottom_line_y, solve for x
        # y = diagonal_start_y + t * (diagonal_end_y - diagonal_start_y)
        # When y = bottom_line_y, solve for t, then get x
        t_bottom = (bottom_line_y - diagonal_start_y) / (diagonal_end_y - diagonal_start_y)
        cross_x_bottom = diagonal_start_x + t_bottom * (diagonal_end_x - diagonal_start_x)

        # Calculate where diagonal crosses the top occluder (for confusion line)
        t_top = (top_line_y - diagonal_start_y) / (diagonal_end_y - diagonal_start_y)
        cross_x_top = diagonal_start_x + t_top * (diagonal_end_x - diagonal_start_x)

        elements = {
            # Occluder rectangle (black horizontal bar in the middle)
            'occluder': {
                'center': ((occluder_left_x + occluder_right_x) // 2, (top_line_y + bottom_line_y) // 2),
                'width': occluder_right_x - occluder_left_x,  # Horizontal length
                'height': bottom_line_y - top_line_y,  # Vertical spacing
                'color': self.OCCLUDER_COLOR,
            },

            # Main diagonal line
            'diagonal': {
                'start': (int(diagonal_start_x), int(diagonal_start_y)),
                'end': (int(diagonal_end_x), int(diagonal_end_y)),
                'color': self.DIAGONAL_COLOR,
                'width': self.DIAGONAL_WIDTH,
            },

            # Bottom part of diagonal (below bottom occluder)
            'diagonal_bottom': {
                'start': (int(diagonal_start_x), int(diagonal_start_y)),
                'end': (int(cross_x_bottom), int(bottom_line_y)),
                'color': self.DIAGONAL_COLOR,
                'width': self.DIAGONAL_WIDTH,
            },

            # Top part of diagonal (above top occluder)
            'diagonal_top': {
                'start': (int(cross_x_top), int(top_line_y)),
                'end': (int(diagonal_end_x), int(diagonal_end_y)),
                'color': (0, 0, 0),  # Black for top segment
                'width': self.DIAGONAL_WIDTH,
            },

            # Confusion line (blue reference line on left side, ends at bottom occluder)
            'confusion_line': {
                'start': (int(diagonal_start_x) - self.CONFUSION_OFFSET, int(diagonal_start_y)),
                'end': (int(cross_x_bottom) - self.CONFUSION_OFFSET, int(bottom_line_y)),
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
        Draw the Poggendorff illusion on the canvas (horizontal version).

        Order of drawing:
        1. Diagonal line (split into bottom red + top black segments)
        2. Confusion line (blue reference)
        3. Occluder rectangle (if enabled, drawn on top)

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw diagonal line as split segments (bottom red, top black)
        # All modes use red-black split segments
        # Draw bottom part (red)
        # Adjust the end point to retract 5 pixels along the diagonal
        angle_rad = elements['angle_rad']
        red_end_x = elements['diagonal_bottom']['end'][0] - 3 * np.cos(angle_rad)
        red_end_y = elements['diagonal_bottom']['end'][1] + 3 * np.sin(angle_rad)

        image = add_arrowed_line(
            image,
            line_color=elements['diagonal_bottom']['color'],
            start_point=elements['diagonal_bottom']['start'],
            end_point=(int(red_end_x), int(red_end_y)),
            line_width=elements['diagonal_bottom']['width'],
            arrow_start='none',
            arrow_end='none',
            antialias=True,
        )

        # Draw top part (black)
        image = add_arrowed_line(
            image,
            line_color=elements['diagonal_top']['color'],
            start_point=elements['diagonal_top']['start'],
            end_point=elements['diagonal_top']['end'],
            line_width=elements['diagonal_top']['width'],
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

        Extends the diagonal line with dashed red lines.

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

        # Calculate the y-coordinate of the bottom edge of occluder (color split point)
        occluder = elements['occluder']
        occluder_center_y = occluder['center'][1]
        occluder_height = occluder['height']
        bottom_edge_y = occluder_center_y + occluder_height / 2

        # Calculate the intersection point where the guide line crosses the bottom edge
        # Using parametric line equation: y = y1 + t*(y2-y1), x = x1 + t*(x2-x1)
        # Solve for t when y = bottom_edge_y
        t = (bottom_edge_y - guide_start_y) / (guide_end_y - guide_start_y)
        intersection_x = guide_start_x + t * (guide_end_x - guide_start_x)

        # Draw bottom segment (red dashed line)
        image = add_arrowed_line(
            image,
            line_color=(1, 0, 0),  # Red
            start_point=(int(guide_start_x), int(guide_start_y)),
            end_point=(int(intersection_x), int(bottom_edge_y)),
            line_width=self.GUIDE_WIDTH,
            arrow_start='none',
            arrow_end='none',
            dashed=True,
            dash_length=10,
            gap_length=5,
            antialias=True,
        )

        # Draw top segment (red dashed line)
        image = add_arrowed_line(
            image,
            line_color=(1, 0, 0),  # Red
            start_point=(int(intersection_x), int(bottom_edge_y)),
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
        Create perturbed version by horizontally offsetting the top segment.

        The top segment is shifted horizontally based on strength:
        - strength = 0.5: 50 pixels leftward
        - strength = 1.0: no offset
        - strength = 1.5: 50 pixels rightward

        Args:
            elements: Original elements

        Returns:
            Modified elements with top segment offset
        """
        # Enable perturbation flag
        elements['is_perturbed'] = True

        # Calculate horizontal offset from strength
        # Formula: horizontal_offset = (strength - 1.0) * 100
        # strength = 0.5 → -50 (leftward), 1.0 → 0, 1.5 → +50 (rightward)
        horizontal_offset = (self.strength - 1.0) * 80

        # Offset the top diagonal segment horizontally
        elements['diagonal_top']['start'] = (
            elements['diagonal_top']['start'][0] + horizontal_offset,
            elements['diagonal_top']['start'][1]
        )
        elements['diagonal_top']['end'] = (
            elements['diagonal_top']['end'][0] + horizontal_offset,
            elements['diagonal_top']['end'][1]
        )

        return elements
