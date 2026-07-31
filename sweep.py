"""Parameter sweep: render every (class x variation x base_scale x strength)
combination described by a sweep config and write the generation metadata.

Faithful port of the original ``0_dataset_generation/generation*.ipynb``
notebooks; with a frozen config from ``configs/sweeps/`` it reproduces the
published metadata (folder names, file names, row order and prompts) exactly.
"""

import gc
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import yaml

from core.draw import hsb_to_rgb
from illusions.registry import resolve_class

#: Variation order used for the published dataset (perturbed sweep first,
#: then originals at strength 1.0).
PERTURBATION_VARIATIONS = [
    {"control": False, "perturbed": True, "original": False, "visual_guide": False},
    {"control": False, "perturbed": True, "original": False, "visual_guide": True},
    {"control": True, "perturbed": True, "original": False, "visual_guide": False},
]
ORG_VARIATIONS = [
    {"control": True, "perturbed": False, "original": True, "visual_guide": False},
    {"control": False, "perturbed": False, "original": True, "visual_guide": False},
    {"control": False, "perturbed": False, "original": True, "visual_guide": True},
]


def load_config(path) -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


def _linspace(spec: Dict[str, Any]) -> np.ndarray:
    values = np.linspace(spec["start"], spec["stop"], spec["num"], endpoint=spec.get("endpoint", True))
    for excluded in spec.get("exclude", []):
        values = values[values != excluded]
    return values


def _hue_shift(scale_factor: float) -> float:
    # Original notebook transform: x - 1 if x - 1 >= 0 else x
    return scale_factor - 1 if scale_factor - 1 >= 0 else scale_factor


def _ctor_kwargs(cfg: Dict[str, Any], class_key: str, scale_factor: float) -> Dict[str, Any]:
    """Constructor kwargs for one class at one base-scale, per param_mode."""
    mode = cfg["param_mode"]
    fixed = dict(cfg.get("ctor_params", {}).get(class_key, {}))

    if mode == "scaled":
        return {k: v * scale_factor for k, v in fixed.items()}

    if mode == "table":
        tables = cfg.get("table_ctor_params", {}).get(class_key, {})
        level = {k: table[f"{scale_factor:.2f}"] for k, table in tables.items()}
        return {**level, **fixed}

    if mode == "hsb_shift":
        hsb = cfg.get("hsb_ctor_params", {}).get(class_key, {})
        level = {}
        for key, value in hsb.items():
            shifted = list(value)
            shifted[0] = value[0] + _hue_shift(scale_factor)
            level[key] = hsb_to_rgb(shifted)
        return {**level, **fixed}

    raise ValueError(f"Unknown param_mode: {mode}")


def _question(cfg: Dict[str, Any], class_key: str, var: Dict[str, bool]) -> str:
    is_control = var["control"] and class_key in cfg.get("questions_control", {})
    if is_control:
        return cfg["questions_control"].get(class_key, "")
    return cfg.get("questions_non_control", {}).get(class_key, "")


def sweep_class(
    cfg: Dict[str, Any],
    class_key: str,
    output_prefix: Path,
    generate_images: bool = True,
) -> List[Dict[str, Any]]:
    """Sweep one illusion class; returns the metadata records."""
    cls = resolve_class(class_key)
    scale_factors = _linspace(cfg["scale_factors"])
    strengths = _linspace(cfg["strengths"])

    if "is_guide_first_by_class" in cfg:
        is_guide_first = cfg["is_guide_first_by_class"].get(class_key, True)
    else:
        is_guide_first = cfg.get("is_guide_first", False)

    records: List[Dict[str, Any]] = []
    for variations, strength_values in [
        (PERTURBATION_VARIATIONS, strengths),
        (ORG_VARIATIONS, [1.0]),
    ]:
        for var in variations:
            for scale_factor in scale_factors:
                kwargs = _ctor_kwargs(cfg, class_key, scale_factor)
                for strength in strength_values:
                    instance = cls(**kwargs)
                    instance.set_variation(**var)
                    folder = instance._get_variation_folder()

                    if len(strength_values) > 1:
                        rel = f"{folder}/base_scale_{scale_factor:.2f}_strength_{strength:.2f}.png"
                    else:
                        rel = f"{folder}/base_scale_{scale_factor:.2f}.png"

                    if generate_images:
                        save_path = output_prefix / rel
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        instance.generate(
                            strength=strength,
                            show=False,
                            save_path=save_path,
                            is_guide_first=is_guide_first,
                        )

                    records.append(
                        {
                            "class_name": class_key,
                            "type": folder,
                            "base_scale": f"{scale_factor:.2f}",
                            "strength": f"{strength:.2f}",
                            "image_path": rel,
                            "prompt": _question(cfg, class_key, var),
                        }
                    )
    return records


def run_sweep(
    config_path,
    output_dir,
    classes: Optional[List[str]] = None,
    generate_images: bool = True,
) -> None:
    """Run the sweep for every class in the config (or a subset).

    Writes images under ``output_dir/<N_ClassName>/<variation>/...`` and one
    ``<ClassName>_generation_metadata.xlsx`` per class, mirroring the layout
    of the published dataset.
    """
    import pandas as pd

    cfg = load_config(config_path)
    output_dir = Path(output_dir)

    for class_key in cfg["ctor_params"]:
        if classes and class_key not in classes:
            continue
        folder_name = cfg["output_folders"][class_key]
        prefix = output_dir / folder_name
        prefix.mkdir(parents=True, exist_ok=True)
        print(f"Sweeping {class_key} -> {prefix}")
        records = sweep_class(cfg, class_key, prefix, generate_images=generate_images)
        pd.DataFrame(records).to_excel(prefix / f"{class_key}_generation_metadata.xlsx", index=False)
        gc.collect()
