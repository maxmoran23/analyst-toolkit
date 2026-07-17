#!/usr/bin/env python3
"""Create a deterministic RGB contact sheet from rendered slide PNG files."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--columns", type=int, default=3)
    args = parser.parse_args()
    source = Path(args.input_dir)
    paths = sorted(source.glob("slide-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    if not paths:
        raise SystemExit("no slide PNGs found")
    thumb_w, thumb_h = 480, 360
    label_h, gap = 28, 20
    cols = max(1, args.columns)
    rows = (len(paths) + cols - 1) // cols
    canvas = Image.new("RGB", (
        gap + cols * (thumb_w + gap),
        gap + rows * (thumb_h + label_h + gap),
    ), "white")
    draw = ImageDraw.Draw(canvas)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        col, row = index % cols, index // cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)
        canvas.paste(image, (x, y))
        draw.text((x, y + thumb_h + 5), f"Slide {index + 1}", fill="#10243E")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    print(f"created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
