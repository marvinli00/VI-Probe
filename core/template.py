"""Abstract base class for optical illusion generators.

Every illusion in :mod:`illusions` subclasses
:class:`IllusionTemplate` and implements the element/drawing hooks; the base
class orchestrates the six published image variants
(``original``, ``original_with_guide``, ``original_control``, ``perturbed``,
``perturbed_with_guide``, ``perturbed_control``) and the strength sweep.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from .image_io import save_image, show_image


class IllusionTemplate(ABC):
    """Base class for optical illusion generation.

    Subclasses must implement :meth:`define_elements` and
    :meth:`generate_illusion`, and typically override
    :meth:`add_visual_guides`, :meth:`apply_control_modification` and
    :meth:`apply_perturbation`.
    """

    def __init__(
        self,
        illusion_name: str,
        width: int = 512,
        height: int = 256,
        strength_levels: Optional[List[float]] = None,
        background_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        output_base_dir: Optional[Union[str, Path]] = None,
    ):
        """
        Args:
            illusion_name: Name of the illusion (e.g. ``'muller_lyer'``).
                Used as the output subdirectory name.
            width: Image width in pixels.
            height: Image height in pixels.
            strength_levels: Strength levels rendered by ``generate_all*``.
            background_color: RGB background color (0-1 range).
            output_base_dir: Base directory for saved images
                (default: ``<cwd>/output``). Directories are created lazily
                on first save.
        """
        self.illusion_name = illusion_name
        self.width = width
        self.height = height
        self.strength_levels = strength_levels or [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
        self.background_color = background_color

        # Variation flags (see set_variation)
        self.is_control = False
        self.is_perturbed = False
        self.is_original = True
        self.has_visual_guide = False

        # Element storage
        self.elements: Dict[str, Any] = {}

        self.output_base_dir = Path(output_base_dir) if output_base_dir else Path.cwd() / "output"
        self.output_dir = self.output_base_dir / illusion_name

    def set_output_dir(self, base_dir: Union[str, Path], subdir: Optional[str] = None) -> None:
        """Point saved images at ``base_dir/<subdir or illusion_name>/...``."""
        self.output_base_dir = Path(base_dir)
        self.output_dir = self.output_base_dir / (subdir or self.illusion_name)

    def set_variation(
        self,
        control: bool = False,
        perturbed: bool = False,
        original: bool = False,
        visual_guide: bool = False,
    ) -> None:
        """Select which of the six variants subsequent ``generate`` calls render.

        Exactly one of ``perturbed``/``original`` may be True (``control``
        combines with either). If all are False, ``original`` is assumed.
        Control versions never carry visual guides.
        """
        if not (control or perturbed or original):
            original = True

        if sum([perturbed, original]) > 1:
            raise ValueError("Only one of control, perturbed, or original can be True")

        self.is_control = control
        self.is_perturbed = perturbed
        self.is_original = original
        self.has_visual_guide = visual_guide

        if control:
            self.has_visual_guide = False

    def _get_variation_folder(self) -> str:
        """Subfolder name for the current variation settings."""
        if self.is_control:
            if self.is_perturbed:
                return "perturbed_control"
            if self.is_original:
                return "original_control"
            raise ValueError("Control variation must be either original or perturbed")
        elif self.is_perturbed:
            return "perturbed_with_guide" if self.has_visual_guide else "perturbed"
        else:  # original
            return "original_with_guide" if self.has_visual_guide else "original"

    def get_save_path(self, strength: Optional[float] = None) -> Path:
        """Path for saving the current variant: ``output_dir/<variation>/strength_*.png``."""
        save_dir = self.output_dir / self._get_variation_folder()
        save_dir.mkdir(parents=True, exist_ok=True)

        if strength is not None:
            strength_str = f"{strength:+.1f}".replace(".", "p").replace("+", "pos").replace("-", "neg")
            filename = f"strength_{strength_str}.png"
        else:
            filename = f"{self.illusion_name}.png"

        return save_dir / filename

    def initialize_canvas(self) -> np.ndarray:
        """Blank float32 canvas filled with the background color."""
        image = np.ones((self.height, self.width, 3), dtype=np.float32)
        for i in range(3):
            image[:, :, i] *= self.background_color[i]
        return image

    @abstractmethod
    def define_elements(self, strength: float, is_original: bool) -> Dict[str, Any]:
        """Return the drawable elements for a given strength level.

        The returned dict holds every parameter needed to draw the illusion
        (positions, sizes, colors, ...); it is the input to
        :meth:`generate_illusion` and to the control/perturbation hooks.
        """

    @abstractmethod
    def generate_illusion(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """Draw the illusion elements onto the canvas and return the image."""

    def add_visual_guides(self, image: np.ndarray, elements: Dict[str, Any]) -> np.ndarray:
        """Add guide bars/markers for the ``*_with_guide`` variants.

        Default: no guides. Override in subclasses.
        """
        return image

    def apply_control_modification(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Transform elements into the control condition (no illusion effect).

        Default: unchanged. Override in subclasses.
        """
        return elements

    def apply_perturbation(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Transform elements into the perturbed condition.

        Default: unchanged. Override in subclasses.
        """
        return elements

    def generate(
        self,
        strength: float = 0.0,
        save: bool = True,
        show: bool = False,
        save_path: Optional[Union[str, Path]] = None,
        is_guide_first: bool = False,
    ) -> np.ndarray:
        """Render a single image for the current variation at ``strength``.

        Args:
            strength: Illusion strength level.
            save: Write a PNG to :meth:`get_save_path` (or ``save_path``).
            show: Display the image with matplotlib.
            save_path: Explicit output path overriding the naming convention.
            is_guide_first: Draw visual guides beneath the illusion instead
                of on top.

        Returns:
            The rendered image as a float32 array in [0, 1].
        """
        elements = self.define_elements(strength, is_original=self.is_original)

        if self.is_control:
            elements = self.apply_control_modification(elements)
        if self.is_perturbed:
            elements = self.apply_perturbation(elements)

        image = self.initialize_canvas()
        if is_guide_first and self.has_visual_guide:
            image = self.add_visual_guides(image, elements)
        image = self.generate_illusion(image, elements)
        if self.has_visual_guide and not is_guide_first:
            image = self.add_visual_guides(image, elements)

        if save:
            path = Path(save_path) if save_path is not None else self.get_save_path(strength)
            path.parent.mkdir(parents=True, exist_ok=True)
            save_image(image, path)

        if show:
            show_image(image)

        return image

    #: The six published variants, in the original generation order.
    VARIATIONS = (
        {"control": True, "perturbed": False, "original": True, "visual_guide": False},
        {"control": False, "perturbed": False, "original": True, "visual_guide": False},
        {"control": False, "perturbed": False, "original": True, "visual_guide": True},
        {"control": False, "perturbed": True, "original": False, "visual_guide": False},
        {"control": False, "perturbed": True, "original": False, "visual_guide": True},
        {"control": True, "perturbed": True, "original": False, "visual_guide": False},
    )

    def generate_all_variations(self, strength: float = 0.0, is_guide_first: bool = False) -> None:
        """Render and save all six variants at one strength level."""
        for var in self.VARIATIONS:
            self.set_variation(**var)
            self.generate(strength=strength, save=True, show=False, is_guide_first=is_guide_first)

    def generate_all_strengths(self, include_variations: bool = True) -> None:
        """Render every strength level, optionally with all variants."""
        for strength in self.strength_levels:
            if include_variations:
                self.generate_all_variations(strength)
            else:
                self.generate(strength=strength, save=True, show=False)

    def generate_all(self, strength_min: float = -1.0, is_guide_first: bool = False) -> None:
        """Render all variants for every strength level >= ``strength_min``."""
        filtered_strengths = [s for s in self.strength_levels if s >= strength_min]
        for strength in filtered_strengths:
            self.generate_all_variations(strength, is_guide_first=is_guide_first)
