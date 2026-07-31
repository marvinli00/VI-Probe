"""Zollner Illusion Vertical (orientation, VI-Probe case 22).

Vertical parallel lines crossed by alternating diagonal hash marks appear
tilted although they are perfectly vertical.
"""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line
from core.template import IllusionTemplate


class ZollnerIllusionVertical(IllusionTemplate):
    """
    Zöllner Illusion Generator (Vertical Version)

    Generates the vertical version of Zöllner illusion with:
    - Multiple vertical parallel lines with alternating diagonal hash marks
    - Lines appear tilted but are actually vertical (in original mode)

    The strength parameter has dual meaning:
    - Original mode: Controls hash mark angle (angle = 45 * strength degrees)
    - Perturbed mode: Controls actual line tilt (tilt = 3 * (strength - 1.0) degrees)
      - strength = 1.0: Vertical lines (baseline)
      - strength > 1.0: Alternating tilt
      - strength < 1.0: Reduced tilt
    """

    def __init__(self,
                 NUM_PARALLEL_LINES: int = 6,
                 NUM_HASH_MARKS_PER_LINE: int = 10):
        # Image dimensions
        WIDTH = 512
        HEIGHT = 512

        # Vertical parallel lines configuration
        self.NUM_PARALLEL_LINES = NUM_PARALLEL_LINES
        self.PARALLEL_LINE_COLOR = (1, 0, 0)  # Red
        self.PARALLEL_LINE_WIDTH = 2
        self.LINE_START_Y = 50
        self.LINE_END_Y = HEIGHT - 50
        self.HORIZONTAL_SPACING = WIDTH // (NUM_PARALLEL_LINES + 1)

        # Hash marks configuration
        self.NUM_HASH_MARKS_PER_LINE = NUM_HASH_MARKS_PER_LINE
        self.HASH_MARK_COLOR = (0, 0, 0)  # Black
        self.HASH_MARK_WIDTH = 1
        self.HASH_MARK_LENGTH = 20  # pixels
        self.DEFAULT_HASH_ANGLE = 45  # degrees (relative to horizontal)

        # Tilt configuration (for perturbed mode)
        self.DEFAULT_TILT_ANGLE = 3  # degrees

        super().__init__(
            illusion_name="zollner_illusion_v",
            width=WIDTH,
            height=HEIGHT,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0)  # White background
        )

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Zöllner illusion (vertical version) elements in their base state.

        This method always defines vertical lines as STRAIGHT. Tilting
        will be applied later in apply_perturbation().

        For Original variation:
            - Hash mark angle varies with strength (angle = 45 * strength degrees)
        For Perturbed variation:
            - Hash mark angle is fixed at 45 degrees
            - Tilt angle = 3 * (strength - 1.0) degrees
              - strength=1.0 → tilt=0 (vertical, baseline)
              - strength>1.0 → tilt>0 (alternating tilt)
              - strength<1.0 → tilt<0 (reduced/reverse tilt)

        Args:
            strength: Controls hash angle (original) or tilt angle (perturbed)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing vertical lines configuration
        """
        self.strength = strength

        if is_original:
            # Original: Variable hash mark angle based on strength
            hash_mark_angle = self.DEFAULT_HASH_ANGLE * strength
            # Tilt not used (lines stay vertical)
            tilt_angle = 0
        else:
            # Perturbed: Fixed hash mark angle, calculate tilt
            hash_mark_angle = self.DEFAULT_HASH_ANGLE
            # strength=1.0 → vertical (tilt=0)
            # strength>1.0 → alternating tilt (tilt>0)
            # strength<1.0 → reduced tilt (tilt<0)
            tilt_angle = self.DEFAULT_TILT_ANGLE * (strength - 1.0)

        # Define all vertical parallel lines
        parallel_lines = []
        for i in range(self.NUM_PARALLEL_LINES):
            x_position = self.HORIZONTAL_SPACING * (i + 1)

            # Hash marks alternate in angle: even columns +angle, odd columns -angle
            current_hash_angle = hash_mark_angle if i % 2 == 0 else -hash_mark_angle

            line_config = {
                'index': i,
                'x': x_position,
                'start_y': self.LINE_START_Y,
                'end_y': self.LINE_END_Y,
                'color': self.PARALLEL_LINE_COLOR,
                'width': self.PARALLEL_LINE_WIDTH,
                'is_tilted': False,  # Always vertical in base definition
                'tilt_angle': 0,  # Will be set by apply_perturbation()
                'hash_angle': current_hash_angle,  # Alternating angle
                'num_hash_marks': self.NUM_HASH_MARKS_PER_LINE,
                'draw_hash_marks': True,  # Control will set to False
            }
            parallel_lines.append(line_config)

        elements = {
            'parallel_lines': parallel_lines,
            'tilt_angle': tilt_angle,  # Store for apply_perturbation()
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Zöllner illusion (vertical version) on the canvas.

        Order of drawing:
        1. All vertical parallel lines
        2. Hash marks on each line (if enabled)

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw each vertical line with its hash marks
        for line_config in elements['parallel_lines']:
            image = self._draw_vertical_line_with_hashes(image, line_config)

        return image

    def _draw_vertical_line_with_hashes(self, image: np.ndarray,
                                        line_config: Dict[str, Any]) -> np.ndarray:
        """
        Draw a single vertical line with its hash marks.

        Args:
            image: Current image
            line_config: Line configuration dictionary

        Returns:
            Image with line and hash marks drawn
        """
        x_pos = line_config['x']
        start_y = line_config['start_y']
        end_y = line_config['end_y']
        color = line_config['color']
        width = line_config['width']
        is_tilted = line_config['is_tilted']
        tilt_angle = line_config['tilt_angle']

        # Calculate main line endpoints
        if not is_tilted:
            # Straight vertical line
            start_point = (x_pos, start_y)
            end_point = (x_pos, end_y)
        else:
            # Tilted line (tilts left-right)
            line_length = end_y - start_y
            tilt_rad = np.radians(tilt_angle)
            dx = line_length * np.tan(tilt_rad) / 2
            # Top tilts left, bottom tilts right (for positive tilt_angle)
            start_point = (int(x_pos - dx), start_y)
            end_point = (int(x_pos + dx), end_y)

        # Draw main vertical line (RED)
        image = add_arrowed_line(
            image,
            line_color=color,
            start_point=start_point,
            end_point=end_point,
            line_width=width,
            arrow_start='none',
            arrow_end='none',
            antialias=True
        )

        # Draw hash marks if enabled
        if line_config['draw_hash_marks']:
            num_hash_marks = line_config['num_hash_marks']
            hash_angle = line_config['hash_angle']

            for i in range(num_hash_marks):
                # Calculate position along the line
                t = (i + 1) / (num_hash_marks + 1)
                center_y = int(start_y + t * (end_y - start_y))

                if not is_tilted:
                    center_x = x_pos
                else:
                    # Interpolate x position along tilted line
                    center_x = int(start_point[0] + t * (end_point[0] - start_point[0]))

                # Calculate hash mark endpoints
                # Hash marks are centered on the main line
                # Angle is relative to horizontal axis
                hash_rad = np.radians(hash_angle)
                dx = (self.HASH_MARK_LENGTH / 2) * np.cos(hash_rad)
                dy = (self.HASH_MARK_LENGTH / 2) * np.sin(hash_rad)

                hash_start = (int(center_x - dx), int(center_y - dy))
                hash_end = (int(center_x + dx), int(center_y + dy))

                image = add_arrowed_line(
                    image,
                    line_color=self.HASH_MARK_COLOR,
                    start_point=hash_start,
                    end_point=hash_end,
                    line_width=self.HASH_MARK_WIDTH,
                    arrow_start='none',
                    arrow_end='none',
                    antialias=True
                )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add visual guide lines to mark the first and last vertical line positions.

        Draws two dashed gray vertical lines:
        - Left guide at the first vertical line
        - Right guide at the last vertical line

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide lines added
        """
        GUIDE_COLOR = (0.5, 0.5, 0.5)  # Gray
        GUIDE_WIDTH = 1

        parallel_lines = elements['parallel_lines']

        # Left guide (at first line)
        first_x = parallel_lines[0]['x']
        image = add_arrowed_line(
            image,
            line_color=GUIDE_COLOR,
            start_point=(first_x, 0),
            end_point=(first_x, self.height),
            line_width=GUIDE_WIDTH,
            arrow_start='none',
            arrow_end='none',
            dashed=True,
            antialias=True
        )

        # Right guide (at last line)
        last_x = parallel_lines[-1]['x']
        image = add_arrowed_line(
            image,
            line_color=GUIDE_COLOR,
            start_point=(last_x, 0),
            end_point=(last_x, self.height),
            line_width=GUIDE_WIDTH,
            arrow_start='none',
            arrow_end='none',
            dashed=True,
            antialias=True
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing hash marks.

        In the control condition, only vertical lines are shown without hash marks,
        making it clear that they are actually vertical (no illusion effect).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no hash marks
        """
        for line_config in elements['parallel_lines']:
            line_config['draw_hash_marks'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply perturbation by tilting the vertical lines.

        This method modifies the vertical lines defined in define_elements()
        to have alternating tilts. The tilt angle is determined by the strength
        parameter (stored in elements['tilt_angle']).

        Perturbation effects (alternating tilt):
        - Even-indexed lines: Tilt right by +tilt_angle (top left, bottom right)
        - Odd-indexed lines: Tilt left by -tilt_angle (top right, bottom left)
        - Tilt angle = 3 * (strength - 1.0) degrees

        Args:
            elements: Elements with vertical lines from define_elements()

        Returns:
            Modified elements with tilted vertical lines
        """
        # Get the stored tilt angle
        tilt_angle = elements.get('tilt_angle', 0)

        # Apply alternating tilt to vertical lines
        for line_config in elements['parallel_lines']:
            line_index = line_config['index']

            # Enable tilting
            line_config['is_tilted'] = True

            # Alternating tilt: even columns +tilt, odd columns -tilt
            current_tilt = tilt_angle if line_index % 2 == 0 else -tilt_angle
            line_config['tilt_angle'] = current_tilt

        return elements
