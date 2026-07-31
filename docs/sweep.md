# Parameter sweeps

`python main.py --sweep <config> -o <dir>` renders every
(class × variant × base-scale × strength) combination described by a sweep config:

```
IllusionTemplate subclasses (illusions/)
        │  python main.py --sweep configs/sweeps/size.yaml -o <dir>
        ▼
<dir>/<N_ClassName>/{original,original_with_guide,original_control,
                     perturbed,perturbed_with_guide,perturbed_control}/
        base_scale_X.XX[_strength_Y.YY].png
<dir>/<N_ClassName>/<ClassName>_generation_metadata.xlsx
```

Use `--classes` to sweep a subset and `--metadata-only` to skip image rendering.

## Config format

A sweep config (see `configs/sweeps/`) declares, per category:

| Key | Meaning |
|---|---|
| `param_mode` | how constructor params vary with base scale: `scaled` (multiply), `table` (per-scale lookup), `hsb_shift` (HSB hue shifted by scale, converted to RGB) |
| `scale_factors` / `strengths` | `np.linspace` specs; strength 1.0 is excluded from the perturbed sweep |
| `ctor_params` | fixed constructor params per class (keyed by **legacy** class name) |
| `output_folders` | class -> published folder name (`1_MullerLyerIllusion`, ...) |
| `questions_non_control` / `questions_control` | VQA prompt per class, verbatim as published |

Perturbed variants sweep all (scale, strength) pairs; original variants render at
strength 1.0 only. Metadata columns: `class_name, type, base_scale, strength, image_path, prompt`.

## As-run grids (validated against the published files)

| Config | Released cases | Scales | Strengths |
|---|---|---|---|
| `size.yaml` | 1–11 | 51 (0.5–1.5) | 51 minus 1.0 |
| `color.yaml` | 12–18 | 50 (endpoint excluded) | 51 minus 1.0 |
| `orientation.yaml` | 19–27 | 11 | 11 minus 1.0 |

## Provenance

These configs are the exact as-run parameters of the published dataset, frozen verbatim
(including historical quirks such as the `CornswweetIllusion` legacy class name), with
output folders renumbered to the released case ids 1–27. Under the locked environment in
`requirements-lock.txt` a sweep regenerates the published images byte-for-byte (verified
by `tests/golden/` and spot-checked against the HuggingFace-hosted PNGs, with the
Chubb-RNG exception noted in the README). The released dataset hosts the 0.1-grid subset
of each sweep; that row selection and the reverse-prompt post-processing are not part of
this repository — see the dataset card on HuggingFace.
