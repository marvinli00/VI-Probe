"""Render a one-image gallery of every registered illusion.

Usage: python examples/gallery.py [output_dir]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.image_io import save_image
from illusions.registry import all_specs


def main(output_dir: str = "gallery") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for spec in all_specs():
        try:
            instance = spec.load()()
        except ImportError as e:  # OpenCV-backed illusions without cv2 installed
            print(f"{spec.name:<24} skipped ({e})")
            continue
        instance.set_variation(original=True)
        image = instance.generate(strength=1.0, save=False, show=False)
        save_image(image, out / f"{spec.name}.png")
        print(f"{spec.name:<24} -> {out / spec.name}.png")


if __name__ == "__main__":
    main(*sys.argv[1:2])
