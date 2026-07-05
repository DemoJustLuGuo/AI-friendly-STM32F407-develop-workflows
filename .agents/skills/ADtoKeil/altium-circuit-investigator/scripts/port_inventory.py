#!/usr/bin/env python3
"""Inventory likely ports and firmware-relevant pins in Altium files.

The script intentionally errs on the side of inclusion. Treat results as a
checklist, then decide which items are external ports, board jumpers, or
internal MCU functions.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CONNECTOR_PREFIXES = ("CN", "J", "P", "AC", "N-", "L-", "PADDLE", "CON")
SUSPICIOUS_TOKENS = (
    "CTRL",
    "OUT",
    "IN",
    "AD",
    "ADC",
    "FG",
    "VSP",
    "PWM",
    "SW",
    "LEVEL",
    "PUMP",
    "COMP",
    "RELAY",
    "TX",
    "RX",
    "SCL",
    "SDA",
)

MCU_TEXT_TOKENS = ("MCU", "MICROCONTROLLER", "MICROCHIP", "单片机", "微控制器")
MCU_PIN_TOKENS = ("P0.", "P1.", "P2.", "P3.", "AIN", "PWM", "TK", "INT")


def _load_schdoc(path: Path):
    from altium_monkey import AltiumSchDoc
    from altium_monkey.altium_netlist_single_sheet import (
        AltiumNetlistSingleSheetCompiler,
    )

    sch = AltiumSchDoc(str(path))
    netlist = AltiumNetlistSingleSheetCompiler(sch).generate()
    return sch, netlist


def _component_parameters(component: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for parameter in getattr(component, "parameters", []) or []:
        name = getattr(parameter, "name", None)
        text = getattr(parameter, "text", None)
        if name and text not in (None, ""):
            out[str(name)] = str(text)
    return out


def _fix_mojibake(text: str | None) -> str | None:
    if not text:
        return text
    for enc in ("latin1", "cp1252"):
        try:
            return text.encode(enc).decode("gbk")
        except Exception:
            pass
    return text


def _endpoint_json(ep: Any, net_name: str) -> dict[str, Any]:
    return {
        "designator": getattr(ep, "designator", None),
        "pin": getattr(ep, "pin", None),
        "pin_name": getattr(ep, "pin_name", None),
        "net": net_name,
        "connection_point": getattr(ep, "connection_point", None),
    }


def _dedupe_endpoints(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = (
            str(row.get("designator") or ""),
            str(row.get("pin") or ""),
            str(row.get("pin_name") or ""),
            str(row.get("net") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _symbol_pin_rows(component: Any, endpoint_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return all symbol pins, annotated with netlist data when connected.

    Netlists omit unconnected pins. For MCU and connector coverage, those pins
    must still appear in reports as NC / needs review.
    """

    by_pin: dict[str, dict[str, Any]] = {}
    for row in _dedupe_endpoints(endpoint_rows):
        pin = str(row.get("pin") or "")
        if pin and pin not in by_pin:
            by_pin[pin] = row

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for pin in getattr(component, "pins", []) or []:
        number = str(getattr(pin, "designator", "") or "")
        if not number:
            continue
        connected = by_pin.get(number, {})
        out.append(
            {
                "designator": connected.get("designator"),
                "pin": number,
                "pin_name": connected.get("pin_name") or getattr(pin, "name", None),
                "net": connected.get("net"),
                "connection_point": connected.get("connection_point")
                or getattr(pin, "connection_point", None),
                "is_connected": bool(connected.get("net")),
            }
        )
        seen.add(number)

    for number, row in by_pin.items():
        if number not in seen:
            row = dict(row)
            row["is_connected"] = bool(row.get("net"))
            out.append(row)

    return _dedupe_endpoints(out)


def _looks_like_mcu(designator: str, comment: str, spec: str, pins: list[dict[str, Any]]) -> bool:
    text = f"{designator} {comment} {spec}".upper()
    if designator.upper() == "MCU" or any(token in text for token in MCU_TEXT_TOKENS):
        return True
    if len(pins) < 16:
        return False
    mux_hits = 0
    for pin in pins:
        pin_name = str(pin.get("pin_name") or "").upper()
        if any(token in pin_name for token in MCU_PIN_TOKENS):
            mux_hits += 1
    return mux_hits >= 8


def schematic_inventory(schdoc: Path) -> dict[str, Any]:
    sch, netlist = _load_schdoc(schdoc)
    comp_nets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for net in netlist.nets:
        for ep in net.endpoints:
            comp_nets[ep.designator].append(_endpoint_json(ep, net.name))

    connectors = []
    mcu_like = []
    for component in sch.components:
        params = _component_parameters(component)
        designator = params.get("Designator") or getattr(component, "designator", None)
        if not designator:
            continue
        comment = params.get("Comment") or params.get("Value") or ""
        spec = params.get("spec") or params.get("ITEMDESC") or ""
        row = {
            "designator": designator,
            "comment": _fix_mojibake(comment),
            "spec": _fix_mojibake(spec),
            "pins": sorted(
                _symbol_pin_rows(component, comp_nets.get(designator, [])),
                key=lambda r: (str(r["pin"]).zfill(8), str(r["pin"])),
            ),
        }
        if designator.upper().startswith(CONNECTOR_PREFIXES):
            connectors.append(row)
        if _looks_like_mcu(designator, str(comment), str(spec), row["pins"]):
            mcu_like.append(row)

    suspicious_nets = []
    for net in netlist.nets:
        name = net.name or ""
        upper = name.upper()
        if any(token in upper for token in SUSPICIOUS_TOKENS):
            suspicious_nets.append(
                {
                    "name": name,
                    "terminal_count": len(net.terminals),
                    "endpoints": _dedupe_endpoints([_endpoint_json(ep, name) for ep in net.endpoints]),
                }
            )

    local_labels = []
    for attr in ("labels", "net_labels", "text_frames"):
        for obj in getattr(sch, attr):
            text = getattr(obj, "text", None)
            if not text:
                continue
            loc = getattr(obj, "location", None)
            local_labels.append(
                {
                    "kind": attr,
                    "text": _fix_mojibake(text),
                    "x": getattr(loc, "x", None),
                    "y": getattr(loc, "y", None),
                }
            )

    return {
        "schdoc": str(schdoc),
        "connectors": sorted(connectors, key=lambda r: r["designator"]),
        "mcu_like": mcu_like,
        "suspicious_nets": sorted(suspicious_nets, key=lambda r: r["name"]),
        "local_labels": sorted(local_labels, key=lambda r: (r["y"] or 0, r["x"] or 0)),
    }


def pcb_inventory(pcbdoc: Path) -> dict[str, Any]:
    from altium_monkey import AltiumPcbDoc

    pcb = AltiumPcbDoc.from_file(pcbdoc)
    net_names = [n.name for n in pcb.nets]
    comp_by_idx = {i: c for i, c in enumerate(pcb.components)}
    pads_by_comp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pad in pcb.pads:
        component = comp_by_idx.get(pad.component_index)
        if not component:
            continue
        idx = pad.net_index
        net = net_names[idx] if isinstance(idx, int) and 0 <= idx < len(net_names) else None
        pads_by_comp[component.designator].append(
            {
                "pad": pad.designator,
                "net": net,
                "layer": str(getattr(pad, "layer", "")),
            }
        )

    ports = []
    for component in pcb.components:
        designator = component.designator or ""
        footprint = component.footprint or ""
        pads = pads_by_comp.get(designator, [])
        looks_like_port = (
            designator.upper().startswith(CONNECTOR_PREFIXES)
            or footprint.startswith(("315009", "315010", "SIP"))
            or "CON" in footprint.upper()
        )
        if looks_like_port:
            ports.append(
                {
                    "designator": designator,
                    "footprint": footprint,
                    "layer": component.layer,
                    "x_mils": component.get_x_mils(),
                    "y_mils": component.get_y_mils(),
                    "pads": sorted(pads, key=lambda r: str(r["pad"])),
                }
            )
    return {"pcbdoc": str(pcbdoc), "pcb_ports": sorted(ports, key=lambda r: r["designator"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schdoc", type=Path, required=True)
    parser.add_argument("--pcbdoc", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    payload = schematic_inventory(args.schdoc)
    if args.pcbdoc:
        payload.update(pcb_inventory(args.pcbdoc))

    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
