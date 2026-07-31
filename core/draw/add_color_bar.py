import numpy as np


def add_color_bar(image_numpy, start_color, end_color, start_pos, end_pos, bar_width, antialiasing=True, border_width=1):
    """
    Add an angled gradient color bar to an image numpy array with anti-aliasing

    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    start_color : tuple
        RGB color at the start position (values 0-1)
    end_color : tuple
        RGB color at the end position (values 0-1)
    start_pos : tuple (x, y)
        Starting position (column, row) of the color bar center line
    end_pos : tuple (x, y)
        Ending position (column, row) of the color bar center line
    bar_width : float
        Width (thickness) of the color bar in pixels
    antialiasing : bool
        Whether to apply anti-aliasing at the edges (default: True)
    border_width : float
        Width of red border around the color bar (default: 1, set to 0 to disable)

    Returns:
    --------
    numpy.ndarray
        Modified image with angled gradient color bar added
    """
    height, width = image_numpy.shape[:2]

    # Convert positions to numpy arrays
    start_pos = np.array(start_pos, dtype=float)
    end_pos = np.array(end_pos, dtype=float)

    # Calculate direction vector and length
    direction = end_pos - start_pos
    bar_length = np.linalg.norm(direction)

    if bar_length == 0:
        return image_numpy

    # Normalize direction vector
    direction_norm = direction / bar_length

    # Perpendicular vector for width calculation
    perpendicular = np.array([-direction_norm[1], direction_norm[0]])

    # Create coordinate grids
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    coords = np.stack([x_coords, y_coords], axis=-1)  # Shape: (height, width, 2)

    # Calculate vector from start_pos to each pixel
    vec_to_pixels = coords - start_pos  # Shape: (height, width, 2)

    # Project onto direction vector (distance along the bar)
    along_distance = np.sum(vec_to_pixels * direction_norm, axis=-1)  # Shape: (height, width)

    # Project onto perpendicular vector (distance from center line)
    perp_distance = np.abs(np.sum(vec_to_pixels * perpendicular, axis=-1))  # Shape: (height, width)

    # Create mask for pixels within the bar
    half_width = bar_width / 2.0

    if antialiasing:
        # Soft edges with 1-pixel transition
        along_mask = np.clip((along_distance + 1) / 1, 0, 1) * np.clip((bar_length - along_distance + 1) / 1, 0, 1)
        perp_mask = np.clip((half_width - perp_distance + 1) / 1, 0, 1)
        alpha = along_mask * perp_mask  # Combined alpha mask
    else:
        # Hard edges
        along_mask = (along_distance >= 0) & (along_distance <= bar_length)
        perp_mask = perp_distance <= half_width
        alpha = (along_mask & perp_mask).astype(float)

    # Calculate color interpolation factor (0 to 1 along the bar)
    t = np.clip(along_distance / bar_length, 0, 1)  # Shape: (height, width)

    # Interpolate colors
    start_color = np.array(start_color)
    end_color = np.array(end_color)

    # Expand t for broadcasting with color channels
    t_expanded = t[..., np.newaxis]  # Shape: (height, width, 1)

    # Linear interpolation between start and end colors
    interpolated_color = start_color * (1 - t_expanded) + end_color * t_expanded

    # Apply alpha blending
    alpha_expanded = alpha[..., np.newaxis]  # Shape: (height, width, 1)
    image_numpy[:, :, :] = image_numpy * (1 - alpha_expanded) + interpolated_color * alpha_expanded

    # Add red border if border_width > 0
    if border_width > 0:
        border_color = np.array([1.0, 0.0, 0.0])  # Red color

        # Calculate border mask (region between bar edge and border edge)
        inner_edge = half_width
        outer_edge = half_width + border_width

        if antialiasing:
            # Soft border edges with 1-pixel transition
            border_along_mask = np.clip((along_distance + 1) / 1, 0, 1) * np.clip((bar_length - along_distance + 1) / 1, 0, 1)
            # Border is between inner_edge and outer_edge
            outer_mask = np.clip((outer_edge - perp_distance + 1) / 1, 0, 1)
            inner_mask = np.clip((perp_distance - inner_edge + 1) / 1, 0, 1)
            border_alpha = border_along_mask * outer_mask * inner_mask
        else:
            # Hard border edges
            border_along_mask = (along_distance >= 0) & (along_distance <= bar_length)
            border_perp_mask = (perp_distance > inner_edge) & (perp_distance <= outer_edge)
            border_alpha = (border_along_mask & border_perp_mask).astype(float)

        # Apply border with alpha blending
        border_alpha_expanded = border_alpha[..., np.newaxis]
        image_numpy[:, :, :] = image_numpy * (1 - border_alpha_expanded) + border_color * border_alpha_expanded

    return image_numpy
