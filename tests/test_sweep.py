"""Sweep round-trip: metadata schema and layout survive the write cycle."""

from pathlib import Path

import pandas as pd
import pytest

from sweep import load_config, run_sweep, sweep_class

CFG_ROOT = Path(__file__).resolve().parents[1] / "configs"


@pytest.fixture(scope="module")
def length_metadata(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("sweep")
    cfg = load_config(CFG_ROOT / "sweeps" / "size.yaml")
    records = sweep_class(cfg, "MullerLyerIllusion", tmp, generate_images=False)
    path = tmp / "MullerLyerIllusion_generation_metadata.xlsx"
    pd.DataFrame(records).to_excel(path, index=False)
    return str(path)


def test_xlsx_roundtrip_preserves_schema(length_metadata):
    df = pd.read_excel(length_metadata)
    assert list(df.columns) == ["class_name", "type", "base_scale", "strength", "image_path", "prompt"]
    # 3 perturbation variants x 51 scales x 50 strengths + 3 original variants x 51 scales
    assert len(df) == 3 * 51 * 50 + 3 * 51
    assert set(df["type"].unique()) == {
        "original", "original_with_guide", "original_control",
        "perturbed", "perturbed_with_guide", "perturbed_control",
    }


def test_run_sweep_writes_published_layout(tmp_path):
    run_sweep(CFG_ROOT / "sweeps" / "size.yaml", tmp_path,
              classes=["MullerLyerIllusion"], generate_images=False)
    expected = tmp_path / "1_MullerLyerIllusion" / "MullerLyerIllusion_generation_metadata.xlsx"
    assert expected.is_file()
