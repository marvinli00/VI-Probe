#!/usr/bin/env python3
"""VI-Probe illusion generator.

Usage:
  python main.py --list
  python main.py --illusion muller_lyer                     # all 6 variants x default strengths -> ./output
  python main.py --illusion ponzo --variation perturbed --strength 1.2
  python main.py --all -o output/renders
  python main.py --sweep configs/sweeps/size.yaml -o output/size_sweep
"""

import argparse
from pathlib import Path

#: The six published variants -> IllusionTemplate.set_variation kwargs.
VARIATIONS = {
    "original": dict(control=False, perturbed=False, original=True, visual_guide=False),
    "original_with_guide": dict(control=False, perturbed=False, original=True, visual_guide=True),
    "original_control": dict(control=True, perturbed=False, original=True, visual_guide=False),
    "perturbed": dict(control=False, perturbed=True, original=False, visual_guide=False),
    "perturbed_with_guide": dict(control=False, perturbed=True, original=False, visual_guide=True),
    "perturbed_control": dict(control=True, perturbed=True, original=False, visual_guide=False),
}


def list_illusions():
    from illusions.registry import all_specs

    fmt = "{:<24} {:<32} {:<12} {:>6}"
    print(fmt.format("NAME", "CLASS", "CATEGORY", "CASE"))
    for spec in all_specs():
        print(fmt.format(spec.name, spec.class_name, "/".join(spec.categories), spec.number_prefix))


def render(spec, variation, strength, strength_min, output):
    instance = spec.load()()
    if output:
        instance.set_output_dir(output)
    if variation == "all":
        if strength is not None:
            instance.generate_all_variations(strength=strength)
        else:
            instance.generate_all(strength_min=strength_min)
    else:
        instance.set_variation(**VARIATIONS[variation])
        instance.generate(strength=1.0 if strength is None else strength, save=True)
    print(f"Images written under {instance.output_dir}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="List registered illusions")
    mode.add_argument("--illusion", metavar="NAME",
                      help="Render one illusion (registry, class, or legacy class name)")
    mode.add_argument("--all", action="store_true", dest="all_illusions",
                      help="Render every registered illusion")
    mode.add_argument("--sweep", metavar="CONFIG", type=Path,
                      help="Run a sweep config from configs/sweeps/")
    parser.add_argument("--variation", choices=[*VARIATIONS, "all"], default="all",
                        help="Which variant to render (default: all six)")
    parser.add_argument("--strength", type=float, default=None,
                        help="Single strength (default: 1.0, or every level with --variation all)")
    parser.add_argument("--strength-min", type=float, default=-1.0,
                        help="With --variation all: only render strengths >= this")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output directory (default ./output; required with --sweep)")
    parser.add_argument("--classes", nargs="*",
                        help="With --sweep: subset of class names from the config")
    parser.add_argument("--metadata-only", action="store_true",
                        help="With --sweep: write metadata xlsx only, skip image rendering")
    args = parser.parse_args(argv)

    if args.list:
        list_illusions()
    elif args.sweep:
        if args.output is None:
            parser.error("--sweep requires -o/--output")
        from sweep import run_sweep

        run_sweep(args.sweep, args.output, classes=args.classes or None,
                  generate_images=not args.metadata_only)
    else:
        from illusions.registry import all_specs, get_spec

        specs = all_specs() if args.all_illusions else [get_spec(args.illusion)]
        for spec in specs:
            render(spec, args.variation, args.strength, args.strength_min, args.output)


if __name__ == "__main__":
    main()
