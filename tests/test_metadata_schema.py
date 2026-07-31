"""The sweep produces the published metadata schema and naming conventions."""

import re
from pathlib import Path

from sweep import load_config, sweep_class

CFG_ROOT = Path(__file__).resolve().parents[1] / "configs"

EXPECTED_COLUMNS = ["class_name", "type", "base_scale", "strength", "image_path", "prompt"]
EXPECTED_TYPES = {
    "original",
    "original_with_guide",
    "original_control",
    "perturbed",
    "perturbed_with_guide",
    "perturbed_control",
}
PATH_RE = re.compile(r"^[a-z_]+/base_scale_\d\.\d{2}(_strength_\d\.\d{2})?\.png$")


def _records(config_name, class_key, tmp_path):
    cfg = load_config(str(CFG_ROOT / "sweeps" / config_name))
    return cfg, sweep_class(cfg, class_key, tmp_path, generate_images=False)


def test_size_schema(tmp_path):
    cfg, records = _records("size.yaml", "MullerLyerIllusion", tmp_path)
    assert list(records[0].keys()) == EXPECTED_COLUMNS
    assert {r["type"] for r in records} == EXPECTED_TYPES
    assert all(PATH_RE.match(r["image_path"]) for r in records)
    # 3 perturbation variants x 51 scales x 50 strengths + 3 original variants x 51 scales
    assert len(records) == 3 * 51 * 50 + 3 * 51
    assert all(r["class_name"] == "MullerLyerIllusion" for r in records)


def test_orientation_schema(tmp_path):
    cfg, records = _records("orientation.yaml", "HeringIllusion", tmp_path)
    assert len(records) == 3 * 11 * 10 + 3 * 11
    assert {r["type"] for r in records} == EXPECTED_TYPES


def test_color_schema(tmp_path):
    cfg, records = _records("color.yaml", "ChubbIllusion", tmp_path)
    # color sweeps use 50 scale factors (endpoint excluded)
    assert len(records) == 3 * 50 * 50 + 3 * 50


def test_legacy_class_names_in_configs():
    """Frozen configs key classes by their published (legacy) names."""
    cfg = load_config(str(CFG_ROOT / "sweeps" / "color.yaml"))
    assert "CornswweetIllusion" in cfg["ctor_params"]  # historical typo, kept on purpose
    assert cfg["output_folders"]["CornswweetIllusion"] == "12_CornswweetIllusion"
