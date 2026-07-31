import numpy as np


def add_polygon(image_numpy, polygon_color, center, radius, num_sides,
                rotation_angle=0, antialias=True,
                border_width=0, border_color=None, border_alpha=1.0):
    """
    Add a regular polygon to the image numpy array with anti-aliasing

    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    polygon_color : tuple or numpy.ndarray
        - If tuple: RGB color of the polygon (values 0-1)
        - If numpy.ndarray: 3D array with per-pixel colors (values 0-1)
    center : tuple (x, y)
        Center position of the polygon (column, row)
    radius : float
        Radius of the circumscribed circle (distance from center to vertices)
    num_sides : int
        Number of sides (3 for triangle, 4 for square, 5 for pentagon, etc.)
    rotation_angle : float
        Rotation angle in degrees (default: 0)
        Positive = counterclockwise, Negative = clockwise
        For pentagon, use -90 to have vertex pointing up
    antialias : bool
        Whether to apply anti-aliasing (default: True)
    border_width : float
        Width of the border in pixels (default: 0, no border)
    border_color : tuple
        RGB color of the border (values 0-1) (default: None)
    border_alpha : float
        Opacity of the border (0-1) (default: 1.0)

    Returns:
    --------
    numpy.ndarray
        Modified image with polygon added

    Example:
    --------
    # Draw a regular pentagon
    image = add_polygon(image, (0.9, 0.5, 0.3), (256, 256),
                       radius=100, num_sides=5, rotation_angle=-90)
    """
    # Get image dimensions
    height, width = image_numpy.shape[:2]

    # Create coordinate grids
    y, x = np.ogrid[:height, :width]

    # Calculate vertices of the polygon
    vertices = []
    angle_step = 2 * np.pi / num_sides
    rotation_rad = np.radians(rotation_angle)

    for i in range(num_sides):
        angle = i * angle_step + rotation_rad
        vertex_x = center[0] + radius * np.cos(angle)
        vertex_y = center[1] - radius * np.sin(angle)  # Negative because y increases downward
        vertices.append((vertex_x, vertex_y))

    def point_in_polygon(px, py, vertices):
        """
        Check if points are inside polygon using ray casting algorithm
        Returns distance to nearest edge (negative inside, positive outside)
        """
        n = len(vertices)

        # For each point, count how many edges it crosses
        inside = np.zeros_like(px, dtype=bool)

        for i in range(n):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n]

            # Check if ray crosses this edge
            crosses = ((v1[1] > py) != (v2[1] > py)) & \
                     (px < (v2[0] - v1[0]) * (py - v1[1]) / (v2[1] - v1[1] + 1e-10) + v1[0])
            inside = inside ^ crosses

        # Calculate distance to nearest edge for antialiasing
        min_dist = np.full_like(px, float('inf'))

        for i in range(n):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n]

            # Calculate distance from point to line segment
            edge_dx = v2[0] - v1[0]
            edge_dy = v2[1] - v1[1]
            edge_len_sq = edge_dx**2 + edge_dy**2

            if edge_len_sq == 0:
                dist = np.sqrt((px - v1[0])**2 + (py - v1[1])**2)
            else:
                # Project point onto line
                t = np.clip(((px - v1[0]) * edge_dx + (py - v1[1]) * edge_dy) / edge_len_sq, 0, 1)
                proj_x = v1[0] + t * edge_dx
                proj_y = v1[1] + t * edge_dy
                dist = np.sqrt((px - proj_x)**2 + (py - proj_y)**2)

            min_dist = np.minimum(min_dist, dist)

        # Return signed distance (negative inside, positive outside)
        return np.where(inside, -min_dist, min_dist)

    # Calculate signed distance for all pixels
    signed_dist = point_in_polygon(x, y, vertices)

    # Check if polygon_color is an array or single color
    is_color_array = isinstance(polygon_color, np.ndarray) and polygon_color.ndim == 3

    if antialias:
        # Create smooth alpha channel
        alpha = np.clip(0.5 - signed_dist, 0, 1)

        if is_color_array:
            # Map image coordinates to color array
            poly_left = center[0] - radius
            poly_top = center[1] - radius

            xx, yy = np.meshgrid(np.arange(width), np.arange(height))
            color_x = xx - poly_left
            color_y = yy - poly_top

            box_size = int(np.round(2 * radius))
            valid_mask = (color_x >= 0) & (color_x < polygon_color.shape[1]) & \
                        (color_y >= 0) & (color_y < polygon_color.shape[0]) & \
                        (alpha > 0)

            color_x_int = np.clip(np.floor(color_x).astype(int), 0, polygon_color.shape[1] - 1)
            color_y_int = np.clip(np.floor(color_y).astype(int), 0, polygon_color.shape[0] - 1)

            poly_colors = polygon_color[color_y_int, color_x_int]

            for i in range(3):
                alpha_channel = alpha * valid_mask
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha_channel) + \
                                      poly_colors[:, :, i] * alpha_channel
        else:
            # Single color
            poly_color_array = np.array(polygon_color)
            for i in range(3):
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha) + poly_color_array[i] * alpha
    else:
        # Hard mask (no antialiasing)
        mask = signed_dist <= 0

        if is_color_array:
            poly_left = center[0] - radius
            poly_top = center[1] - radius

            y_coords, x_coords = np.where(mask)
            color_x = (x_coords - poly_left).astype(int)
            color_y = (y_coords - poly_top).astype(int)

            valid = (color_x >= 0) & (color_x < polygon_color.shape[1]) & \
                   (color_y >= 0) & (color_y < polygon_color.shape[0])

            y_coords = y_coords[valid]
            x_coords = x_coords[valid]
            color_x = np.clip(color_x[valid], 0, polygon_color.shape[1] - 1)
            color_y = np.clip(color_y[valid], 0, polygon_color.shape[0] - 1)

            image_numpy[y_coords, x_coords] = polygon_color[color_y, color_x]
        else:
            image_numpy[mask] = polygon_color

    # Add border if specified
    if border_width > 0 and border_color is not None:
        # Border is a band around the edge
        border_mask = (np.abs(signed_dist) <= border_width / 2.0) & (signed_dist <= 0.5)

        if antialias:
            border_alpha_val = np.clip(border_width / 2.0 + 0.5 - np.abs(signed_dist), 0, 1) * border_alpha
            border_alpha_val = border_alpha_val * border_mask

            border_color_array = np.array(border_color)
            for i in range(3):
                image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - border_alpha_val) + \
                                      border_color_array[i] * border_alpha_val
        else:
            if border_alpha < 1.0:
                border_color_array = np.array(border_color)
                for i in range(3):
                    image_numpy[border_mask, i] = image_numpy[border_mask, i] * (1 - border_alpha) + \
                                                  border_color_array[i] * border_alpha
            else:
                image_numpy[border_mask] = border_color

    return image_numpy
