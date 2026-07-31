import numpy as np


def calculate_gradient(color1, color2, steps):
    """
    Calculate the linear gradient between two colors
    """
    color1 = np.array(color1)
    color2 = np.array(color2)
    gradient = np.zeros((steps, 3))
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        gradient[i] = color1 * (1 - t) + color2 * t
    return gradient



# Method 1: gamma correction (simple and efficient)
def calculate_perceptual_gradient_gamma(color1, color2, steps, gamma=2.2):
    """
    Calculate perceptually uniform gradient using gamma correction
    
    Args:
        color1: Starting color (RGB, 0-255)
        color2: Ending color (RGB, 0-255)
        steps: Number of steps
        gamma: Gamma value (typically 2.2 for sRGB)
    """
    color1 = np.array(color1) / 255.0
    color2 = np.array(color2) / 255.0

    # Convert to linear space
    color1_linear = np.power(color1, gamma)
    color2_linear = np.power(color2, gamma)

    gradient = np.zeros((steps, 3))
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        # Linear interpolation in linear space
        linear_color = color1_linear * (1 - t) + color2_linear * t
        # Convert back to gamma space
        gradient[i] = np.power(linear_color, 1/gamma) * 255

    return gradient.astype(np.uint8)


# Method 2: LAB color space (more accurate)
def rgb_to_lab(rgb):
    """
    Convert RGB to LAB color space
    
    Args:
        rgb: RGB values in range [0, 1]
    
    Returns:
        LAB values
    """
    rgb = np.array(rgb)

    # Convert to linear RGB
    rgb_linear = np.where(rgb > 0.04045,
                          np.power((rgb + 0.055) / 1.055, 2.4),
                          rgb / 12.92)

    # RGB to XYZ
    xyz = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041]
    ]) @ rgb_linear

    # XYZ to LAB (D65 illuminant)
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    xyz = np.where(xyz > 0.008856,
                   np.power(xyz, 1/3),
                   (7.787 * xyz) + (16/116))

    L = (116 * xyz[1]) - 16
    a = 500 * (xyz[0] - xyz[1])
    b = 200 * (xyz[1] - xyz[2])

    return np.array([L, a, b])


def lab_to_rgb(lab):
    """
    Convert LAB to RGB color space
    
    Args:
        lab: LAB values
    
    Returns:
        RGB values in range [0, 1]
    """
    L, a, b = lab

    # LAB to XYZ
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    xyz = np.array([fx, fy, fz])
    xyz = np.where(np.power(xyz, 3) > 0.008856,
                   np.power(xyz, 3),
                   (xyz - 16/116) / 7.787)

    xyz = xyz * np.array([0.95047, 1.0, 1.08883])

    # XYZ to RGB
    rgb_linear = np.array([
        [ 3.2404542, -1.5371385, -0.4985314],
        [-0.9692660,  1.8760108,  0.0415560],
        [ 0.0556434, -0.2040259,  1.0572252]
    ]) @ xyz

    # Convert to sRGB
    rgb = np.where(rgb_linear > 0.0031308,
                   1.055 * np.power(rgb_linear, 1/2.4) - 0.055,
                   12.92 * rgb_linear)

    return np.clip(rgb, 0, 1)

def calculate_perceptual_gradient_lab(color1, color2, steps):
    """
    Calculate perceptually uniform gradient using LAB color space
    
    Args:
        color1: Starting color (R, G, B) in range [0, 1]
        color2: Ending color (R, G, B) in range [0, 1]
        steps: Number of steps
    
    Returns:
        Array of shape (steps, 3) with RGB values in range [0, 1]
    """
    lab1 = rgb_to_lab(color1)
    lab2 = rgb_to_lab(color2)

    gradient = np.zeros((steps, 3))
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        # Linear interpolation in LAB space
        lab_color = lab1 * (1 - t) + lab2 * t
        gradient[i] = lab_to_rgb(lab_color)

    return gradient
