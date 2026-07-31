"""Irradiation Illusion (length, VI-Probe case 10). Light areas appear larger than dark areas of the same physical size."""

from typing import Any, Dict

import numpy as np

from core.draw import add_arrowed_line, add_rectangle
from core.template import IllusionTemplate


class IrradiationIllusion(IllusionTemplate):
    """
    Irradiation Illusion Generator

    Generates the classic Irradiation illusion with:
    - White rectangle on black background (appears larger)
    - Black rectangle on white background (appears smaller)
    - Both rectangles are actually the same size

    The strength parameter controls rectangle size via scaling:
    - strength = 0.4: size = DEFAULT * 0.4
    - strength = 1.0: size = DEFAULT * 1.0
    - strength = 1.6: size = DEFAULT * 1.6

    Rectangle size calculation:
        width = DEFAULT_RECT_WIDTH * strength
        height = DEFAULT_RECT_HEIGHT * strength
    """

    def __init__(self, DEFAULT_RECT_WIDTH=128, DEFAULT_RECT_HEIGHT=128):
        # For 512px width, default rectangle is WIDTH // 4 = 128px
        # For 256px height, default rectangle is HEIGHT // 2 = 128px
        self.DEFAULT_RECT_WIDTH = DEFAULT_RECT_WIDTH
        self.DEFAULT_RECT_HEIGHT = DEFAULT_RECT_HEIGHT

        # Color configuration
        self.BLACK = (0, 0, 0)
        self.WHITE = (1, 1, 1)

        # Left side configuration (white on black)
        self.LEFT_CENTER_X_RATIO = 1 / 4  # x = WIDTH / 4

        # Right side configuration (black on white)
        self.RIGHT_CENTER_X_RATIO = 3 / 4  # x = 3 * WIDTH / 4

        super().__init__(
            illusion_name="irradiation",
            width=512,
            height=256,
            strength_levels=[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_rect_size(self, strength: float) -> tuple:
        """
        Calculate rectangle size from strength using scaling.

        Args:
            strength: Scaling factor (e.g., 1.0 = default size, 1.5 = 150% of default)

        Returns:
            Tuple of (width, height) in pixels
        """
        width = self.DEFAULT_RECT_WIDTH * strength
        height = self.DEFAULT_RECT_HEIGHT * strength
        return (int(round(width)), int(round(height)))

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Irradiation illusion elements.

        For Original variation:
            - Both rectangles have the same size (determined by strength)
        For Perturbed variation:
            - Left rectangle size varies with strength
            - Right rectangle fixed at default size

        Args:
            strength: Controls rectangle size (scaling factor)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing background areas and rectangles
        """
        self.strength = strength

        # Calculate rectangle sizes
        if is_original:
            rect_width, rect_height = self._calculate_rect_size(strength)
            left_rect_width = rect_width
            left_rect_height = rect_height
            right_rect_width = rect_width
            right_rect_height = rect_height
        else:
            # Perturbed: right fixed at default, left varies
            left_rect_width, left_rect_height = self._calculate_rect_size(strength)
            right_rect_width = self.DEFAULT_RECT_WIDTH
            right_rect_height = self.DEFAULT_RECT_HEIGHT

        # Calculate positions
        center_y = self.height // 2
        left_center_x = int(self.width * self.LEFT_CENTER_X_RATIO)   # 128px
        right_center_x = int(self.width * self.RIGHT_CENTER_X_RATIO) # 384px

        elements = {
            # Left background (black, full height)
            'background_left': {
                'center': (self.width // 4, self.height // 2),
                'width': self.width // 2,  # 256px
                'height': self.height,     # 256px
                'color': self.BLACK,
            },

            # Right background (white, full height)
            'background_right': {
                'center': (self.width * 3 // 4, self.height // 2),
                'width': self.width // 2,  # 256px
                'height': self.height,     # 256px
                'color': self.WHITE,
            },

            # Left rectangle (white on black background)
            'rect_left': {
                'center': (left_center_x, center_y),
                'width': left_rect_width,
                'height': left_rect_height,
                'color': self.WHITE,
            },

            # Right rectangle (black on white background)
            'rect_right': {
                'center': (right_center_x, center_y),
                'width': right_rect_width,
                'height': right_rect_height,
                'color': self.BLACK,
            },

            # Visual guide lines
            'guide_lines': {
                'top_y': center_y - left_rect_height // 2,
                'bottom_y': center_y + left_rect_height // 2,
            },

            # Flag to control whether background colors should be drawn
            'draw_backgrounds': True,

            # Store parameters for later use
            'left_rect_width': left_rect_width,
            'left_rect_height': left_rect_height,
            'right_rect_width': right_rect_width,
            'right_rect_height': right_rect_height,
            'center_y': center_y,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Irradiation illusion on the canvas.

        Order of drawing:
        1. Background areas (if enabled)
        2. Left rectangle (white on black)
        3. Right rectangle (black on white)

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw background areas first (if enabled)
        if elements.get('draw_backgrounds', True):
            # Left background (black)
            image = add_rectangle(
                image,
                rect_color=elements['background_left']['color'],
                rect_center=elements['background_left']['center'],
                rect_width=elements['background_left']['width'],
                rect_height=elements['background_left']['height'],
                antialias=False,
            )

            # Right background (white)
            image = add_rectangle(
                image,
                rect_color=elements['background_right']['color'],
                rect_center=elements['background_right']['center'],
                rect_width=elements['background_right']['width'],
                rect_height=elements['background_right']['height'],
                antialias=False,
            )

        # Draw rectangles on top
        # Left rectangle (white)
        image = add_rectangle(
            image,
            rect_color=elements['rect_left']['color'],
            rect_center=elements['rect_left']['center'],
            rect_width=elements['rect_left']['width'],
            rect_height=elements['rect_left']['height'],
            antialias = False,
        )

        # Right rectangle (black)
        image = add_rectangle(
            image,
            rect_color=elements['rect_right']['color'],
            rect_center=elements['rect_right']['center'],
            rect_width=elements['rect_right']['width'],
            rect_height=elements['rect_right']['height'],
            antialias = False,
        )

        return image

    def update_visual_guides(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update guide line positions based on current left rectangle.

        Args:
            elements: Current element parameters
        Returns:
            Updated elements with guide line positions
        """
        center_y = elements['center_y']
        left_height = elements['left_rect_height']

        elements['guide_lines']['top_y'] = center_y - left_height // 2
        elements['guide_lines']['bottom_y'] = center_y + left_height // 2

        return elements

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal guide lines spanning the full width.

        Two dashed horizontal lines are drawn:
        - Top line: At the top edge of the left rectangle
        - Bottom line: At the bottom edge of the left rectangle

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide lines added
        """
        elements = self.update_visual_guides(elements)

        guide_color = (1, 0, 0)  # Red
        guide_width = 1

        # Top horizontal guide line
        image = add_arrowed_line(
            image,
            line_color=guide_color,
            start_point=(0, elements['guide_lines']['top_y']),
            end_point=(self.width, elements['guide_lines']['top_y']),
            line_width=guide_width,
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
            dashed=True,
            antialias=False,
        )

        # Bottom horizontal guide line
        image = add_arrowed_line(
            image,
            line_color=guide_color,
            start_point=(0, elements['guide_lines']['bottom_y']),
            end_point=(self.width, elements['guide_lines']['bottom_y']),
            line_width=guide_width,
            arrow_start='none',
            arrow_end='none',
            arrow_length=0,
            dashed=True,
            antialias=False,
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing colored backgrounds.

        In the control condition, both rectangles are shown as black on white background,
        making it clear they are the same size (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no colored backgrounds
        """
        # Disable drawing of colored backgrounds
        elements['draw_backgrounds'] = False

        # Change left rectangle to black (instead of white)
        elements['rect_left']['color'] = self.BLACK

        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version by varying only the left rectangle size.

        The perturbation logic:
        - Left rectangle: Size varies with strength parameter
        - Right rectangle: Fixed at default size

        This is already handled in define_elements() when is_original=False,
        so this method doesn't need to modify anything.

        Args:
            elements: Original elements (with right fixed, left variable)

        Returns:
            Unmodified elements (perturbation logic already applied)
        """
        # Perturbation logic is already handled in define_elements()
        # No additional modifications needed
        return elements
