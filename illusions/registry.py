"""Registry of every illusion in the VI-Probe generator.

Each :class:`IllusionSpec` records where the class lives, its case number in
the released dataset (1-27, matching the paper and the HuggingFace release),
and the *legacy* class names used by the published metadata (including
historical typos such as ``CornswweetIllusion``), so that sweeps driven by
the frozen configs emit the published folder names and metadata.
"""

from dataclasses import dataclass
from importlib import import_module
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class IllusionSpec:
    name: str                      # registry key (snake_case)
    module: str                    # import path within illusions/
    class_name: str                # current (corrected) class name
    display_name: str
    categories: Tuple[str, ...]    # published categories this case appears in
    number_prefix: Optional[int] = None   # case number in the released dataset (1-27)
    legacy_class_name: Optional[str] = None  # published class_name metadata value

    @property
    def legacy_folder(self) -> Optional[str]:
        if self.number_prefix is None:
            return None
        return f"{self.number_prefix}_{self.legacy_class_name or self.class_name}"

    def load(self):
        return getattr(import_module(self.module), self.class_name)


def _spec(name, module, class_name, display_name, categories, number_prefix=None,
          legacy_class_name=None):
    return IllusionSpec(
        name=name,
        module=f"illusions.{module}",
        class_name=class_name,
        display_name=display_name,
        categories=categories,
        number_prefix=number_prefix,
        legacy_class_name=legacy_class_name or class_name,
    )


SPECS = [
    # -- size (released cases 1-11) ------------------------------------------
    _spec("muller_lyer", "length.muller_lyer", "MullerLyerIllusion", "Muller Lyer Illusion", ("size",), 1),
    _spec("circle_muller_lyer", "length.circle_muller_lyer", "CircleMullerLyerIllusion", "Circle Muller Lyer Illusion", ("size",), 2),
    _spec("ponzo", "length.ponzo", "PonzoIllusion", "Ponzo Illusion", ("size",), 3),
    _spec("ponzo_trapezoid", "length.ponzo_trapezoid", "PonzoTrapezoidIllusion", "Ponzo Trapezoid Illusion", ("size",), 4),
    _spec("ebbinghaus", "length.ebbinghaus", "EbbinghausIllusion", "Ebbinghaus Illusion", ("size",), 5),
    _spec("ebbinghaus_rectangular", "length.ebbinghaus_rectangular", "EbbinghausIllusionRectangular", "Ebbinghaus Illusion Rectangular", ("size",), 6),
    _spec("delboeuf", "length.delboeuf", "DelboeufIllusion", "Delboeuf Illusion", ("size",), 7),
    _spec("oppel_kundt", "length.oppel_kundt", "OppelKundtIllusion", "Oppel Kundt Illusion", ("size",), 8),
    _spec("irradiation", "length.irradiation", "IrradiationIllusion", "Irradiation Illusion", ("size",), 9),
    _spec("irradiation_pentagon", "length.irradiation_pentagon", "IrradiationPentagonIllusion", "Irradiation Pentagon Illusion", ("size",), 10),
    _spec("circle_ponzo", "length.circle_ponzo", "CirclePonzoIllusion", "Circle Ponzo Illusion", ("size",), 11),
    # -- color (released cases 12-18) ----------------------------------------
    _spec("cornsweet", "color.cornsweet", "CornsweetIllusion", "Cornsweet Illusion", ("color",), 12,
          legacy_class_name="CornswweetIllusion"),
    _spec("simultaneous_contrast", "color.simultaneous_contrast", "SimultaneousContrastIllusion", "Simultaneous Contrast Illusion", ("color",), 13),
    _spec("munker_white", "color.munker_white", "MunkerWhiteIllusion", "Munker White Illusion", ("color",), 14),
    _spec("mach_band", "color.mach_band", "MachBandIllusion", "Mach Band Illusion", ("color",), 15),
    _spec("mach_band_case2", "color.mach_band_case2", "MachBandIllusionCase2", "Mach Band Illusion Case2", ("color",), 16,
          legacy_class_name="MachBandIllusion_Case2"),
    _spec("chubb", "color.chubb", "ChubbIllusion", "Chubb Illusion", ("color",), 17),
    _spec("cornsweet_case1", "color.cornsweet_case1", "CornsweetIllusionCase1", "Cornsweet Illusion Case1", ("color",), 18,
          legacy_class_name="CornswweetIllusionCase1"),
    # -- orientation (released cases 19-27) ----------------------------------
    _spec("hering", "orientation.hering", "HeringIllusion", "Hering Illusion", ("orientation",), 19),
    _spec("hering_vertical", "orientation.hering_vertical", "HeringIllusionVertical", "Hering Illusion Vertical", ("orientation",), 20),
    _spec("zollner", "orientation.zollner", "ZollnerIllusion", "Zollner Illusion", ("orientation",), 21),
    _spec("zollner_vertical", "orientation.zollner_vertical", "ZollnerIllusionVertical", "Zollner Illusion Vertical", ("orientation",), 22),
    _spec("twisted_cord", "orientation.twisted_cord", "TwistedCordIllusion", "Twisted Cord Illusion", ("orientation",), 23),
    _spec("twisted_cord_light", "orientation.twisted_cord_light", "TwistedCordIllusionLight", "Twisted Cord Illusion Light", ("orientation",), 24),
    _spec("poggendorff", "orientation.poggendorff", "PoggendorffIllusion", "Poggendorff Illusion", ("orientation",), 25),
    _spec("poggendorff_horizontal", "orientation.poggendorff_horizontal", "PoggendorffHorizontalIllusion", "Poggendorff Horizontal Illusion", ("orientation",), 26),
    _spec("ehrenstein", "orientation.ehrenstein", "EhrensteinIllusion", "Ehrenstein Illusion", ("orientation",), 27),
]

_BY_KEY: Dict[str, IllusionSpec] = {}
for s in SPECS:
    for key in {s.name, s.class_name, s.legacy_class_name}:
        if key:
            _BY_KEY.setdefault(key, s)


def all_specs():
    return list(SPECS)


def get_spec(key: str) -> IllusionSpec:
    """Look up a spec by registry name, class name, or legacy class name."""
    try:
        return _BY_KEY[key]
    except KeyError:
        raise KeyError(
            f"Unknown illusion {key!r}. Known: {sorted(s.name for s in SPECS)}"
        ) from None


def get_illusion(key: str):
    """Return the illusion class for a registry key."""
    return get_spec(key).load()


def resolve_class(key: str):
    """Alias of :func:`get_illusion` (accepts legacy class names too)."""
    return get_spec(key).load()
