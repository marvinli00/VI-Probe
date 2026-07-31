def hsl_to_rgb(hsl):
    """
    Convert an HSL color to RGB.
    
    Args:
        hsl: tuple of (h, s, l) where each value is in range [0, 1]
    
    Returns:
        tuple of (r, g, b) where each value is in range [0, 1]
    """
    h, s, l = hsl

    if s == 0:
        # zero saturation -> gray
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p

        if l < 0.5:
            q = l * (1 + s)
        else:
            q = l + s - l * s

        p = 2 * l - q

        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return (r, g, b)

def hsb_to_rgb(hsb):
    h = hsb[0]
    s = hsb[1]
    b = hsb[2]
    """Convert HSB to RGB (h: 0-1, s: 0-1, b: 0-1) -> (r: 0-1, g: 0-1, b: 0-1)."""
    if s == 0:
        r = g = b = b  # gray
    else:
        h = h * 6.0  # sector 0-6
        i = int(h)
        f = h - i
        p = b * (1 - s)
        q = b * (1 - s * f)
        t = b * (1 - s * (1 - f))

        sector = i % 6
        if sector == 0:
            r, g, b = b, t, p
        elif sector == 1:
            r, g, b = q, b, p
        elif sector == 2:
            r, g, b = p, b, t
        elif sector == 3:
            r, g, b = p, q, b
        elif sector == 4:
            r, g, b = t, p, b
        else:
            r, g, b = b, p, q

    return (r, g, b)


def rgb_to_hsl(rgb):
    """
    Convert an RGB color to HSL.
    
    Args:
        rgb: tuple of (r, g, b) where each value is in range [0, 1]
    
    Returns:
        tuple of (h, s, l) where each value is in range [0, 1]
    """
    r, g, b = rgb
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val

    # lightness
    l = (max_val + min_val) / 2

    # max == min -> zero saturation, hue undefined (set to 0)
    if diff == 0:
        h = 0
        s = 0
    else:
        # saturation
        if l < 0.5:
            s = diff / (max_val + min_val)
        else:
            s = diff / (2.0 - max_val - min_val)

        # hue
        if max_val == r:
            h = (g - b) / diff + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4

        h /= 6  # normalize to [0, 1]

    return (h, s, l)



def rgb_to_hsb(rgb):
    """
    Convert an RGB color to HSB (a.k.a. HSV).
    
    Args:
        rgb: tuple of (r, g, b) where each value is in range [0, 1]
    
    Returns:
        tuple of (h, s, b) where each value is in range [0, 1]
    """
    r, g, b = rgb
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val

    # brightness / value
    brightness = max_val

    # max == 0 -> zero saturation, hue undefined (set to 0)
    if max_val == 0:
        h = 0
        s = 0
    else:
        # saturation
        s = diff / max_val

        # zero saturation -> hue undefined (set to 0)
        if diff == 0:
            h = 0
        else:
            # hue
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4

            h /= 6  # normalize to [0, 1]

    return (h, s, brightness)
