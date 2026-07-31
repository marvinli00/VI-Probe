# Legacy name mapping

The research tree that produced VI-Probe used numbered folders and a few historical
names/typos. The **released dataset** (paper Table 1, HuggingFace) contains **27 cases
renumbered contiguously 1–27**; the code here uses corrected, importable names and
preserves the published class names as `legacy_*` fields in `illusions/registry.py`.
Sweeps driven by the frozen configs in `configs/sweeps/` emit the released folder names.

Columns: released case id (as on HuggingFace) · research-era number (folder prefixes in
the original research tree and its intermediate outputs) · source file · module · class.

## Size (released cases 1–11, `size.yaml`)

| Case | Research # | Original folder | Module | Class |
|---|---|---|---|---|
| 1 | 1 | `1_1_muller_lyer/generate.py` | `length/muller_lyer.py` | `MullerLyerIllusion` |
| 2 | 2 | `1_2_Circle_Muller-Lyer/generate.py` | `length/circle_muller_lyer.py` | `CircleMullerLyerIllusion` |
| 3 | 3 | `1_3_Ponzo/generate_classical.py` | `length/ponzo.py` | `PonzoIllusion` |
| 4 | 4 | `1_3_Ponzo/generate_trapezoid.py` | `length/ponzo_trapezoid.py` | `PonzoTrapezoidIllusion` |
| 5 | 6 | `1_5_Ebbinghaus/generate.py` | `length/ebbinghaus.py` | `EbbinghausIllusion` |
| 6 | 7 | `1_5_Ebbinghaus/generate_rectangular.py` | `length/ebbinghaus_rectangular.py` | `EbbinghausIllusionRectangular` |
| 7 | 8 | `1_6_delboeuf/generate.py` | `length/delboeuf.py` | `DelboeufIllusion` |
| 8 | 9 | `1_8_oppel_kundt/generate.py` | `length/oppel_kundt.py` | `OppelKundtIllusion` |
| 9 | 10 | `1_9_irradiation/generate.py` | `length/irradiation.py` | `IrradiationIllusion` |
| 10 | 11 | `1_10_irradiation_pentagon/generate.py` | `length/irradiation_pentagon.py` | `IrradiationPentagonIllusion` |
| 11 | 12 | `1_11_circle_ponzo/generate.py` | `length/circle_ponzo.py` | `CirclePonzoIllusion` |

## Color (released cases 12–18, `color.yaml`)

| Case | Research # | Original folder | Module | Class (legacy name) |
|---|---|---|---|---|
| 12 | 13 | `2_1_Cornsweet illusion/case2/` | `color/cornsweet.py` | `CornsweetIllusion` (published as `CornswweetIllusion`) |
| 13 | 14 | `2_2_Simultaneous contrast/case1/` | `color/simultaneous_contrast.py` | `SimultaneousContrastIllusion` |
| 14 | 15 | `2_3_munker-white/case1/` | `color/munker_white.py` | `MunkerWhiteIllusion` |
| 15 | 16 | `2_4_mach_band/` | `color/mach_band.py` | `MachBandIllusion` |
| 16 | 17 | `2_5_mach_band/` | `color/mach_band_case2.py` | `MachBandIllusionCase2` (published as `MachBandIllusion_Case2`) |
| 17 | 18 | `2_6_chubb/` | `color/chubb.py` | `ChubbIllusion` (+ new optional `seed` param) |
| 18 | 19 | `2_1_Cornsweet illusion/case1/` | `color/cornsweet_case1.py` | `CornsweetIllusionCase1` (published as `CornswweetIllusionCase1`) |

The released color images come from `color.yaml` (verified byte-exact against the
HuggingFace PNGs).

## Orientation (released cases 19–27, `orientation.yaml`)

| Case | Research # | Original folder | Module | Class |
|---|---|---|---|---|
| 19 | 19 | `3_1_hering_illusion/` | `orientation/hering.py` | `HeringIllusion` |
| 20 | 20 | `3_1_hering_illusion_v/` | `orientation/hering_vertical.py` | `HeringIllusionVertical` |
| 21 | 21 | `3_3_zollner_illusion/` | `orientation/zollner.py` | `ZollnerIllusion` |
| 22 | 22 | `3_3_zollner_illusion_v/` | `orientation/zollner_vertical.py` | `ZollnerIllusionVertical` |
| 23 | 25 | `3_6_twisted_cord_illusion/` | `orientation/twisted_cord.py` | `TwistedCordIllusion` |
| 24 | 26 | `3_6_twisted_cord_illusion_light/` | `orientation/twisted_cord_light.py` | `TwistedCordIllusionLight` |
| 25 | 27 | `3_5_poggendorff/` | `orientation/poggendorff.py` | `PoggendorffIllusion` |
| 26 | 28 | `3_5_poggendorff_1/` | `orientation/poggendorff_horizontal.py` | `PoggendorffHorizontalIllusion` |
| 27 | 29 | `3_7_ehrenstein_illusion/` | `orientation/ehrenstein.py` | `EhrensteinIllusion` |

## Historical quirks (preserved on purpose)

- **`Cornswweet` typo** — the released folder/metadata names spell Cornsweet with a double
  `w`; the registry's `legacy_class_name` keeps that spelling so sweep output matches.
- **Release renumbering** — the research tree numbered cases 1–29 with number 19 reused
  (Cornsweet Case1 and Hering) and 23–24 skipped; the release renumbered the 27 shipped
  cases contiguously (see the Research # column above). A `VerticalHorizontalIllusion`
  (research case 5) existed in the research tree but was dropped at release time and is
  not included in this repository.
- **Category naming** — the research tree called the size category "length"; the released
  dataset and this repo's registry use "size" (the modules stay under `illusions/length/`,
  their historical home).
- The original per-illusion `generate.ipynb` notebooks were pre-refactor prototypes and were
  not migrated; the `.py` classes are the source of truth (verified pixel-identical against
  golden renders in `tests/golden/` and against the HuggingFace-hosted PNGs).
