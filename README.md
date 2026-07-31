# VI-Probe Generator

Procedural generator for **VI-Probe**, a controllable visual-illusion benchmark for probing
whether vision-language models respond based on visual perception or memorized priors.

- 📊 **Dataset:** [huggingface.co/datasets/xxsun/VI-Probe](https://huggingface.co/datasets/xxsun/VI-Probe) (CC-BY-4.0)
- 📄 **Paper:** *Do VLMs Perceive or Recall? Probing Visual Perception vs. Memory with Classic
  Visual Illusions*, CVPR 2026 (see [Citation](#citation))

Every image in VI-Probe is rendered procedurally by this code: 27 released illusion cases
across three categories (size, color, orientation — numbered 1–27 as in the paper), each in
six controlled variants — `original`, `perturbed`, matched `control`s, and `with_guide`
versions — over a grid of base scales and illusion strengths, with paired VQA prompts.

## Requirements

Python >= 3.9. No install step — clone and run from the repo root:

```bash
git clone https://github.com/marvinli00/VI-Probe
cd VI-Probe
pip install -r requirements.txt
```

Core rendering needs only `numpy`, `pillow`, `matplotlib`; sweeps additionally use
`pyyaml`, `pandas`, `openpyxl`. The two twisted-cord illusions call OpenCV for
super-resolution anti-aliasing (`pip install opencv-python-headless`).

## Usage

Everything runs through `main.py`:

```bash
python main.py --list                                  # all registered illusions
python main.py --illusion muller_lyer                  # all 6 variants x strength levels -> ./output
python main.py --illusion ponzo --variation perturbed --strength 1.2
python main.py --all -o output/renders                 # every illusion
```

`--variation` is one of `original`, `original_with_guide`, `original_control`, `perturbed`,
`perturbed_with_guide`, `perturbed_control`, or `all` (default). Or from Python:

```python
from illusions.registry import get_illusion

illusion = get_illusion("muller_lyer")()
illusion.set_variation(perturbed=True, visual_guide=True)
image = illusion.generate(strength=1.2, save=False)   # float32 RGB, (256, 512, 3), values in [0, 1]
```

Each illusion subclasses `IllusionTemplate` (`core/template.py`) and implements five hooks
(`define_elements`, `generate_illusion`, `add_visual_guides`,
`apply_control_modification`, `apply_perturbation`); the base class orchestrates the six
variants and strength sweeps. See [docs/adding_an_illusion.md](docs/adding_an_illusion.md)
to add your own. [examples/quickstart.ipynb](examples/quickstart.ipynb) walks through the
variants interactively.

## Sweeps

`--sweep` renders every (class × variant × base-scale × strength) combination described by a
sweep config and writes one `*_generation_metadata.xlsx` per class
(columns `class_name, type, base_scale, strength, image_path, prompt`):

```bash
python main.py --sweep configs/sweeps/size.yaml -o output/size_sweep
python main.py --sweep configs/sweeps/color.yaml -o output/color --classes ChubbIllusion --metadata-only
```

See [docs/sweep.md](docs/sweep.md) for the config format and the as-run parameter grids.

## Provenance

The exact as-run sweep parameters and VQA prompts of the published dataset are frozen
verbatim in `configs/sweeps/`; under the locked environment in `requirements-lock.txt`
(Python 3.11, numpy 1.24.4, Pillow 9.4.0) the sweeps regenerate the published images
byte-for-byte — verified by the golden tests in `tests/golden/` and spot-checked against
the PNGs hosted on HuggingFace. Sweep output folders use the released case numbering
(1–27). The downstream row selection (the 0.1-grid subset hosted on HuggingFace) and
reverse-prompt post-processing are not included here; see the dataset card.

> **Chubb caveat** — `ChubbIllusion` historically drew its noise texture from an unseeded
> RNG, so the published Chubb images are the one case that cannot be regenerated
> pixel-exactly. The class now accepts `seed=` for deterministic rendering going forward.

## Repository layout

```
main.py            # single entry point: --list | --illusion | --all | --sweep
sweep.py           # parameter-sweep engine behind --sweep
core/              # IllusionTemplate + drawing primitives (float32 RGB canvases)
illusions/         # one module per illusion; registry with released case IDs
└── length/  color/  orientation/
configs/sweeps/    # frozen as-run sweep configs (one YAML per category)
docs/              # guides, per-illusion notes, legacy name mapping
examples/          # quickstart notebook + gallery script
tests/             # golden-image equivalence + schema + sweep tests
```

Historical class names from the research code (e.g. the `CornswweetIllusion` typo, which
is baked into the released folder names and metadata) are preserved in the registry as
`legacy_*` fields so sweep output matches the published dataset exactly; see
[docs/name_mapping.md](docs/name_mapping.md) for the full research-name ↔ released-case
mapping.

## Tests

```bash
pip install -r requirements.txt pytest
pytest
```

The golden-image equivalence tests compare renders hash-for-hash against the published
generation run; they require the locked environment (`requirements-lock.txt`) and skip
elsewhere with an explanatory message.

## Citation

```bibtex
@inproceedings{sun2026vlms,
  title={Do VLMs Perceive or Recall? Probing Visual Perception vs. Memory with Classic Visual Illusions},
  author={Sun, Xiaoxiao and Li, Mingyang and Yuan, Kun and Sun, Min Woo and Endo, Mark and Wu, Shengguang and Li, Changlin and Zhang, Yuhui and Wang, Zeyu and Yeung-Levy, Serena},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={25861--25870},
  year={2026}
}
```

## License

Code: [MIT](LICENSE). The published VI-Probe dataset is distributed separately under
CC-BY-4.0 on HuggingFace.
