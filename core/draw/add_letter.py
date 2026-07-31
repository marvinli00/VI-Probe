"""
Letter and Number Drawing Module

This module provides functionality to draw uppercase letters (A-Z) and numbers (0-9)
on numpy image arrays with support for anti-aliasing, borders, rotation, and custom colors.

Uses PIL/Pillow for robust text rendering, then converts back to numpy array.
"""


import numpy as np
from PIL import Image, ImageDraw, ImageFont


def add_letter(image_numpy, letter, letter_color, center, height,
               rotation_angle=0, antialias=True,
               border_width=0, border_color=None, border_alpha=1.0):
    """
    Add a letter or number to the image numpy array with anti-aliasing and styling options.

    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    letter : str
        Character to draw: uppercase letters 'A'-'Z' or numbers '0'-'9'
    letter_color : tuple or numpy.ndarray
        - If tuple: RGB color of the letter (values 0-1)
        - If numpy.ndarray: Not supported in this implementation, will use tuple fallback
    center : tuple (x, y)
        Center position of the letter (column, row)
    height : float
        Height of the letter in pixels (width is auto-calculated)
    rotation_angle : float
        Rotation angle in degrees (default: 0)
        Positive = counterclockwise, Negative = clockwise
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
        Modified image with letter added

    Example:
    --------
    >>> image = np.ones((512, 512, 3))
    >>> image = add_letter(image, 'A', (0, 0, 0), (256, 256), height=100)
    >>> image = add_letter(image, '5', (1, 0, 0), (128, 128), height=80, rotation_angle=45)
    """
    # Validate letter
    letter = str(letter).upper()
    if len(letter) != 1 or letter not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
        raise ValueError(f"Letter must be a single character A-Z or 0-9, got: {letter}")

    # Handle numpy array color (convert to tuple)
    if isinstance(letter_color, np.ndarray):
        letter_color = tuple(letter_color.flatten()[:3])

    # Convert image from float [0,1] to uint8 [0,255]
    image_uint8 = (np.clip(image_numpy, 0, 1) * 255).astype(np.uint8)

    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(image_uint8, mode='RGB')
    draw = ImageDraw.Draw(pil_image)

    # Load a monospace font - try to find a suitable system font
    # Font size needs to be calibrated to match desired height
    font_size = int(height * 1.3)  # Empirical scaling factor
    font = _get_font(font_size)

    # Convert color from [0,1] to [0,255]
    text_color_255 = tuple(int(c * 255) for c in letter_color[:3])
    if border_color is not None:
        border_color_255 = tuple(int(c * 255) for c in border_color[:3])
    else:
        border_color_255 = None

    # Get text bounding box to calculate proper positioning
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate top-left position from center
    # Account for bbox offsets
    text_x = center[0] - text_width / 2 - bbox[0]
    text_y = center[1] - text_height / 2 - bbox[1]

    # If rotation is needed, draw on a temporary transparent image
    if rotation_angle != 0:
        # Create a larger temporary image with transparency
        temp_size = int(max(text_width, text_height) * 3)
        temp_image = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_image)

        # Draw text at center of temp image
        temp_center_x = temp_size / 2 - text_width / 2 - bbox[0]
        temp_center_y = temp_size / 2 - text_height / 2 - bbox[1]

        # Draw border if specified
        if border_width > 0 and border_color_255 is not None:
            # Draw multiple offset copies for border effect
            for offset_x in range(-int(border_width), int(border_width) + 1):
                for offset_y in range(-int(border_width), int(border_width) + 1):
                    if offset_x*offset_x + offset_y*offset_y <= border_width*border_width:
                        temp_draw.text(
                            (temp_center_x + offset_x, temp_center_y + offset_y),
                            letter,
                            font=font,
                            fill=border_color_255 + (int(border_alpha * 255),)
                        )

        # Draw main text
        temp_draw.text(
            (temp_center_x, temp_center_y),
            letter,
            font=font,
            fill=text_color_255 + (255,)
        )

        # Rotate the temporary image
        rotated = temp_image.rotate(-rotation_angle, resample=Image.BICUBIC if antialias else Image.NEAREST, expand=False)

        # Paste onto main image
        # Calculate paste position
        paste_x = int(center[0] - temp_size / 2)
        paste_y = int(center[1] - temp_size / 2)

        # Convert main image to RGBA for compositing
        pil_image_rgba = pil_image.convert('RGBA')
        pil_image_rgba.paste(rotated, (paste_x, paste_y), rotated)
        pil_image = pil_image_rgba.convert('RGB')
    else:
        # Draw without rotation
        # Draw border if specified
        if border_width > 0 and border_color_255 is not None:
            # Draw multiple offset copies for border effect
            for offset_x in range(-int(border_width), int(border_width) + 1):
                for offset_y in range(-int(border_width), int(border_width) + 1):
                    if offset_x*offset_x + offset_y*offset_y <= border_width*border_width:
                        draw.text(
                            (text_x + offset_x, text_y + offset_y),
                            letter,
                            font=font,
                            fill=border_color_255
                        )

        # Draw main text
        draw.text((text_x, text_y), letter, font=font, fill=text_color_255)

    # Convert back to numpy array
    result_uint8 = np.array(pil_image)

    # Convert back to float [0,1]
    result_float = result_uint8.astype(np.float32) / 255.0

    return result_float


def _get_font(size):
    """
    Get a suitable monospace font for rendering letters.

    Tries to load system fonts in order of preference.
    Falls back to PIL's default font if none available.
    """
    # List of fonts to try (in order of preference)
    font_names = [
        # macOS fonts
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/SFNSMono.ttf',
        '/Library/Fonts/Arial.ttf',
        # Linux fonts
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
        # Windows fonts
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/cour.ttf',
    ]

    # Try each font
    for font_path in font_names:
        try:
            return ImageFont.truetype(font_path, size)
        except (IOError, OSError):
            continue

    # Try loading a default TrueType font
    try:
        return ImageFont.load_default()
    except:
        # If all else fails, return None (PIL will use built-in bitmap font)
        return None


def add_text(image_numpy, text, text_color, start_position, letter_height,
             letter_spacing=None, rotation_angle=0, antialias=True,
             border_width=0, border_color=None, border_alpha=1.0):
    """
    Add a string of text (multiple letters/numbers) to the image.

    Parameters:
    -----------
    image_numpy : numpy.ndarray
        Input image as numpy array with shape (height, width, 3)
    text : str
        Text string to draw (uppercase letters A-Z and numbers 0-9)
    text_color : tuple or numpy.ndarray
        RGB color of the text (values 0-1)
    start_position : tuple (x, y)
        Starting position for the first character (column, row)
    letter_height : float
        Height of each letter in pixels
    letter_spacing : float, optional
        Horizontal spacing between letters in pixels
        If None, defaults to letter_height * 0.2
    rotation_angle : float
        Rotation angle in degrees (default: 0)
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
        Modified image with text added

    Example:
    --------
    >>> image = np.ones((512, 512, 3))
    >>> image = add_text(image, 'HELLO', (0, 0, 0), (100, 256), letter_height=50)
    """
    if letter_spacing is None:
        letter_spacing = letter_height * 0.2

    # Handle numpy array color (convert to tuple)
    if isinstance(text_color, np.ndarray):
        text_color = tuple(text_color.flatten()[:3])

    # Convert image from float [0,1] to uint8 [0,255]
    image_uint8 = (np.clip(image_numpy, 0, 1) * 255).astype(np.uint8)

    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(image_uint8, mode='RGB')
    draw = ImageDraw.Draw(pil_image)

    # Load font
    font_size = int(letter_height * 1.3)
    font = _get_font(font_size)

    # Convert color from [0,1] to [0,255]
    text_color_255 = tuple(int(c * 255) for c in text_color[:3])
    if border_color is not None:
        border_color_255 = tuple(int(c * 255) for c in border_color[:3])
    else:
        border_color_255 = None

    # Calculate character spacing
    # Get approximate width of a single character
    bbox = draw.textbbox((0, 0), 'A', font=font)
    char_width = bbox[2] - bbox[0]
    advance = char_width + letter_spacing

    # Process text
    text = text.upper()
    current_x = start_position[0]
    current_y = start_position[1]

    # For rotation, render entire text and rotate
    if rotation_angle != 0:
        # Calculate total text dimensions
        full_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = full_bbox[2] - full_bbox[0]
        text_height = full_bbox[3] - full_bbox[1]

        # Create temporary image
        temp_size = int(max(text_width, text_height) * 3)
        temp_image = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_image)

        # Draw text at center
        temp_x = temp_size / 2 - text_width / 2 - full_bbox[0]
        temp_y = temp_size / 2 - text_height / 2 - full_bbox[1]

        # Draw border if specified
        if border_width > 0 and border_color_255 is not None:
            for offset_x in range(-int(border_width), int(border_width) + 1):
                for offset_y in range(-int(border_width), int(border_width) + 1):
                    if offset_x*offset_x + offset_y*offset_y <= border_width*border_width:
                        temp_draw.text(
                            (temp_x + offset_x, temp_y + offset_y),
                            text,
                            font=font,
                            fill=border_color_255 + (int(border_alpha * 255),)
                        )

        # Draw main text
        temp_draw.text((temp_x, temp_y), text, font=font, fill=text_color_255 + (255,))

        # Rotate
        rotated = temp_image.rotate(-rotation_angle, resample=Image.BICUBIC if antialias else Image.NEAREST)

        # Paste onto main image
        paste_x = int(start_position[0] - temp_size / 2 + text_width / 2)
        paste_y = int(start_position[1] - temp_size / 2 + text_height / 2)

        pil_image_rgba = pil_image.convert('RGBA')
        pil_image_rgba.paste(rotated, (paste_x, paste_y), rotated)
        pil_image = pil_image_rgba.convert('RGB')
    else:
        # Draw without rotation - just render entire text at once
        bbox = draw.textbbox((0, 0), text, font=font)
        text_height = bbox[3] - bbox[1]
        text_x = start_position[0] - bbox[0]
        text_y = start_position[1] - text_height / 2 - bbox[1]

        # Draw border if specified
        if border_width > 0 and border_color_255 is not None:
            for offset_x in range(-int(border_width), int(border_width) + 1):
                for offset_y in range(-int(border_width), int(border_width) + 1):
                    if offset_x*offset_x + offset_y*offset_y <= border_width*border_width:
                        draw.text(
                            (text_x + offset_x, text_y + offset_y),
                            text,
                            font=font,
                            fill=border_color_255
                        )

        # Draw main text
        draw.text((text_x, text_y), text, font=font, fill=text_color_255)

    # Convert back to numpy array
    result_uint8 = np.array(pil_image)

    # Convert back to float [0,1]
    result_float = result_uint8.astype(np.float32) / 255.0

    return result_float
