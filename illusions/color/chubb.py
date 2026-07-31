"""Chubb Illusion (color, VI-Probe case 18).

The Chubb illusion (also called contrast-contrast illusion) demonstrates how the perceived
contrast of a pattern depends on the contrast of its surrounding context.

Classic setup:
- Left background: Uniform gray
- Right background: High-contrast random binary noise (black/white)
- Two circles with identical low-contrast binary noise texture
- Left circle appears to have lower contrast (on uniform background)
- Right circle appears to have higher contrast (on high-contrast background)
- They actually have the same contrast!

Variations:
- Control: Remove background patterns (circles clearly identical)
- Original: Both circles with same contrast varying with strength
- Perturbed: Left circle fixed, right circle contrast varies with strength

Strength system:
- Controls contrast of circle noise patterns
- Uses midpoint-preserving contrast adjustment:
  - mid = (BASE_LOW + BASE_HIGH) / 2
  - low_val = mid - strength × contrast_range
  - high_val = mid + strength × contrast_range
- Keeps average brightness constant while changing contrast
"""

from typing import Any, Dict, Tuple

import numpy as np

from core.draw import add_rectangle, hsl_to_rgb, rgb_to_hsb, rgb_to_hsl
from core.template import IllusionTemplate


class ChubbIllusion(IllusionTemplate):
    """
    Chubb Illusion Generator

    Generates the Chubb (contrast-contrast) illusion with:
    - Two background rectangles (uniform gray vs high-contrast noise)
    - Two circles with identical low-contrast binary noise texture
    - Perceived contrast influenced by background context

    Strength parameter controls circle contrast while preserving average brightness:
    - Uses midpoint-preserving contrast adjustment
    - strength < 1: lower contrast
    - strength = 1: default contrast
    - strength > 1: higher contrast

    Package migration notes:
    - The historical default ``hue=0`` crashed (``rgb_to_hsl`` cannot unpack an
      int); the default is now ``hue=(0, 0.5, 0.5)``, the value used to render
      the published dataset.
    - An optional ``seed`` parameter was added. When set, ``np.random`` is
      seeded at the start of ``define_elements`` so the noise textures are
      reproducible. ``seed=None`` (the default) preserves the original
      unseeded behavior.
    """

    def __init__(self,
                 base_low=0,      # Base low value for contrast
                 base_high=170,   # Base high value for contrast (out of 255)
                 circle_alpha=1,  # Circle transparency
                 base_saturation=0.5,
                 hue = (0, 0.5, 0.5),
                 perturb_mode='contrast', # 'contrast' or 'hue'
                 seed=None,
                 ):
        """
        Initialize Chubb Illusion generator.

        Args:
            base_low: Base low value for circle contrast (default: 0)
            base_high: Base high value for circle contrast (default: 170)
            circle_alpha: Circle transparency (default: 0.5)
            seed: Optional numpy random seed for reproducible noise textures
        """
        self.perturb_mode = perturb_mode
        self.base_low = base_low
        self.base_high = base_high
        self.circle_alpha = circle_alpha

        # Calculate midpoint and range for contrast adjustment
        self.contrast_mid = (base_low + base_high) / 2
        self.contrast_range = (base_high - base_low) / 2

        # Background configuration
        self.left_bg_color = (0.5, 0.5, 0.5)  # Uniform gray

        # Circle configuration
        self.circle_radius_ratio = 1 / 16  # radius = WIDTH // 16
        self.base_saturation = base_saturation
        self.hue = rgb_to_hsl(hue)[0]
        self.seed = seed
        super().__init__(
            illusion_name="chubb",
            width=512,
            height=256,
            strength_levels=[0.5, 0.75, 1.0, 1.25, 1.5],
            background_color=(1.0, 1.0, 1.0),  # White background
        )

    def _calculate_contrast_values(self, strength: float) -> Tuple[float, float]:
        """
        Calculate low and high values for contrast based on strength.

        Uses midpoint-preserving contrast adjustment to keep average brightness constant.

        Args:
            strength: Contrast scaling factor

        Returns:
            Tuple of (low_val, high_val) in range [0, 255]
        """
        # Midpoint-preserving contrast adjustment
        low_val = self.contrast_mid - strength * self.contrast_range
        high_val = self.contrast_mid + strength * self.contrast_range

        # Clamp to [0, 255]
        low_val = max(0, min(255, low_val))
        high_val = max(0, min(255, high_val))

        return (low_val, high_val)

    def _generate_binary_noise_texture(self, size: Tuple[int, int],
                                      low_val: float, high_val: float) -> np.ndarray:
        """
        Generate binary random noise texture.

        Args:
            size: (height, width) of texture
            low_val: Low value (darker)
            high_val: High value (lighter)

        Returns:
            RGB texture array in range [0, 1]
        """
        height, width = size
        noise = np.random.rand(height, width, 1)
        binary_noise = np.where(noise > 0.5, high_val, low_val).repeat(3, axis=2)
        return (binary_noise / 255.0).clip(0.1, 0.9)

    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """
        Define Chubb illusion elements.

        For Original variation:
            - Both circles have the same contrast (determined by strength)
        For Perturbed variation:
            - Left circle fixed at default (strength=1.0)
            - Right circle varies with strength

        Args:
            strength: Controls circle contrast
            is_original: Whether this is the original variation

        Returns:
            Dictionary containing background and circle parameters
        """
        if self.seed is not None:
            np.random.seed(self.seed)
        self.strength = strength

        # Calculate positions
        center_y = self.height // 2
        left_center_x = self.width // 4
        right_center_x = 3 * self.width // 4
        circle_radius = int(self.width * self.circle_radius_ratio)


        left_bg_color = self.modify_color(self.left_bg_color)

        # Generate background noise texture (right rectangle)
        right_bg_noise = self._generate_binary_noise_texture(
            (self.height, self.width // 2), 0, 255
        )
        if self.perturb_mode == 'contrast':
            right_bg_noise = self.update_texture_color(right_bg_noise)

        # Calculate circle contrast values
        if is_original:
            # Original: Both circles same contrast, vary with strength
            low_val, high_val = self._calculate_contrast_values(strength)
            left_contrast = (low_val, high_val)
            right_contrast = (low_val, high_val)
        else:
            # Perturbed: Left fixed, right varies
            left_contrast = self._calculate_contrast_values(1.0)
            strength_map = lambda x: -(x - 1) + 1
            right_contrast = self._calculate_contrast_values(strength_map(strength))
        if self.perturb_mode != 'contrast':
            # Original: Both circles same contrast, vary with strength
            low_val, high_val = self._calculate_contrast_values(1)
            left_contrast = (low_val, high_val)
            right_contrast = (low_val, high_val)
        # Generate circle noise textures
        circle_size = (circle_radius * 2, circle_radius * 2)
        left_circle_texture = self._generate_binary_noise_texture(
            circle_size, left_contrast[0], left_contrast[1]
        )
        left_circle_texture = self.update_texture_color(left_circle_texture)
        right_circle_texture = self._generate_binary_noise_texture(
            circle_size, right_contrast[0], right_contrast[1]
        )
        if is_original:
            right_circle_texture = self.update_texture_color(right_circle_texture)
        else:
            right_circle_texture = self.update_texture_color(right_circle_texture, self.perturb_mode)

        elements = {
            # Background rectangles
            'left_bg': {
                'center': (left_center_x, center_y),
                'width': self.width // 2,
                'height': self.height,
                'color': left_bg_color,
            },
            'right_bg': {
                'center': (right_center_x, center_y),
                'width': self.width // 2,
                'height': self.height,
                'texture': right_bg_noise,
            },

            # Circles with noise textures
            'left_circle': {
                'center': (left_center_x, center_y),
                'radius': circle_radius,
                'texture': left_circle_texture,
                'alpha': self.circle_alpha,
            },
            'right_circle': {
                'center': (right_center_x, center_y),
                'radius': circle_radius,
                'texture': right_circle_texture,
                'alpha': self.circle_alpha,
            },

            # Visual guide
            'guide_texture': left_circle_texture,  # Use left circle's texture
            'left_contrast': left_contrast,  # Store for later use

            # Control flag
            'draw_backgrounds': True,  # Control will set to False
        }

        return elements
    def update_texture_color(self, elements: Dict[str, Any], perturb_mode: str = "contrast") -> Dict[str, Any]:
        """
        Update the background color of the left rectangle.
        """
        unique_colors = np.unique(elements.reshape(-1, 3), axis=0)

        # Convert numpy arrays to tuples for dictionary keys
        unique_colors_dict = {tuple(color): self.modify_color(color, perturb_mode) for color in unique_colors}

        # Apply color modifications
        for color_tuple, modified_color in unique_colors_dict.items():
            color_array = np.array(color_tuple)
            # Create a mask that matches all three channels
            mask = np.all(elements == color_array, axis=-1)
            elements[mask] = modified_color

        return elements

    def modify_color(self, color: Tuple[float, float, float], perturb_mode = "contrast") -> Tuple[float, float, float]:
        """
        Modify the color of the circle.
        """
        h, s, b = rgb_to_hsb(color)

        if perturb_mode == 'hue':
            h = (self.strength - 1.0) * 360 / 180
        else:
            h = self.hue
        s = self.base_saturation
        return hsl_to_rgb((h, s, b))
    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Draw the Chubb illusion on the canvas.

        Order of drawing:
        1. Background rectangles (if enabled)
        2. Circles with noise textures

        Args:
            image: Blank canvas
            elements: Element parameters from define_elements()

        Returns:
            Image with illusion drawn
        """
        # Draw background rectangles (if enabled)
        if elements.get('draw_backgrounds', True):
            # Left background (uniform gray)
            left_bg = elements['left_bg']
            image = add_rectangle(
                image,
                rect_color=left_bg['color'],
                rect_center=left_bg['center'],
                rect_width=left_bg['width'],
                rect_height=left_bg['height'],
                antialias=False
            )

            # Right background (high-contrast noise)
            right_bg = elements['right_bg']
            # right_bg = self.update_texture_color(right_bg)
            # Directly set the texture to image region
            x_start = right_bg['center'][0] - right_bg['width'] // 2
            x_end = right_bg['center'][0] + right_bg['width'] // 2
            y_start = right_bg['center'][1] - right_bg['height'] // 2
            y_end = right_bg['center'][1] + right_bg['height'] // 2
            image[y_start:y_end, x_start:x_end, :] = right_bg['texture']

        # Draw left circle with texture
        left_circle = elements['left_circle']
        # Create circle mask and apply alpha blending manually
        center_x, center_y = left_circle['center']
        radius = left_circle['radius']
        texture = left_circle['texture']
        alpha = left_circle['alpha']

        # Get circle region
        y_coords, x_coords = np.ogrid[:texture.shape[0], :texture.shape[1]]
        center_offset_y = texture.shape[0] // 2
        center_offset_x = texture.shape[1] // 2
        mask = (x_coords - center_offset_x)**2 + (y_coords - center_offset_y)**2 <= radius**2

        # Apply texture to image region with alpha blending
        y_start = center_y - radius
        y_end = center_y + radius
        x_start = center_x - radius
        x_end = center_x + radius

        for c in range(3):
            image[y_start:y_end, x_start:x_end, c] = np.where(
                mask,
                alpha * texture[:, :, c] + (1 - alpha) * image[y_start:y_end, x_start:x_end, c],
                image[y_start:y_end, x_start:x_end, c]
            )

        # Draw right circle with texture
        right_circle = elements['right_circle']
        center_x, center_y = right_circle['center']
        radius = right_circle['radius']
        texture = right_circle['texture']
        alpha = right_circle['alpha']

        # Get circle region
        y_coords, x_coords = np.ogrid[:texture.shape[0], :texture.shape[1]]
        center_offset_y = texture.shape[0] // 2
        center_offset_x = texture.shape[1] // 2
        mask = (x_coords - center_offset_x)**2 + (y_coords - center_offset_y)**2 <= radius**2

        # Apply texture to image region with alpha blending
        y_start = center_y - radius
        y_end = center_y + radius
        x_start = center_x - radius
        x_end = center_x + radius

        for c in range(3):
            image[y_start:y_end, x_start:x_end, c] = np.where(
                mask,
                alpha * texture[:, :, c] + (1 - alpha) * image[y_start:y_end, x_start:x_end, c],
                image[y_start:y_end, x_start:x_end, c]
            )

        return image

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """
        Add horizontal noise bar in the middle as visual guide.

        The guide bar uses the LEFT circle's texture to help compare the two circles.

        Args:
            image: Current image
            elements: Element parameters

        Returns:
            Image with guide bar added
        """
        # Guide bar parameters
        bar_width = self.width // 2
        bar_height = int(elements['left_circle']['radius'] // 2)
        bar_center = (self.width // 2, self.height // 2)

        # Use left circle's contrast for guide texture
        left_contrast = elements['left_contrast']
        guide_texture = self._generate_binary_noise_texture(
            (bar_height, bar_width),
            left_contrast[0],
            left_contrast[1]
        )
        guide_texture = self.update_texture_color(guide_texture)
        # Draw guide bar
        image = add_rectangle(
            image,
            rect_color=guide_texture,
            rect_center=bar_center,
            rect_width=bar_width,
            rect_height=bar_height,
            antialias=False
        )

        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create control condition by removing background patterns.

        In the control condition, circles are shown on uniform white background,
        making it clear they have the same contrast (no illusion).

        Args:
            elements: Original elements

        Returns:
            Modified elements with no backgrounds
        """
        elements['draw_backgrounds'] = False
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create perturbed version with left circle fixed, right varies.

        The perturbation logic is already handled in define_elements(),
        so this method doesn't need to modify anything.

        Args:
            elements: Elements with perturbation already applied

        Returns:
            Unmodified elements
        """
        # Perturbation logic is already handled in define_elements()
        return elements
