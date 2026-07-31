"""
Curved Line Drawing with Pure NumPy and Antialiasing

This module provides smooth antialiased curve drawing using only NumPy,
without relying on PIL or other graphics libraries.

Techniques used:
1. Supersampling Anti-Aliasing (SSAA) - render at 4x resolution then downsample
2. Xiaolin Wu's line algorithm - antialiased line drawing
3. Manual thick line rendering - draw multiple parallel lines for width
"""

import numpy as np


def add_curved_line(
    image_numpy: np.ndarray,
    line_color: tuple,
    points: list,
    line_width: int = 3,
    antialias: bool = True
) -> np.ndarray:
    """
    Draw a smooth curved line on a numpy image array.

    Uses supersampling antialiasing for smooth, high-quality curves.
    All operations are performed using pure NumPy without external graphics libraries.

    Parameters:
    -----------
    image_numpy : np.ndarray
        Input image with shape (H, W, 3) and values in range [0, 1]
    line_color : tuple
        RGB color tuple with values in range [0, 1], e.g., (0, 0, 0) for black
    points : list
        List of (x, y) coordinate tuples defining the curve path
        Example: [(0, 100), (50, 105), (100, 110), ...]
    line_width : int
        Width of the line in pixels (default: 3)
    antialias : bool
        Whether to use supersampling antialiasing (default: True)

    Returns:
    --------
    np.ndarray
        Modified image with the curve drawn, shape (H, W, 3), values in [0, 1]

    Example:
    --------
    >>> image = np.ones((512, 512, 3), dtype=np.float32)
    >>> points = [(100, 256), (200, 200), (300, 256), (400, 200)]
    >>> image = add_curved_line(image, (0, 0, 0), points, line_width=5)
    """
    if len(points) < 2:
        return image_numpy

    if antialias:
        return _draw_supersampled(image_numpy, line_color, points, line_width)
    else:
        return _draw_direct(image_numpy, line_color, points, line_width)


def _draw_supersampled(image: np.ndarray, color: tuple, points: list, width: int) -> np.ndarray:
    """
    Draw curve using supersampling antialiasing.

    Renders the curve at 4x resolution, then downsamples to original size.
    The downsampling averages pixels, creating smooth antialiased edges.
    """
    H, W = image.shape[:2]
    SCALE = 4  # 4x supersampling

    # Step 1: Upsample image to 4x resolution
    upscaled = np.repeat(np.repeat(image, SCALE, axis=0), SCALE, axis=1)

    # Step 2: Scale point coordinates
    scaled_points = [(int(x * SCALE), int(y * SCALE)) for x, y in points]
    scaled_width = width * SCALE

    # Step 3: Draw on high-resolution image
    for i in range(len(scaled_points) - 1):
        x0, y0 = scaled_points[i]
        x1, y1 = scaled_points[i + 1]
        _draw_thick_line_wu(upscaled, x0, y0, x1, y1, color, scaled_width)

    # Step 4: Downsample back to original resolution (area averaging = antialiasing)
    downscaled = _downsample_average(upscaled, SCALE)

    return downscaled


def _draw_direct(image: np.ndarray, color: tuple, points: list, width: int) -> np.ndarray:
    """Draw curve directly without antialiasing (faster but aliased)."""
    image_copy = image.copy()

    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        _draw_thick_line_simple(image_copy, x0, y0, x1, y1, color, width)

    return image_copy


def _downsample_average(image: np.ndarray, scale: int) -> np.ndarray:
    """
    Downsample image by averaging blocks of pixels.

    This is the key to antialiasing: averaging multiple high-res pixels
    creates smooth grayscale transitions at edges.
    """
    H, W = image.shape[:2]
    new_H, new_W = H // scale, W // scale

    # Vectorized approach: reshape and average
    # Trim to exact multiple of scale
    trimmed = image[:new_H * scale, :new_W * scale, :]

    # Reshape to (new_H, scale, new_W, scale, 3)
    reshaped = trimmed.reshape(new_H, scale, new_W, scale, 3)

    # Average over the scale x scale blocks (axes 1 and 3)
    downsampled = reshaped.mean(axis=(1, 3))

    return downsampled.astype(np.float32)


def _draw_thick_line_wu(image: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                        color: tuple, width: int) -> None:
    """
    Draw a thick antialiased line using Xiaolin Wu's algorithm.

    Creates thickness by drawing multiple parallel antialiased lines.
    """
    # Calculate perpendicular direction for thickness
    dx, dy = x1 - x0, y1 - y0
    length = np.sqrt(dx**2 + dy**2)

    if length < 1e-6:
        return

    # Unit perpendicular vector
    perp_x = -dy / length
    perp_y = dx / length

    # Draw multiple parallel lines to create thickness
    num_lines = max(int(width), 1)
    offsets = np.linspace(-width / 2, width / 2, num_lines)

    for offset in offsets:
        ox = offset * perp_x
        oy = offset * perp_y

        _draw_line_wu(
            image,
            int(x0 + ox), int(y0 + oy),
            int(x1 + ox), int(y1 + oy),
            color
        )


def _draw_line_wu(image: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                  color: tuple) -> None:
    """
    Xiaolin Wu's antialiased line algorithm.

    Draws a 1-pixel wide line with antialiased edges by using fractional
    pixel coverage to blend with background.

    Reference: https://en.wikipedia.org/wiki/Xiaolin_Wu%27s_line_algorithm
    """
    H, W = image.shape[:2]

    # Handle steep lines by swapping x and y
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    # Ensure left to right
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    # Avoid division by zero
    if dx == 0:
        return

    gradient = dy / dx

    # Main loop: draw the line
    y = y0
    for x in range(int(x0), int(x1) + 1):
        # Calculate fractional y position
        y_int = int(y)
        y_frac = y - y_int

        # Draw two pixels with antialiasing weights
        # Upper pixel: weight = 1 - fractional part
        # Lower pixel: weight = fractional part
        _blend_pixel(image, x, y_int, color, 1 - y_frac, steep, H, W)
        _blend_pixel(image, x, y_int + 1, color, y_frac, steep, H, W)

        y += gradient


def _blend_pixel(image: np.ndarray, x: int, y: int, color: tuple,
                 alpha: float, steep: bool, H: int, W: int) -> None:
    """
    Blend a pixel with the given color using alpha blending.

    Alpha blending formula: result = background * (1 - alpha) + foreground * alpha
    This creates smooth transitions at edges.
    """
    # Swap coordinates if line was steep
    if steep:
        x, y = y, x

    # Boundary check
    if not (0 <= y < H and 0 <= x < W):
        return

    # Alpha blending
    color_array = np.array(color, dtype=np.float32)
    image[y, x, :] = image[y, x, :] * (1 - alpha) + color_array * alpha


def _draw_thick_line_simple(image: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                            color: tuple, width: int) -> None:
    """
    Simple thick line drawing without antialiasing.
    Uses Bresenham's algorithm with perpendicular offset.
    """
    # Calculate perpendicular direction
    dx, dy = x1 - x0, y1 - y0
    length = np.sqrt(dx**2 + dy**2)

    if length < 1e-6:
        return

    perp_x = -dy / length
    perp_y = dx / length

    # Draw parallel lines
    offsets = np.linspace(-width / 2, width / 2, max(int(width), 1))
    for offset in offsets:
        ox = int(offset * perp_x)
        oy = int(offset * perp_y)
        _draw_line_bresenham(image, x0 + ox, y0 + oy, x1 + ox, y1 + oy, color)


def _draw_line_bresenham(image: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                         color: tuple) -> None:
    """
    Bresenham's line algorithm (no antialiasing).
    Fast integer-only line drawing.
    """
    H, W = image.shape[:2]

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    color_array = np.array(color, dtype=np.float32)

    while True:
        # Draw pixel if in bounds
        if 0 <= y0 < H and 0 <= x0 < W:
            image[y0, x0, :] = color_array

        # Check if we've reached the end
        if x0 == x1 and y0 == y1:
            break

        # Bresenham step
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
