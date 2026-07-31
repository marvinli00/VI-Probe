"""Image saving/loading for float [0, 1] RGB numpy arrays."""

from pathlib import Path
from typing import Union

import numpy as np
import PIL.Image


def to_uint8(array: np.ndarray) -> np.ndarray:
    """Convert a float [0, 1] RGB array to uint8 exactly as the published
    dataset was rendered: (array * 255) truncated, no rounding, no clipping."""
    return (array * 255).astype(np.uint8)


def save_image(array: np.ndarray, path: Union[str, Path]) -> None:
    """Save a float [0, 1] RGB array as a PNG (or any PIL-supported format)."""
    PIL.Image.fromarray(to_uint8(array)).save(str(path))


def show_image(array: np.ndarray):
    """Display the array with matplotlib (for notebooks/interactive use)."""
    import matplotlib.pyplot as plt

    return plt.imshow(array)


def convert_numpy_to_image(numpy_array: np.ndarray, save_path=None):
    """Backward-compatible alias for the original helper of the same name.

    Saves when ``save_path`` is given; unlike the original it does not also
    render a matplotlib figure on every save (which leaked figures during
    large sweeps). Returns the matplotlib image handle only in show mode.
    """
    if save_path is not None:
        save_image(numpy_array, save_path)
        return None
    return show_image(numpy_array)
