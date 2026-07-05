#!/usr/bin/env python3
"""Small helper for single-sheet Altium .SchDoc investigation.

Requires altium-monkey to be importable. It prints compact JSON for net
endpoints and can render a schematic SVG for local visual inspection.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path):
    from altium_monkey import AltiumSchDoc
    from altium_monkey.altium_netlist_single_sheet import (
        AltiumNetlistSingleSheetCompiler,
    )

    sch = AltiumSchDoc(str(path))
    netlist = AltiumNetlistSingleSheetCompiler(sch).generate()
    return sch, {n.name: n for n in netlist.nets}


def _endpoint_json(ep: Any) -> dict[str, Any]:
    return {
        "designator": getattr(ep, "designator", None),
        "pin": getattr(ep, "pin", None),
        "pin_name": getattr(ep, "pin_name", None),
        "pin_type": str(getattr(ep, "pin_type", "")),
        "connection_point": getattr(ep, "connection_point", None),
    }


def cmd_net(args: argparse.Namespace) -> None:
    _, nets = _load(args.schdoc)
    name_map = {k.upper(): k for k in nets}
    key = name_map.get(args.name.upper())
    if not key:
        raise SystemExit(f"No net named {args.name!r}")
    net = nets[key]
    print(
        json.dumps(
            {
                "name": net.name,
                "terminal_count": len(net.terminals),
                "endpoints": [_endpoint_json(ep) for ep in net.endpoints],
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


def cmd_find(args: argparse.Namespace) -> None:
    _, nets = _load(args.schdoc)
    needle = args.contains.upper()
    rows = []
    for name, net in sorted(nets.items()):
        if needle in name.upper():
            rows.append({"name": name, "terminal_count": len(net.terminals)})
    print(json.dumps({"count": len(rows), "nets": rows}, ensure_ascii=False, indent=2))


def cmd_render(args: argparse.Namespace) -> None:
    sch, _ = _load(args.schdoc)
    args.out.write_text(sch.to_svg(project_parameters={}), encoding="utf-8")
    print(json.dumps({"svg": str(args.out), "bytes": args.out.stat().st_size}))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("net")
    p.add_argument("schdoc", type=Path)
    p.add_argument("--name", required=True)
    p.set_defaults(func=cmd_net)

    p = sub.add_parser("find")
    p.add_argument("schdoc", type=Path)
    p.add_argument("--contains", required=True)
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("render")
    p.add_argument("schdoc", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_render)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
