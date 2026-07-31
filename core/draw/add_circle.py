import numpy as np


def add_circle(image_numpy, circle_color, circle_center, circle_radius, antialias=True, hollow=False, edge_width=1.0):
    """
    Add a circle to the image numpy array with anti-aliasing
    
    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    circle_color : tuple or numpy.ndarray
        - If tuple: RGB color of the circle (values 0-1)
        - If numpy.ndarray: 3D array with shape (diameter, diameter, 3)
          specifying color for each pixel in the bounding square of the circle
          where diameter = 2 * circle_radius (values 0-1)
    circle_center : tuple (x, y)
        Center position of the circle (column, row)
    circle_radius : float
        Radius of the circle in pixels
    antialias : bool
        Whether to apply anti-aliasing at the edges (default: True)
    hollow : bool
        Whether to draw a hollow circle (ring) instead of filled (default: False)
    edge_width : float
        Width of the edge for hollow circles in pixels (default: 1.0)
    
    Returns:
    --------
    numpy.ndarray
        Modified image with circle added
    """
    # Get image dimensions
    height, width = image_numpy.shape[:2]

    # Create coordinate grids
    y, x = np.ogrid[:height, :width]

    # Calculate distance from center
    distance = np.sqrt((x - circle_center[0])**2 + (y - circle_center[1])**2)

    # Check if circle_color is an array or a single color
    is_color_array = isinstance(circle_color, np.ndarray) and circle_color.ndim == 3

    if is_color_array:
        # Validate the color array dimensions
        diameter = int(np.round(2 * circle_radius))
        if circle_color.shape != (diameter, diameter, 3):
            raise ValueError(f"circle_color array shape {circle_color.shape} does not match "
                           f"expected shape ({diameter}, {diameter}, 3)")

    if antialias:
        # Create smooth alpha channel for anti-aliasing
        if hollow:
            # For hollow circle, create alpha for the ring
            inner_radius = circle_radius - edge_width
            # Outer edge alpha
            alpha_outer = np.clip(circle_radius + 0.5 - distance, 0, 1)
            # Inner edge alpha (inverted)
            alpha_inner = np.clip(distance - inner_radius + 0.5, 0, 1)
            # Combine to get ring alpha
            alpha = alpha_outer * alpha_inner
        else:
            # Use a 1-pixel transition zone at the edge
            alpha = np.clip(circle_radius + 0.5 - distance, 0, 1)

        if is_color_array:
            # Map image coordinates to color array coordinates
            # Calculate the top-left corner of the bounding square
            square_left = circle_center[0] - circle_radius
            square_top = circle_center[1] - circle_radius

            # Create meshgrid for the entire image
            xx, yy = np.meshgrid(np.arange(width), np.arange(height))

            # Calculate positions in the color array
            color_x = xx - square_left
            color_y = yy - square_top

            # Create a mask for pixels that are within the bounding square
            diameter = circle_color.shape[0]
            valid_mask = (color_x >= 0) & (color_x < diameter) & \
                        (color_y >= 0) & (color_y < diameter) & \
                        (alpha > 0)

            # Convert to integer indices (with bounds checking)
            color_x_int = np.clip(np.floor(color_x).astype(int), 0, diameter - 1)
            color_y_int = np.clip(np.floor(color_y).astype(int), 0, diameter - 1)

            # Get colors from the array
            circle_colors = circle_color[color_y_int, color_x_int]

            # Blend the circle color with existing image
            for i in range(3):  # For each color channel
                alpha_channel = alpha * valid_mask
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha_channel) + \
                                      circle_colors[:, :, i] * alpha_channel
        else:
            # Single color (original behavior)
            circle_color_array = np.array(circle_color)
            for i in range(3):  # For each color channel
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha) + circle_color_array[i] * alpha
    else:
        # Create hard circular mask (original version)
        if hollow:
            # For hollow circle, create ring mask
            inner_radius = circle_radius - edge_width
            mask = (distance <= circle_radius) & (distance >= inner_radius)
        else:
            mask = distance <= circle_radius

        if is_color_array:
            # Map image coordinates to color array coordinates
            square_left = circle_center[0] - circle_radius
            square_top = circle_center[1] - circle_radius

            # Get the coordinates of masked pixels
            y_coords, x_coords = np.where(mask)

            # Calculate positions in the color array
            color_x = (x_coords - square_left).astype(int)
            color_y = (y_coords - square_top).astype(int)

            # Ensure coordinates are within bounds
            diameter = circle_color.shape[0]
            valid = (color_x >= 0) & (color_x < diameter) & \
                   (color_y >= 0) & (color_y < diameter)

            y_coords = y_coords[valid]
            x_coords = x_coords[valid]
            color_x = np.clip(color_x[valid], 0, diameter - 1)
            color_y = np.clip(color_y[valid], 0, diameter - 1)

            # Set colors from the array
            image_numpy[y_coords, x_coords] = circle_color[color_y, color_x]
        else:
            # Single color (original behavior)
            image_numpy[mask] = circle_color

    return image_numpy
