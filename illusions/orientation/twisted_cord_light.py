"""Twisted Cord Illusion Light (orientation, VI-Probe case 26). Low-contrast gray variant: straight vertical poles filled with diagonal gray stripes appear twisted or spiral-shaped like twisted cords."""

from typing import Any, Dict, List, Tuple

import numpy as np

from core.draw import add_rotated_rectangle_sr
from core.template import IllusionTemplate


class TwistedCordIllusionLight(IllusionTemplate):
    """
    Twisted Cord Illusion Generator - Light Version

    Generates the twisted cord illusion using straight vertical poles filled with
    diagonal stripes in low-contrast gray tones.

    The strength parameter = stripe width multiplier:
    - strength = 0.5: Thin stripes (5px)
    - strength = 1.0: Standard stripes (10px)
    - strength = 2.0: Thick stripes (20px)
    """

    def __init__(self,
                 NUM_CORDS: int = 2,
                 CORD_WIDTH: int = 60,
                 STRIPE_WIDTH: int = 10,
                 SR_FACTOR: int = 4):
        # Image dimensions
        WIDTH = 512
        HEIGHT = 512
        self.width = WIDTH
        self.height = HEIGHT

        # Cord (pole) configuration
        self.NUM_CORDS = NUM_CORDS
        self.CORD_WIDTH = CORD_WIDTH
        self.CORD_HEIGHT = int(HEIGHT * 0.9)  # 90% of canvas height

        # Calculate cord spacing to center them
        if NUM_CORDS == 1:
            self.CORD_SPACING = 0
        else:
            total_cord_width = NUM_CORDS * CORD_WIDTH
            available_space = WIDTH - total_cord_width
            self.CORD_SPACING = available_space // (NUM_CORDS + 1)

        # Stripe configuration - LIGHT VERSION with gray tones
        self.BASE_STRIPE_WIDTH = STRIPE_WIDTH  # Base stripe width
        self.STRIPE_WIDTH = STRIPE_WIDTH  # Keep for backward compatibility
        self.DARK_GRAY_COLOR = (0.3, 0.3, 0.3)   # Deep gray for dark stripes
        self.LIGHT_GRAY_COLOR = (0.7, 0.7, 0.7)  # Light gray for bright stripes
        self.GROUND_COLOR = (0.3, 0.3, 0.3)      # Deep gray for ground line

        # Rendering configuration
        self.SR_FACTOR = SR_FACTOR  # Super-resolution factor for anti-aliasing

        # Starting position (center vertically)
        self.START_X = self.CORD_SPACING + CORD_WIDTH // 2
        self.START_Y = (HEIGHT - self.CORD_HEIGHT) // 2 + self.CORD_HEIGHT // 2

        super().__init__(
            illusion_name="twisted_cord_illusion_light",
            width=WIDTH,
            height=HEIGHT,
            strength_levels=[0.5, 0.8, 1.0, 1.2, 1.5, 2.0],  # Stripe width multipliers
            background_color=(0.5, 0.5, 0.5)  # Medium gray background
        )

    def generate_stripe_pattern(self,
                                width: int,
                                height: int,
                                stripe_width: int,
                                angle: float,
                                colors: List[Tuple[float, float, float]]) -> np.ndarray:
        """
        Generate a diagonal stripe pattern.

        The pattern consists of alternating colored stripes at a specified angle.
        The stripes are perpendicular to the angle direction.

        Args:
            width: Pattern width in pixels
            height: Pattern height in pixels
            stripe_width: Width of each stripe in pixels
            angle: Angle of the stripes in degrees (0° = vertical, 90° = horizontal)
            colors: List of colors to alternate (deep gray + light gray)

        Returns:
            Color array of shape (height, width, 3) with diagonal stripe pattern
        """
        pattern = np.zeros((height, width, 3), dtype=np.float32)
        angle_rad = np.radians(angle)

        # For each pixel, calculate which stripe it belongs to
        for row in range(height):
            for col in range(width):
                # Calculate the perpendicular distance from origin along the stripe direction
                # This determines which stripe the pixel belongs to
                # Using: projection = x * cos(θ) + y * sin(θ)
                projection = col * np.cos(angle_rad) + row * np.sin(angle_rad)

                # Determine stripe index
                stripe_index = int(projection / stripe_width) % len(colors)
                pattern[row, col] = colors[stripe_index]

        return pattern

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define twisted cord illusion elements.

        Logic:
        - Control mode: vertical poles (0°) + vertical stripes (0°), strength controls stripe width
        - Original mode: vertical poles (0°) + 45° diagonal stripes, strength controls stripe width
        - Perturbed mode: tilted poles (±strength°) + 45° diagonal stripes, strength controls pole rotation

        Args:
            strength:
                - For Control/Original: stripe width multiplier (e.g., 1.0 = 10px, 2.0 = 20px)
                - For Perturbed: pole rotation angle in degrees (0°-15°)
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing cord configurations
        """
        self.strength = strength

        if is_original:
            # Original mode: vertical poles + 45° diagonal stripes, strength controls stripe width
            stripe_angle = 45.0  # Fixed 45° diagonal stripes
            stripe_width = int(self.BASE_STRIPE_WIDTH * strength)
            cord_rotation = 0  # Poles don't rotate
        else:
            # Perturbed mode: tilted poles + 45° diagonal stripes, strength controls pole rotation
            stripe_angle = 45.0  # Fixed 45° diagonal stripes
            stripe_width = self.BASE_STRIPE_WIDTH  # Fixed stripe width
            cord_rotation = -(self.strength - 1.0)*10  # strength controls pole rotation angle

        # Pre-generate base stripe pattern for efficiency (will be flipped for second cord)
        base_stripe_pattern = self.generate_stripe_pattern(
            width=self.CORD_WIDTH,
            height=self.CORD_HEIGHT,
            stripe_width=stripe_width,
            angle=stripe_angle,
            colors=[self.DARK_GRAY_COLOR, self.LIGHT_GRAY_COLOR]
        )

        # Define cord configurations
        cords = []
        for i in range(self.NUM_CORDS):
            cord_center_x = self.START_X + i * (self.CORD_WIDTH + self.CORD_SPACING)

            # Use np.fliplr to mirror the stripe pattern for second cord (more efficient than recalculating)
            if i == 0:
                stripe_pattern = base_stripe_pattern  # First cord: original pattern
            else:
                stripe_pattern = np.fliplr(base_stripe_pattern)  # Second cord: horizontally flipped pattern

            # In Perturbed mode, two poles tilt in opposite directions (symmetric effect)
            if is_original:
                cord_rotation_angle = 0  # Original mode: poles don't rotate
            else:
                # Perturbed mode: symmetric tilting
                if i == 0:
                    cord_rotation_angle = cord_rotation  # First pole: clockwise rotation
                else:
                    cord_rotation_angle = -cord_rotation  # Second pole: counterclockwise rotation

            cord_config = {
                'cord_index': i,
                'center_x': cord_center_x,
                'center_y': self.START_Y,
                'stripe_pattern': stripe_pattern,  # Pre-generated pattern (original or flipped)
                'stripe_angle': stripe_angle,  # Keep for reference
                'stripe_width': stripe_width,
                'cord_rotation': cord_rotation_angle,  # Pole rotation angle
                'cord_width': self.CORD_WIDTH,
                'cord_height': self.CORD_HEIGHT,
            }
            cords.append(cord_config)

        elements = {
            'cords': cords,
            'stripe_angle': stripe_angle,
            'stripe_width': stripe_width,
        }

        return elements

    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the twisted cord illusion on the canvas.

        Draws each cord as a vertical rectangle filled with diagonal gray stripes,
        plus a horizontal ground line at the bottom.

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw each cord
        for cord_config in elements['cords']:
            image = self._draw_twisted_cord(image, cord_config)

        # Draw ground line (horizontal deep gray rectangle at the bottom of cords)
        ground_y = self.START_Y + self.CORD_HEIGHT // 2  # Bottom of cords
        ground_height = 10  # Ground line height in pixels

        # Ensure ground line stays within canvas bounds
        if ground_y + ground_height <= self.height:
            image[ground_y:ground_y + ground_height, :] = self.GROUND_COLOR

        return image

    def _draw_twisted_cord(self, image: np.ndarray,
                          cord_config: Dict[str, Any]) -> np.ndarray:
        """
        Draw a single twisted cord (pole with diagonal gray stripes).

        The pole can be rotated (in Perturbed mode) while maintaining the stripe pattern.

        Args:
            image: Current image
            cord_config: Cord configuration dictionary (includes pre-generated stripe_pattern)

        Returns:
            Image with cord drawn
        """
        center_x = cord_config['center_x']
        center_y = cord_config['center_y']
        cord_rotation = cord_config['cord_rotation']  # Pole rotation angle
        cord_width = cord_config['cord_width']
        cord_height = cord_config['cord_height']
        control_mode = cord_config.get('control_mode', False)

        # Use pre-generated stripe pattern (or solid gray for control mode)
        if control_mode:
            # Control mode: solid light gray rectangle
            stripe_pattern = np.ones((cord_height, cord_width, 3), dtype=np.float32) * 0.7
        else:
            # Normal mode: use pre-generated pattern from cord_config (already flipped if needed)
            stripe_pattern = cord_config['stripe_pattern']

        # Draw the cord as a rotated rectangle with the stripe pattern
        image = add_rotated_rectangle_sr(
            image,
            rect_color=stripe_pattern,
            rect_center=(center_x, center_y),
            rect_width=cord_width,
            rect_height=cord_height,
            rotation_angle=cord_rotation,  # Use pole rotation angle
            sr_factor=self.SR_FACTOR,
            antialias=True
        )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add visual guide markers to demonstrate that cord edges are straight.

        Draws red vertical lines along the left and right edges of each cord
        to prove that the edges are perfectly straight and parallel.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide lines added
        """
        # Guide line parameters
        GUIDE_COLOR = (1, 0, 0)  # Red
        GUIDE_WIDTH = 3  # pixels

        # Draw guide lines for each cord
        for cord_config in elements['cords']:
            center_x = cord_config['center_x']
            center_y = cord_config['center_y']
            cord_width = cord_config['cord_width']
            cord_height = cord_config['cord_height']

            # Calculate edge positions
            left_edge_x = int(center_x - cord_width / 2)
            right_edge_x = int(center_x + cord_width / 2)
            top_y = int(center_y - cord_height / 2)
            bottom_y = int(center_y + cord_height / 2)

            # Draw left edge guide line
            if left_edge_x - GUIDE_WIDTH >= 0:
                image[top_y:bottom_y, left_edge_x - GUIDE_WIDTH:left_edge_x] = GUIDE_COLOR

            # Draw right edge guide line
            if right_edge_x + GUIDE_WIDTH <= self.width:
                image[top_y:bottom_y, right_edge_x:right_edge_x + GUIDE_WIDTH] = GUIDE_COLOR

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition with vertical stripes and poles.

        In the control condition:
        - Pole rotation is set to 0° (vertical poles)
        - Stripe angle is set to 0° (vertical stripes)
        - Stripe width is controlled by strength (same as Original mode)
        - Creates baseline for comparison

        Args:
            elements: Original elements

        Returns:
            Modified elements with vertical stripes and poles
        """
        # Regenerate vertical stripe pattern for control mode
        stripe_width = elements['stripe_width']
        vertical_stripe_pattern = self.generate_stripe_pattern(
            width=self.CORD_WIDTH,
            height=self.CORD_HEIGHT,
            stripe_width=stripe_width,
            angle=0,  # Vertical stripes
            colors=[self.DARK_GRAY_COLOR, self.LIGHT_GRAY_COLOR]
        )
        vertical_stripe_pattern = np.zeros_like(vertical_stripe_pattern)
        # Set vertical stripes (0°) and no pole rotation for all cords
        for cord_config in elements['cords']:
            cord_config['stripe_angle'] = 0  # Vertical stripes
            # cord_config['cord_rotation'] = 0  # Vertical poles (no rotation)
            cord_config['stripe_pattern'] = vertical_stripe_pattern  # Use vertical pattern (same for both cords)
            # stripe_width remains as defined by strength in define_elements()

        elements['stripe_angle'] = 0

        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply perturbation by tilting poles symmetrically.

        The perturbed version tilts the poles in opposite directions,
        creating a symmetric visual effect.

        Args:
            elements: Elements with original configuration

        Returns:
            Modified elements (already set in define_elements for perturbed mode)
        """
        # Perturbation is already applied in define_elements()
        # (pole rotation for perturbed mode)
        return elements
