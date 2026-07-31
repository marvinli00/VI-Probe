"""
Rotated Rectangle with Super-Resolution Anti-aliasing

This module provides functions to draw rotated rectangles with high-quality
anti-aliasing using super-resolution (upsampling → draw → downsample).

Key features:
- Arbitrary rotation angles
- Per-pixel color control via color arrays
- Auto-generated checkerboard patterns
- Super-resolution anti-aliasing (4x default)
- High-quality downsampling using cv2.INTER_AREA

Author: Generated for Optical Illusion Dataset
Date: 2025
"""

from typing import List, Optional, Tuple, Union

import numpy as np


def _require_cv2():
    try:
        import cv2
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "add_rotated_rectangle_sr requires OpenCV: pip install opencv-python-headless"
        ) from e
    return cv2


def generate_checkerboard_pattern(
    width: int,
    height: int,
    colors: List[Tuple[float, float, float]],
    tile_width: int,
    tile_height: int,
    horizontal_offset: int = 0,
    vertical_offset: int = 0
) -> np.ndarray:
    """
    Generate a checkerboard color pattern array with optional horizontal and vertical offsets.

    Parameters:
    -----------
    width : int
        Width of the pattern in pixels
    height : int
        Height of the pattern in pixels
    colors : list of tuples
        List of RGB colors (values 0-1), e.g., [(0,0,0), (1,1,1)] for black-white
    tile_width : int
        Width of each checkerboard tile in pixels
    tile_height : int
        Height of each checkerboard tile in pixels
    horizontal_offset : int, optional
        Horizontal offset in pixels for the pattern (default: 0)
        Positive values shift the pattern to the left, useful for creating
        the Café Wall illusion effect where rows are staggered.
    vertical_offset : int, optional
        Vertical offset in pixels for the pattern (default: 0)
        Positive values shift the pattern upward, useful for creating
        the Café Wall illusion effect where columns are staggered.

    Returns:
    --------
    np.ndarray
        Color pattern array with shape (height, width, 3)

    Example:
    --------
    >>> # Black-white checkerboard, 40x40 tiles
    >>> pattern = generate_checkerboard_pattern(400, 400, [(0,0,0), (1,1,1)], 40, 40)

    >>> # Checkerboard with 20-pixel horizontal offset
    >>> pattern = generate_checkerboard_pattern(400, 400, [(0,0,0), (1,1,1)], 40, 40, horizontal_offset=20)

    >>> # Checkerboard with 10-pixel vertical offset
    >>> pattern = generate_checkerboard_pattern(400, 400, [(0,0,0), (1,1,1)], 40, 40, vertical_offset=10)

    >>> # Checkerboard with both horizontal and vertical offsets
    >>> pattern = generate_checkerboard_pattern(400, 400, [(0,0,0), (1,1,1)], 40, 40, horizontal_offset=20, vertical_offset=10)
    """
    pattern = np.zeros((height, width, 3), dtype=np.float32)

    for row in range(height):
        for col in range(width):
            # Determine which tile this pixel belongs to
            # Apply both horizontal and vertical offsets
            tile_row = (row + vertical_offset) // tile_height
            tile_col = (col + horizontal_offset) // tile_width

            # Alternate colors based on tile position
            color_idx = (tile_row + tile_col) % len(colors)
            pattern[row, col] = colors[color_idx]

    return pattern


def add_rotated_rectangle_sr(
    image_numpy: np.ndarray,
    rect_color: Union[Tuple[float, float, float], np.ndarray, None],
    rect_center: Tuple[float, float],
    rect_width: float,
    rect_height: float,
    rotation_angle: float = 0.0,
    sr_factor: int = 4,
    downsample_method: str = 'area',
    antialias: bool = True,
    # Rotation pivot parameters
    pivot_corner: Optional[str] = None,
    # Checkerboard mode parameters
    checkerboard_colors: Optional[List[Tuple[float, float, float]]] = None,
    tile_size: Optional[Tuple[int, int]] = None,
    # Border parameters
    border_width: float = 0,
    border_color: Optional[Tuple[float, float, float]] = None,
    border_alpha: float = 1.0
) -> np.ndarray:
    """
    Add a rotated rectangle to the image with super-resolution anti-aliasing.

    This function uses super-resolution technique: draw at higher resolution (sr_factor × original),
    then downsample to achieve smooth anti-aliasing for rotated edges.

    Parameters:
    -----------
    image_numpy : np.ndarray
        Input image as numpy array with shape (height, width, 3), values 0-1
    rect_color : tuple, np.ndarray, or None
        - If tuple: Single RGB color (values 0-1)
        - If np.ndarray: 3D array (rect_height, rect_width, 3) with per-pixel colors
        - If None: Use checkerboard mode (requires checkerboard_colors and tile_size)
    rect_center : tuple (x, y)
        Center position of the rectangle in image coordinates (column, row)
    rect_width : float
        Width of the rectangle in pixels (before rotation)
    rect_height : float
        Height of the rectangle in pixels (before rotation)
    rotation_angle : float
        Rotation angle in degrees, counterclockwise (default: 0.0)
    sr_factor : int
        Super-resolution factor (default: 4). Higher = better quality but slower.
    downsample_method : str
        Downsampling interpolation method: 'area' (recommended) or 'lanczos' (default: 'area')
    antialias : bool
        Whether to apply anti-aliasing (default: True)
    pivot_corner : str, optional
        Which corner to use as rotation pivot (default: None, rotates around center)
        Options: None, 'top-left', 'top-right', 'bottom-left', 'bottom-right'
        - None: Rotate around rect_center (default behavior)
        - 'top-left': Rotate around the top-left corner of the rectangle
        - 'top-right': Rotate around the top-right corner
        - 'bottom-left': Rotate around the bottom-left corner
        - 'bottom-right': Rotate around the bottom-right corner
    checkerboard_colors : list of tuples, optional
        Colors for auto-generated checkerboard pattern, e.g., [(0,0,0), (1,1,1)]
    tile_size : tuple (tile_width, tile_height), optional
        Size of each checkerboard tile in pixels
    border_width : float
        Width of the border in pixels (default: 0, no border)
    border_color : tuple, optional
        RGB color of the border (values 0-1)
    border_alpha : float
        Opacity of the border (0-1, default: 1.0)

    Returns:
    --------
    np.ndarray
        Modified image with rotated rectangle added

    Example:
    --------
    >>> # Rotated red rectangle
    >>> image = add_rotated_rectangle_sr(
    ...     image,
    ...     rect_color=(1, 0, 0),
    ...     rect_center=(256, 256),
    ...     rect_width=100,
    ...     rect_height=50,
    ...     rotation_angle=45.0
    ... )

    >>> # Rotated checkerboard
    >>> image = add_rotated_rectangle_sr(
    ...     image,
    ...     rect_color=None,
    ...     rect_center=(256, 256),
    ...     rect_width=400,
    ...     rect_height=400,
    ...     rotation_angle=15.0,
    ...     checkerboard_colors=[(0,0,0), (1,1,1)],
    ...     tile_size=(40, 40)
    ... )

    >>> # Rotate around top-left corner
    >>> image = add_rotated_rectangle_sr(
    ...     image,
    ...     rect_color=(0, 1, 0),
    ...     rect_center=(256, 256),
    ...     rect_width=200,
    ...     rect_height=100,
    ...     rotation_angle=30.0,
    ...     pivot_corner='top-left'
    ... )
    """
    cv2 = _require_cv2()
    # Validate inputs
    if rect_color is None and (checkerboard_colors is None or tile_size is None):
        raise ValueError("If rect_color is None, must provide checkerboard_colors and tile_size")

    valid_pivots = {None, 'top-left', 'top-right', 'bottom-left', 'bottom-right'}
    if pivot_corner not in valid_pivots:
        raise ValueError(f"pivot_corner must be one of {valid_pivots}, got '{pivot_corner}'")

    img_height, img_width = image_numpy.shape[:2]

    # Prepare color array
    rect_width_int = int(np.round(rect_width))
    rect_height_int = int(np.round(rect_height))

    if rect_color is None:
        # Checkerboard mode
        tile_w, tile_h = tile_size
        color_array = generate_checkerboard_pattern(
            rect_width_int, rect_height_int,
            checkerboard_colors, tile_w, tile_h
        )
        is_color_array = True
    elif isinstance(rect_color, np.ndarray) and rect_color.ndim == 3:
        # User-provided color array
        if rect_color.shape != (rect_height_int, rect_width_int, 3):
            raise ValueError(f"rect_color array shape {rect_color.shape} does not match "
                           f"expected shape ({rect_height_int}, {rect_width_int}, 3)")
        color_array = rect_color.astype(np.float32)
        is_color_array = True
    else:
        # Single color
        color_array = np.array(rect_color, dtype=np.float32)
        is_color_array = False

    # Convert rotation angle to radians
    angle_rad = np.radians(rotation_angle)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)

    # Rotation matrix (counterclockwise)
    rotation_matrix = np.array([
        [cos_a, -sin_a],
        [sin_a,  cos_a]
    ])

    # Calculate the actual rotation pivot point
    cx, cy = rect_center
    if pivot_corner is None:
        # Default: rotate around center
        pivot_x, pivot_y = cx, cy
    elif pivot_corner == 'top-left':
        pivot_x = cx - rect_width / 2
        pivot_y = cy - rect_height / 2
    elif pivot_corner == 'top-right':
        pivot_x = cx + rect_width / 2
        pivot_y = cy - rect_height / 2
    elif pivot_corner == 'bottom-left':
        pivot_x = cx - rect_width / 2
        pivot_y = cy + rect_height / 2
    else:  # 'bottom-right'
        pivot_x = cx + rect_width / 2
        pivot_y = cy + rect_height / 2

    # Calculate bounding box of rotated rectangle
    corners = np.array([
        [-rect_width/2, -rect_height/2],
        [ rect_width/2, -rect_height/2],
        [ rect_width/2,  rect_height/2],
        [-rect_width/2,  rect_height/2]
    ])
    rotated_corners = corners @ rotation_matrix.T

    # Find bounding box in image space (relative to pivot point)
    bbox_min_x = np.min(rotated_corners[:, 0]) + pivot_x
    bbox_max_x = np.max(rotated_corners[:, 0]) + pivot_x
    bbox_min_y = np.min(rotated_corners[:, 1]) + pivot_y
    bbox_max_y = np.max(rotated_corners[:, 1]) + pivot_y

    # Expand bbox slightly for anti-aliasing
    padding = 2
    bbox_min_x = int(np.floor(bbox_min_x)) - padding
    bbox_max_x = int(np.ceil(bbox_max_x)) + padding
    bbox_min_y = int(np.floor(bbox_min_y)) - padding
    bbox_max_y = int(np.ceil(bbox_max_y)) + padding

    # Clip to image bounds
    bbox_min_x = max(0, bbox_min_x)
    bbox_max_x = min(img_width, bbox_max_x)
    bbox_min_y = max(0, bbox_min_y)
    bbox_max_y = min(img_height, bbox_max_y)

    if bbox_max_x <= bbox_min_x or bbox_max_y <= bbox_min_y:
        return image_numpy  # Rectangle is completely outside image

    # Calculate bbox dimensions
    bbox_width = bbox_max_x - bbox_min_x
    bbox_height = bbox_max_y - bbox_min_y

    # Create super-resolution canvas for the bounding box
    sr_bbox_width = bbox_width * sr_factor
    sr_bbox_height = bbox_height * sr_factor

    # Upscale color array if needed
    if is_color_array:
        # Use INTER_NEAREST to preserve sharp tile boundaries
        sr_color_array = cv2.resize(
            color_array,
            (rect_width_int * sr_factor, rect_height_int * sr_factor),
            interpolation=cv2.INTER_NEAREST
        )
    else:
        sr_color_array = color_array

    # Create coordinate grids for super-resolution canvas
    sr_y, sr_x = np.ogrid[:sr_bbox_height, :sr_bbox_width]

    # Convert SR pixel coordinates to original image coordinates
    orig_x = sr_x / sr_factor + bbox_min_x
    orig_y = sr_y / sr_factor + bbox_min_y

    # Translate to rotation pivot point
    dx = orig_x - pivot_x
    dy = orig_y - pivot_y

    # Apply inverse rotation to find position in rectangle's local coordinates
    inv_rotation = rotation_matrix.T  # Inverse of rotation matrix
    local_x = cos_a * dx + sin_a * dy
    local_y = -sin_a * dx + cos_a * dy

    # Adjust local coordinates when pivot is not at center
    # This ensures the rectangle content is correctly positioned relative to the pivot
    if pivot_corner is not None:
        # Calculate offset from pivot to rectangle center
        offset_x = cx - pivot_x
        offset_y = cy - pivot_y

        # Rotate this offset vector (forward rotation)
        rotated_offset_x = cos_a * offset_x - sin_a * offset_y
        rotated_offset_y = sin_a * offset_x + cos_a * offset_y

        # Adjust local coordinates
        local_x = local_x - rotated_offset_x
        local_y = local_y - rotated_offset_y

    # Check if pixels are inside the rectangle
    inside_mask = (np.abs(local_x) <= rect_width/2) & (np.abs(local_y) <= rect_height/2)

    # Create alpha mask for blending
    if antialias:
        # Soft edges with 0.5-pixel transition
        alpha_x = np.clip(rect_width/2 + 0.5/sr_factor - np.abs(local_x), 0, 1)
        alpha_y = np.clip(rect_height/2 + 0.5/sr_factor - np.abs(local_y), 0, 1)
        sr_alpha = alpha_x * alpha_y
    else:
        sr_alpha = inside_mask.astype(np.float32)

    # Create super-resolution image for the bounding box
    sr_rect_image = np.zeros((sr_bbox_height, sr_bbox_width, 3), dtype=np.float32)

    if is_color_array:
        # Map local coordinates to color array indices
        # Local coords: [-width/2, width/2] × [-height/2, height/2]
        # Array coords: [0, width-1] × [0, height-1]
        color_x = (local_x + rect_width/2) * sr_factor
        color_y = (local_y + rect_height/2) * sr_factor

        # Clip to array bounds
        color_x = np.clip(color_x, 0, sr_color_array.shape[1] - 1)
        color_y = np.clip(color_y, 0, sr_color_array.shape[0] - 1)

        # Sample colors using bilinear interpolation
        color_x_int = color_x.astype(int)
        color_y_int = color_y.astype(int)

        # Ensure indices are within bounds
        color_x_int = np.clip(color_x_int, 0, sr_color_array.shape[1] - 1)
        color_y_int = np.clip(color_y_int, 0, sr_color_array.shape[0] - 1)

        # Sample color (simple nearest-neighbor for now)
        for c in range(3):
            sr_rect_image[:, :, c] = sr_color_array[color_y_int, color_x_int, c] * sr_alpha
    else:
        # Single color
        for c in range(3):
            sr_rect_image[:, :, c] = sr_color_array[c] * sr_alpha

    # Downsample to original resolution
    if downsample_method == 'lanczos':
        interp_method = cv2.INTER_LANCZOS4
    else:  # 'area' (recommended)
        interp_method = cv2.INTER_AREA

    downsampled_rect = cv2.resize(
        sr_rect_image,
        (bbox_width, bbox_height),
        interpolation=interp_method
    )

    # Create downsampled alpha mask
    sr_alpha_resized = cv2.resize(
        sr_alpha.astype(np.float32),
        (bbox_width, bbox_height),
        interpolation=interp_method
    )

    # Extract the region from original image
    orig_region = image_numpy[bbox_min_y:bbox_max_y, bbox_min_x:bbox_max_x].copy()

    # Blend downsampled rectangle with original image
    for c in range(3):
        # Alpha compositing
        orig_region[:, :, c] = (
            orig_region[:, :, c] * (1 - sr_alpha_resized) +
            downsampled_rect[:, :, c]
        )

    # Put blended region back
    image_numpy[bbox_min_y:bbox_max_y, bbox_min_x:bbox_max_x] = orig_region

    # Add border if specified (simplified for rotated case)
    if border_width > 0 and border_color is not None:
        # TODO: Implement border for rotated rectangles
        # This would require similar SR treatment for the border
        pass

    return image_numpy


# Backward compatibility alias
add_rotated_rect_sr = add_rotated_rectangle_sr
