import numpy as np


def add_arrowed_line(image_numpy, line_color, start_point, end_point,
                     line_width=2,
                     arrow_start='none',  # 'none', 'out', 'in'
                     arrow_end='none',    # 'none', 'out', 'in'
                     arrow_length=30,
                     arrow_angle=30,      # angle between arrow fins and the main line (degrees)
                     circle_start='none',     # 'none', 'out', 'in' - circle marker at the start
                     circle_end='none',       # 'none', 'out', 'in' - circle marker at the end
                     circle_radius=20,        # circle marker radius
                     circle_filled=False,     # filled (True) or hollow (False) circle marker
                     dashed=False,        # draw a dashed line
                     dash_length=10,      # dash segment length
                     gap_length=5,        # gap length
                     draw_line=True,      # draw the main segment (False draws only the arrow fins)
                     antialias=True,
                     border_width=0, border_color=None, border_alpha=1.0):
    """
    Add an arrowed line (Müller-Lyer style) to the image numpy array
    
    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    line_color : tuple
        RGB color of the line (values 0-1)
    start_point : tuple (x, y)
        Start position of the line (column, row)
    end_point : tuple (x, y)
        End position of the line (column, row)
    line_width : float
        Width of the line in pixels (default: 2)
    arrow_start : str
        Arrow type at start: 'none', 'out' (>─), or 'in' (─<) (default: 'none')
        Ignored if circle_start is not 'none'
    arrow_end : str
        Arrow type at end: 'none', 'out' (─<), or 'in' (─>) (default: 'none')
        Ignored if circle_end is not 'none'
    arrow_length : float
        Length of arrow wings in pixels (default: 30)
    arrow_angle : float
        Angle of arrow wings relative to main line in degrees (default: 30)
    circle_start : str
        Circle at start: 'none', 'out' (circle extends outward), or 'in' (circle inside line) (default: 'none')
    circle_end : str
        Circle at end: 'none', 'out' (circle extends outward), or 'in' (circle inside line) (default: 'none')
    circle_radius : float
        Radius of circles at endpoints in pixels (default: 20)
    circle_filled : bool
        Whether circles are filled (True) or hollow rings (False) (default: False)
    dashed : bool
        Whether to draw dashed line (default: False)
    dash_length : float
        Length of dash segments in pixels (default: 10)
    gap_length : float
        Length of gaps between dashes in pixels (default: 5)
    draw_line : bool
        Whether to draw the main line segment; if False, only arrow fins are drawn (default: True)
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
        Modified image with arrowed line added
    """
    # Get image dimensions
    height, width = image_numpy.shape[:2]

    # Create coordinate grids
    yy, xx = np.mgrid[:height, :width].astype(float)

    # Calculate line direction
    start_x, start_y = float(start_point[0]), float(start_point[1])
    end_x, end_y = float(end_point[0]), float(end_point[1])
    dx = end_x - start_x
    dy = end_y - start_y
    line_length = np.sqrt(dx**2 + dy**2)

    if line_length == 0:
        return image_numpy

    # Normalized direction vector
    dir_x = dx / line_length
    dir_y = dy / line_length

    # Convert angle to radians
    angle_rad = np.deg2rad(arrow_angle)

    def distance_to_line_segment(px, py, x1, y1, x2, y2):
        """Calculate distance from points to line segment"""
        dx_seg = x2 - x1
        dy_seg = y2 - y1
        len_sq = dx_seg**2 + dy_seg**2

        if len_sq == 0:
            return np.sqrt((px - x1)**2 + (py - y1)**2)

        t = np.clip(((px - x1) * dx_seg + (py - y1) * dy_seg) / len_sq, 0, 1)
        proj_x = x1 + t * dx_seg
        proj_y = y1 + t * dy_seg

        return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)

    def distance_along_line(px, py, x1, y1, x2, y2):
        """Calculate distance along the line from start point"""
        dx_seg = x2 - x1
        dy_seg = y2 - y1
        len_sq = dx_seg**2 + dy_seg**2

        if len_sq == 0:
            return np.zeros_like(px)

        t = ((px - x1) * dx_seg + (py - y1) * dy_seg) / len_sq
        seg_length = np.sqrt(len_sq)

        return t * seg_length

    def apply_dash_pattern(alpha, px, py, x1, y1, x2, y2, dash_len, gap_len):
        """Apply dash pattern to alpha channel"""
        if not dashed:
            return alpha

        # Calculate distance along the line
        dist_along = distance_along_line(px, py, x1, y1, x2, y2)

        # Calculate dash pattern
        pattern_length = dash_len + gap_len
        position_in_pattern = np.mod(dist_along, pattern_length)

        # Only keep alpha where we're in a dash (not in a gap)
        if antialias:
            # Smooth transition at dash boundaries
            dash_mask = np.clip(dash_len + 0.5 - position_in_pattern, 0, 1)
        else:
            dash_mask = (position_in_pattern < dash_len).astype(float)

        return alpha * dash_mask

    def rotate_vector(vx, vy, angle):
        """Rotate a vector by angle (radians)"""
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        return vx * cos_a - vy * sin_a, vx * sin_a + vy * cos_a

    def draw_circle(center_x, center_y, radius, filled=False):
        """Draw a circle and return alpha channel"""
        dist_to_center = np.sqrt((xx - center_x)**2 + (yy - center_y)**2)

        if filled:
            # Filled circle
            if antialias:
                alpha = np.clip(radius + 0.5 - dist_to_center, 0, 1)
            else:
                alpha = (dist_to_center <= radius).astype(float)
        else:
            # Hollow circle (ring with thickness = line_width)
            dist_to_ring = np.abs(dist_to_center - radius)
            if antialias:
                alpha = np.clip(line_width/2.0 + 0.5 - dist_to_ring, 0, 1)
            else:
                alpha = (dist_to_ring <= line_width/2.0).astype(float)

        return alpha

    # Draw main line (only if draw_line is True)
    if draw_line:
        dist_to_line = distance_to_line_segment(xx, yy, start_x, start_y, end_x, end_y)

        if antialias:
            alpha_total = np.clip(line_width/2.0 + 0.5 - dist_to_line, 0, 1)
        else:
            alpha_total = (dist_to_line <= line_width/2.0).astype(float)

        # Apply dash pattern to main line
        alpha_total = apply_dash_pattern(alpha_total, xx, yy, start_x, start_y, end_x, end_y,
                                         dash_length, gap_length)
    else:
        # Initialize with no line, only arrow fins will be drawn
        alpha_total = np.zeros((height, width))

    # Handle start point (circle or arrow)
    if circle_start != 'none':
        # Draw circle at start
        if circle_start == 'out':
            # Circle center at start point (extends outward)
            circle_center_x = start_x
            circle_center_y = start_y
        else:  # 'in'
            # Circle center moved inward along the line
            circle_center_x = start_x + dir_x * circle_radius
            circle_center_y = start_y + dir_y * circle_radius

        alpha_circle_start = draw_circle(circle_center_x, circle_center_y, circle_radius, circle_filled)
        alpha_total = np.maximum(alpha_total, alpha_circle_start)
    elif arrow_start != 'none':
        # Draw arrow at start
        if arrow_start == 'out':
            # Arrow wings pointing outward: >─
            wing1_dx, wing1_dy = rotate_vector(dir_x, dir_y, angle_rad)
            wing1_end_x = start_x + wing1_dx * arrow_length
            wing1_end_y = start_y + wing1_dy * arrow_length

            wing2_dx, wing2_dy = rotate_vector(dir_x, dir_y, -angle_rad)
            wing2_end_x = start_x + wing2_dx * arrow_length
            wing2_end_y = start_y + wing2_dy * arrow_length
        else:  # 'in'
            # Arrow wings pointing inward: ─
            wing1_dx, wing1_dy = rotate_vector(-dir_x, -dir_y, angle_rad)
            wing1_end_x = start_x + wing1_dx * arrow_length
            wing1_end_y = start_y + wing1_dy * arrow_length

            wing2_dx, wing2_dy = rotate_vector(-dir_x, -dir_y, -angle_rad)
            wing2_end_x = start_x + wing2_dx * arrow_length
            wing2_end_y = start_y + wing2_dy * arrow_length

        # Draw both wings
        dist_wing1 = distance_to_line_segment(xx, yy, start_x, start_y, wing1_end_x, wing1_end_y)
        dist_wing2 = distance_to_line_segment(xx, yy, start_x, start_y, wing2_end_x, wing2_end_y)

        if antialias:
            alpha_wing1 = np.clip(line_width/2.0 + 0.5 - dist_wing1, 0, 1)
            alpha_wing2 = np.clip(line_width/2.0 + 0.5 - dist_wing2, 0, 1)
        else:
            alpha_wing1 = (dist_wing1 <= line_width/2.0).astype(float)
            alpha_wing2 = (dist_wing2 <= line_width/2.0).astype(float)

        # Apply dash pattern to wings
        alpha_wing1 = apply_dash_pattern(alpha_wing1, xx, yy, start_x, start_y,
                                         wing1_end_x, wing1_end_y, dash_length, gap_length)
        alpha_wing2 = apply_dash_pattern(alpha_wing2, xx, yy, start_x, start_y,
                                         wing2_end_x, wing2_end_y, dash_length, gap_length)

        alpha_total = np.maximum(alpha_total, np.maximum(alpha_wing1, alpha_wing2))

    # Handle end point (circle or arrow)
    if circle_end != 'none':
        # Draw circle at end
        if circle_end == 'out':
            # Circle center at end point (extends outward)
            circle_center_x = end_x
            circle_center_y = end_y
        else:  # 'in'
            # Circle center moved inward along the line
            circle_center_x = end_x - dir_x * circle_radius
            circle_center_y = end_y - dir_y * circle_radius

        alpha_circle_end = draw_circle(circle_center_x, circle_center_y, circle_radius, circle_filled)
        alpha_total = np.maximum(alpha_total, alpha_circle_end)
    elif arrow_end != 'none':
        # Draw arrow at end
        if arrow_end == 'out':
            # Arrow wings pointing outward: ─
            wing1_dx, wing1_dy = rotate_vector(-dir_x, -dir_y, angle_rad)
            wing1_end_x = end_x + wing1_dx * arrow_length
            wing1_end_y = end_y + wing1_dy * arrow_length

            wing2_dx, wing2_dy = rotate_vector(-dir_x, -dir_y, -angle_rad)
            wing2_end_x = end_x + wing2_dx * arrow_length
            wing2_end_y = end_y + wing2_dy * arrow_length
        else:  # 'in'
            # Arrow wings pointing inward: ─>
            wing1_dx, wing1_dy = rotate_vector(dir_x, dir_y, angle_rad)
            wing1_end_x = end_x + wing1_dx * arrow_length
            wing1_end_y = end_y + wing1_dy * arrow_length

            wing2_dx, wing2_dy = rotate_vector(dir_x, dir_y, -angle_rad)
            wing2_end_x = end_x + wing2_dx * arrow_length
            wing2_end_y = end_y + wing2_dy * arrow_length

        # Draw both wings
        dist_wing1 = distance_to_line_segment(xx, yy, end_x, end_y, wing1_end_x, wing1_end_y)
        dist_wing2 = distance_to_line_segment(xx, yy, end_x, end_y, wing2_end_x, wing2_end_y)

        if antialias:
            alpha_wing1 = np.clip(line_width/2.0 + 0.5 - dist_wing1, 0, 1)
            alpha_wing2 = np.clip(line_width/2.0 + 0.5 - dist_wing2, 0, 1)
        else:
            alpha_wing1 = (dist_wing1 <= line_width/2.0).astype(float)
            alpha_wing2 = (dist_wing2 <= line_width/2.0).astype(float)

        # Apply dash pattern to wings
        alpha_wing1 = apply_dash_pattern(alpha_wing1, xx, yy, end_x, end_y,
                                         wing1_end_x, wing1_end_y, dash_length, gap_length)
        alpha_wing2 = apply_dash_pattern(alpha_wing2, xx, yy, end_x, end_y,
                                         wing2_end_x, wing2_end_y, dash_length, gap_length)

        alpha_total = np.maximum(alpha_total, np.maximum(alpha_wing1, alpha_wing2))

    # Blend colors
    line_color_array = np.array(line_color)
    for i in range(3):
        image_numpy[:, :, i] = image_numpy[:, :, i] * (1 - alpha_total) + line_color_array[i] * alpha_total

    return image_numpy
