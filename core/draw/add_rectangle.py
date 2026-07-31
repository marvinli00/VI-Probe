import numpy as np


def add_rectangle(image_numpy, rect_color, rect_center, rect_width, rect_height,
                  antialias=True, border_width=0, border_color=None, border_alpha=1.0):
    """
    Add a rectangle to the image numpy array with anti-aliasing and optional border

    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    rect_color : tuple or numpy.ndarray
        - If tuple: RGB color of the rectangle (values 0-1)
        - If numpy.ndarray: 3D array with shape (rect_height, rect_width, 3) 
          specifying color for each pixel in the rectangle (values 0-1)
    rect_center : tuple (x, y)
        Center position of the rectangle (column, row)
    rect_width : float
        Width of the rectangle in pixels
    rect_height : float
        Height of the rectangle in pixels
    antialias : bool
        Whether to apply anti-aliasing at the edges (default: True)
    border_width : float
        Width of the border in pixels, drawn inward (default: 0, no border)
    border_color : tuple
        RGB color of the border (values 0-1). If None, no border is drawn (default: None)
    border_alpha : float
        Opacity of the border (0-1, where 1 is fully opaque) (default: 1.0)

    Returns:
    --------
    numpy.ndarray
        Modified image with rectangle (and optional border) added
    """
    # Get image dimensions
    height, width = image_numpy.shape[:2]

    # Create coordinate grids
    y, x = np.ogrid[:height, :width]

    # Calculate distance from center in x and y directions
    dx = np.abs(x - rect_center[0])
    dy = np.abs(y - rect_center[1])

    # Half dimensions
    half_width = rect_width / 2.0
    half_height = rect_height / 2.0

    # Check if rect_color is an array or a single color
    is_color_array = isinstance(rect_color, np.ndarray) and rect_color.ndim == 3

    if is_color_array:
        # Validate the color array dimensions
        expected_height = int(np.round(rect_height))
        expected_width = int(np.round(rect_width))
        if rect_color.shape != (expected_height, expected_width, 3):
            raise ValueError(f"rect_color array shape {rect_color.shape} does not match "
                           f"expected shape ({expected_height}, {expected_width}, 3)")

    if antialias:
        # Create smooth alpha channel for anti-aliasing
        # Use a 1-pixel transition zone at the edges
        alpha_x = np.clip(half_width + 0.5 - dx, 0, 1)
        alpha_y = np.clip(half_height + 0.5 - dy, 0, 1)

        # Combine x and y alpha (both must be inside for the pixel to be in the rectangle)
        alpha = alpha_x * alpha_y

        if is_color_array:
            # Map image coordinates to rectangle color array coordinates
            # Calculate the top-left corner of the rectangle
            rect_left = rect_center[0] - half_width
            rect_top = rect_center[1] - half_height

            # Create meshgrid for the entire image
            xx, yy = np.meshgrid(np.arange(width), np.arange(height))

            # Calculate positions in the color array (can be fractional)
            color_x = xx - rect_left
            color_y = yy - rect_top

            # Create a mask for pixels that are within the rectangle bounds
            valid_mask = (color_x >= 0) & (color_x < rect_width) & \
                        (color_y >= 0) & (color_y < rect_height) & \
                        (alpha > 0)

            # Convert to integer indices (with bounds checking)
            color_x_int = np.clip(np.floor(color_x).astype(int), 0, expected_width - 1)
            color_y_int = np.clip(np.floor(color_y).astype(int), 0, expected_height - 1)

            # Get colors from the array
            rect_colors = rect_color[color_y_int, color_x_int]

            # Blend the rectangle color with existing image
            for i in range(3):  # For each color channel
                alpha_channel = alpha * valid_mask
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha_channel) + \
                                      rect_colors[:, :, i] * alpha_channel
        else:
            # Single color (original behavior)
            rect_color_array = np.array(rect_color)
            for i in range(3):  # For each color channel
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha) + rect_color_array[i] * alpha
    else:
        # Create hard rectangular mask (original version)
        mask = (dx <= half_width) & (dy <= half_height)

        if is_color_array:
            # Map image coordinates to rectangle color array coordinates
            rect_left = rect_center[0] - half_width
            rect_top = rect_center[1] - half_height

            # Get the coordinates of masked pixels
            y_coords, x_coords = np.where(mask)

            # Calculate positions in the color array
            color_x = (x_coords - rect_left).astype(int)
            color_y = (y_coords - rect_top).astype(int)

            # Ensure coordinates are within bounds
            valid = (color_x >= 0) & (color_x < expected_width) & \
                   (color_y >= 0) & (color_y < expected_height)

            y_coords = y_coords[valid]
            x_coords = x_coords[valid]
            color_x = np.clip(color_x[valid], 0, expected_width - 1)
            color_y = np.clip(color_y[valid], 0, expected_height - 1)

            # Set colors from the array
            image_numpy[y_coords, x_coords] = rect_color[color_y, color_x]
        else:
            # Single color (original behavior)
            image_numpy[mask] = rect_color

    # Add border if specified
    if border_width > 0 and border_color is not None:
        # Calculate distance from the inner edge of the rectangle
        # Distance to the nearest edge (inward)
        dist_to_edge_x = half_width - dx
        dist_to_edge_y = half_height - dy

        # Minimum distance to any edge (negative if outside rectangle)
        dist_to_nearest_edge = np.minimum(dist_to_edge_x, dist_to_edge_y)

        if antialias:
            # Anti-aliased border with smooth edges
            # Border exists where: 0 <= dist_to_nearest_edge <= border_width
            border_alpha_mask = np.clip(dist_to_nearest_edge + 0.5, 0, 1)  # Outer edge
            border_alpha_mask *= np.clip(border_width + 0.5 - dist_to_nearest_edge, 0, 1)  # Inner edge
            border_alpha_mask *= border_alpha  # Apply border transparency

            # Blend border color with existing image
            border_color_array = np.array(border_color)
            for i in range(3):  # For each color channel
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - border_alpha_mask) + border_color_array[i] * border_alpha_mask
        else:
            # Hard-edged border
            border_mask = (dist_to_nearest_edge >= 0) & (dist_to_nearest_edge <= border_width)

            if border_alpha < 1.0:
                # Apply transparency if border_alpha < 1
                border_color_array = np.array(border_color)
                for i in range(3):
                    image_numpy[border_mask, i] = image_numpy[border_mask, i] * (1 - border_alpha) + border_color_array[i] * border_alpha
            else:
                # Fully opaque border
                image_numpy[border_mask] = border_color

    return image_numpy
