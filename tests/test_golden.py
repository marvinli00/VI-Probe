"""Golden-image equivalence: renders must match the pre-refactor hashes.

The hashes in ``golden/hashes.json`` were generated from the original research
code under the locked environment (see requirements-lock.txt). The raw float32
array hash is independent of the PNG encoder; the PNG hash additionally pins
the Pillow version. In a different environment, minor libc/BLAS differences
could in principle change pixels — if only PNG hashes fail, check Pillow first.
"""

import hashlib
import io
import json
import os
from pathlib import Path

import numpy as np
import PIL.Image
import pytest

from illusions.registry import get_spec

GOLDEN_PATH = Path(__file__).parent / "golden" / "hashes.json"
GOLDEN = json.loads(GOLDEN_PATH.read_text())
GOLDEN_SEED = GOLDEN["env"]["golden_seed"]

# Bit-exact hashes are only guaranteed under the locked environment
# (requirements-lock.txt). Elsewhere the comparison is skipped unless
# VIPROBE_GOLDEN_STRICT=1 forces it.
_env_diffs = [
    f"{name} {have} != golden {want}"
    for name, have, want in [
        ("numpy", np.__version__, GOLDEN["env"]["numpy"]),
        ("Pillow", PIL.__version__, GOLDEN["env"]["pillow"]),
    ]
    if have != want
]
if _env_diffs and not os.environ.get("VIPROBE_GOLDEN_STRICT"):
    pytestmark = pytest.mark.skip(
        reason="golden hashes require the locked environment (requirements-lock.txt): "
        + "; ".join(_env_diffs)
    )

# original source file -> registry key (files not listed were not shipped)
FILE_TO_KEY = {
    "1_1_muller_lyer/generate.py": "muller_lyer",
    "1_2_Circle_Muller-Lyer/generate.py": "circle_muller_lyer",
    "1_3_Ponzo/generate_classical.py": "ponzo",
    "1_3_Ponzo/generate_trapezoid.py": "ponzo_trapezoid",
    "1_5_Ebbinghaus/generate.py": "ebbinghaus",
    "1_5_Ebbinghaus/generate_rectangular.py": "ebbinghaus_rectangular",
    "1_6_delboeuf/generate.py": "delboeuf",
    "1_8_oppel_kundt/generate.py": "oppel_kundt",
    "1_9_irradiation/generate.py": "irradiation",
    "1_10_irradiation_pentagon/generate.py": "irradiation_pentagon",
    "1_11_circle_ponzo/generate.py": "circle_ponzo",
    "2_1_Cornsweet illusion/case2/generate.py": "cornsweet",
    "2_1_Cornsweet illusion/case1/generate.py": "cornsweet_case1",
    "2_2_Simultaneous contrast/case1/generate.py": "simultaneous_contrast",
    "2_3_munker-white/case1/generate.py": "munker_white",
    "2_4_mach_band/generate.py": "mach_band",
    "2_5_mach_band/generate.py": "mach_band_case2",
    "2_6_chubb/generate.py": "chubb",
    "3_1_hering_illusion/generate.py": "hering",
    "3_1_hering_illusion_v/generate.py": "hering_vertical",
    "3_3_zollner_illusion/generate.py": "zollner",
    "3_3_zollner_illusion_v/generate.py": "zollner_vertical",
    "3_5_poggendorff/generate.py": "poggendorff",
    "3_5_poggendorff_1/generate.py": "poggendorff_horizontal",
    "3_6_twisted_cord_illusion/generate.py": "twisted_cord",
    "3_6_twisted_cord_illusion_light/generate.py": "twisted_cord_light",
    "3_7_ehrenstein_illusion/generate.py": "ehrenstein",
}

VAR_KWARGS = {
    "original": dict(control=False, perturbed=False, original=True, visual_guide=False),
    "original_with_guide": dict(control=False, perturbed=False, original=True, visual_guide=True),
    "original_control": dict(control=True, perturbed=False, original=True, visual_guide=False),
    "perturbed": dict(control=False, perturbed=True, original=False, visual_guide=False),
    "perturbed_with_guide": dict(control=False, perturbed=True, original=False, visual_guide=True),
    "perturbed_control": dict(control=True, perturbed=True, original=False, visual_guide=False),
}

RECORDS = [r for r in GOLDEN["records"] if r["file"] in FILE_TO_KEY]

_BY_GROUP = {}
for r in RECORDS:
    _BY_GROUP.setdefault((FILE_TO_KEY[r["file"]], r.get("ctor_tag", "")), []).append(r)


@pytest.mark.parametrize(
    "group", sorted(_BY_GROUP), ids=[f"{k}{('-' + t) if t else ''}" for k, t in sorted(_BY_GROUP)]
)
def test_golden_equivalence(group):
    key, _tag = group
    records = _BY_GROUP[group]
    instance = get_spec(key).load()(**records[0].get("ctor_kwargs", {}))

    mismatches = []
    for r in records:
        instance.set_variation(**VAR_KWARGS[r["variation"]])
        np.random.seed(GOLDEN_SEED)
        image = np.asarray(instance.generate(strength=r["strength"], save=False, show=False))
        array_hash = hashlib.sha256(np.ascontiguousarray(image).tobytes()).hexdigest()

        buffer = io.BytesIO()
        PIL.Image.fromarray((image * 255).astype(np.uint8)).save(buffer, format="PNG")
        png_hash = hashlib.sha256(buffer.getvalue()).hexdigest()

        if array_hash != r["array_sha256"] or png_hash != r["png_sha256"]:
            mismatches.append(f"{r['variation']}/strength={r['strength']}")

    assert not mismatches, f"{key}: renders differ from golden for {mismatches}"


def test_chubb_seed_is_deterministic():
    cls = get_spec("chubb").load()
    instance = cls(seed=0)
    instance.set_variation(perturbed=True)
    a = instance.generate(strength=1.2, save=False, show=False)
    b = instance.generate(strength=1.2, save=False, show=False)
    assert np.array_equal(a, b)
