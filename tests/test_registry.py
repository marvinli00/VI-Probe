"""Every registered illusion loads, instantiates, and renders all six variants."""

import numpy as np
import pytest

from core.template import IllusionTemplate
from illusions.registry import all_specs

SPECS = all_specs()


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_class_loads_and_renders(spec, tmp_path):
    cls = spec.load()
    assert issubclass(cls, IllusionTemplate)

    instance = cls()
    instance.set_output_dir(tmp_path)

    for var in IllusionTemplate.VARIATIONS:
        instance.set_variation(**var)
        np.random.seed(0)
        try:
            image = instance.generate(strength=1.0, save=False, show=False)
        except ImportError as e:
            pytest.skip(str(e))  # OpenCV-backed illusions without cv2 installed
        assert image.shape == (instance.height, instance.width, 3)
        assert image.dtype == np.float32


def test_registry_names_unique():
    names = [s.name for s in SPECS]
    assert len(names) == len(set(names))


def test_case_numbering_matches_released_taxonomy():
    by_cat = {}
    for s in SPECS:
        for c in s.categories:
            by_cat.setdefault(c, []).append(s)
    assert len(by_cat["size"]) == 11
    assert len(by_cat["color"]) == 7
    assert len(by_cat["orientation"]) == 9
    # released numbering is contiguous 1-27 (paper Table 1 / HF dataset_order.csv)
    assert sorted(s.number_prefix for s in SPECS) == list(range(1, 28))
