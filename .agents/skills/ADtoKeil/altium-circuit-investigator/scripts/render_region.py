#!/usr/bin/env python3
"""Render full or cropped SVG regions from an Altium .SchDoc.

Cropping is SVG viewBox based. It preserves the full drawing content but sets a
viewBox around a coordinate or the first endpoint of a target net.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def _load(path: Path):
    from altium_monkey import AltiumSchDoc
    from altium_monkey.altium_netlist_single_sheet import (
        AltiumNetlistSingleSheetCompiler,
    )

    sch = AltiumSchDoc(str(path))
    netlist = AltiumNetlistSingleSheetCompiler(sch).generate()
    return sch, {n.name.upper(): n for n in netlist.nets}


def _inject_viewbox(svg: str, x: int, y: int, width: int, height: int) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        tag = re.sub(r'\swidth="[^"]*"', f' width="{width}"', tag)
        tag = re.sub(r'\sheight="[^"]*"', f' height="{height}"', tag)
        if "viewBox=" in tag:
            tag = re.sub(r'\sviewBox="[^"]*"', f' viewBox="{x} {y} {width} {height}"', tag)
        else:
            tag = tag[:-1] + f' viewBox="{x} {y} {width} {height}">'
        return tag

    return re.sub(r"<svg\b[^>]*>", repl, svg, count=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schdoc", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--net")
    parser.add_argument("--x", type=int)
    parser.add_argument("--y", type=int)
    parser.add_argument("--margin", type=int, default=160)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    args = parser.parse_args()

    sch, nets = _load(args.schdoc)
    svg = sch.to_svg(project_parameters={})

    x = args.x
    y = args.y
    if args.net:
        net = nets.get(args.net.upper())
        if not net:
            raise SystemExit(f"No net named {args.net!r}")
        points = [getattr(ep, "connection_point", None) for ep in net.endpoints]
        points = [p for p in points if p]
        if not points:
            raise SystemExit(f"Net {args.net!r} has no endpoint coordinates")
        x, y = points[0]

    if x is not None and y is not None:
        width = args.width or args.margin * 2
        height = args.height or args.margin * 2
        svg = _inject_viewbox(svg, int(x - width / 2), int(y - height / 2), width, height)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(svg, encoding="utf-8")
    print(f"{args.out} {args.out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
