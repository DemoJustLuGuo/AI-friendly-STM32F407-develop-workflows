#!/usr/bin/env python3
"""Trace an Altium .SchDoc net through small topology components for a few hops."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


TRAVERSABLE_PREFIXES = (
    "R",
    "C",
    "L",
    "FB",
    "D",
    "ZD",
    "TVS",
    "Q",
    "T",
    "U",
    "IC",
    "PC",
    "OP",
    "RY",
    "K",
    "CN",
    "J",
    "P",
)

STOP_PREFIXES = ("MCU", "CPU")


def _component_parameters(component: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for parameter in getattr(component, "parameters", []) or []:
        name = getattr(parameter, "name", None)
        text = getattr(parameter, "text", None)
        if name and text not in (None, ""):
            out[str(name)] = str(text)
    return out


def _comp_kind(designator: str, component: Any | None) -> str:
    text = " ".join(
        str(x or "")
        for x in (
            designator,
            getattr(component, "comment", ""),
            getattr(component, "description", ""),
            _component_parameters(component).get("Comment", ""),
            _component_parameters(component).get("Description", ""),
            _component_parameters(component).get("SPEC", ""),
        )
    ).upper()
    if designator.upper().startswith(STOP_PREFIXES):
        return "stop-processor"
    if any(word in text for word in ("MCU", "MICRO", "CPU", "单片机", "处理器")):
        return "stop-processor"
    if any(word in text for word in ("EEPROM", "FLASH", "LDO", "REGULATOR", "稳压", "电源芯片")):
        return "stop-ic"
    if any(word in text for word in ("OPTO", "光耦", "PHOTOCOUPLER")):
        return "opto"
    if any(word in text for word in ("RELAY", "继电器")):
        return "relay"
    return "small-topology"


def _can_traverse(designator: str, component: Any | None, mode: str) -> tuple[bool, str]:
    if mode == "all":
        return True, "mode=all"
    upper = designator.upper()
    kind = _comp_kind(designator, component)
    if kind.startswith("stop"):
        return False, kind
    if upper.startswith(TRAVERSABLE_PREFIXES):
        return True, kind
    return False, "unknown-designator"


def _load(path: Path):
    from altium_monkey import AltiumSchDoc
    from altium_monkey.altium_netlist_single_sheet import (
        AltiumNetlistSingleSheetCompiler,
    )

    sch = AltiumSchDoc(str(path))
    netlist = AltiumNetlistSingleSheetCompiler(sch).generate()
    return sch, netlist


def _ep(ep: Any) -> dict[str, Any]:
    return {
        "designator": getattr(ep, "designator", None),
        "pin": getattr(ep, "pin", None),
        "pin_name": getattr(ep, "pin_name", None),
        "connection_point": getattr(ep, "connection_point", None),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schdoc", type=Path)
    parser.add_argument("--net", required=True)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--max-nets", type=int, default=80)
    parser.add_argument(
        "--traverse-mode",
        choices=("small-signal", "all"),
        default="small-signal",
        help="small-signal avoids crossing MCU/large IC internals; all reproduces raw component-neighbor BFS.",
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    sch, netlist = _load(args.schdoc)
    nets = {n.name: n for n in netlist.nets}
    upper_to_name = {name.upper(): name for name in nets}
    start = upper_to_name.get(args.net.upper())
    if not start:
        raise SystemExit(f"No net named {args.net!r}")

    comp_to_nets: dict[str, set[str]] = defaultdict(set)
    for net in netlist.nets:
        for ep in net.endpoints:
            comp_to_nets[ep.designator].add(net.name)
    components = {
        getattr(component, "designator", ""): component
        for component in getattr(sch, "components", [])
    }

    seen_nets = {start}
    queue = deque([(start, 0)])
    rows = []
    edges = []
    while queue and len(seen_nets) <= args.max_nets:
        net_name, depth = queue.popleft()
        net = nets[net_name]
        endpoints = [_ep(ep) for ep in net.endpoints]
        rows.append({"depth": depth, "net": net_name, "endpoints": endpoints})
        if depth >= args.depth:
            continue
        for ep in net.endpoints:
            can_traverse, reason = _can_traverse(
                ep.designator, components.get(ep.designator), args.traverse_mode
            )
            edges.append(
                {
                    "from_net": net_name,
                    "through": ep.designator,
                    "allowed": can_traverse,
                    "reason": reason,
                }
            )
            if not can_traverse:
                continue
            for next_net in sorted(comp_to_nets.get(ep.designator, [])):
                if next_net not in seen_nets:
                    seen_nets.add(next_net)
                    queue.append((next_net, depth + 1))

    payload = {
        "schdoc": str(args.schdoc),
        "start_net": start,
        "depth": args.depth,
        "traverse_mode": args.traverse_mode,
        "trace": rows,
        "edges": edges,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
