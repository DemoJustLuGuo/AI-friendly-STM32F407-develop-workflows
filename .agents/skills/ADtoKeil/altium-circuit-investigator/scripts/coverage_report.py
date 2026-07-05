#!/usr/bin/env python3
"""Summarize port-inventory completeness for firmware-oriented reviews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


POWER_TOKENS = ("GND", "VDD", "VCC", "+", "-5V", "5V", "3V", "15V", "12V")
BOOT_TOKENS = ("RST", "RESET", "CLK", "SWD", "DEBUG", "TX", "RX")
FUNCTION_TOKENS = (
    "AD",
    "ADC",
    "AIN",
    "FG",
    "VSP",
    "PWM",
    "SW",
    "PUMP",
    "COMP",
    "RELAY",
    "KEY",
    "NTC",
    "TEMP",
    "LEVEL",
    "SCL",
    "SDA",
    "TX",
    "RX",
)


def _pins(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        designator = str(row.get("designator") or "")
        for pin in row.get("pins") or []:
            key = (designator, str(pin.get("pin") or ""))
            if key in seen:
                continue
            seen.add(key)
            out.append(pin)
    return out


def _classify_pin(pin: dict[str, Any]) -> str:
    net = str(pin.get("net") or "").upper()
    pin_name = str(pin.get("pin_name") or "").upper()
    text = f"{net} {pin_name}"
    if not net:
        return "nc_or_unconnected"
    if any(token in net for token in POWER_TOKENS):
        return "power"
    if any(token in text for token in BOOT_TOKENS):
        return "debug_or_boot"
    if any(token in text for token in FUNCTION_TOKENS):
        return "firmware_relevant"
    return "needs_review"


def build_report(inventory: dict[str, Any]) -> dict[str, Any]:
    mcu_pins = _pins(inventory.get("mcu_like") or [])
    classes: dict[str, int] = {}
    pin_rows = []
    for pin in mcu_pins:
        cls = _classify_pin(pin)
        classes[cls] = classes.get(cls, 0) + 1
        pin_rows.append({**pin, "coverage_class": cls})

    connectors = inventory.get("connectors") or []
    connector_pin_count = sum(len(c.get("pins") or []) for c in connectors)
    pcb_ports = inventory.get("pcb_ports") or []
    pcb_pad_count = sum(len(p.get("pads") or []) for p in pcb_ports)

    schematic_connector_names = {c.get("designator") for c in connectors}
    pcb_only_ports = [
        p
        for p in pcb_ports
        if p.get("designator") not in schematic_connector_names
    ]

    suspicious_nets = inventory.get("suspicious_nets") or []
    review_nets = []
    for net in suspicious_nets:
        endpoints = net.get("endpoints") or []
        has_mcu = any(str(ep.get("designator") or "").upper().startswith("MCU") for ep in endpoints)
        has_connector = any(
            str(ep.get("designator") or "").upper().startswith(("CN", "J", "P"))
            for ep in endpoints
        )
        if has_mcu or has_connector:
            review_nets.append(
                {
                    "name": net.get("name"),
                    "terminal_count": net.get("terminal_count"),
                    "has_mcu": has_mcu,
                    "has_connector": has_connector,
                }
            )

    return {
        "summary": {
            "mcu_pin_total": len(mcu_pins),
            "mcu_pin_classes": classes,
            "schematic_connectors": len(connectors),
            "schematic_connector_pins": connector_pin_count,
            "pcb_ports": len(pcb_ports),
            "pcb_port_pads": pcb_pad_count,
            "pcb_only_ports": len(pcb_only_ports),
            "suspicious_nets_for_review": len(review_nets),
        },
        "mcu_pins": pin_rows,
        "pcb_only_ports": pcb_only_ports,
        "suspicious_nets_for_review": review_nets,
    }


def to_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# 端口覆盖率检查",
        "",
        "## 摘要",
        "",
        "| 项目 | 数量 |",
        "| --- | --- |",
    ]
    for key, value in summary.items():
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in sorted(value.items()))
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "## MCU Pin 覆盖",
        "",
        "| Pin | Pin name | Net | Class |",
        "| --- | --- | --- | --- |",
    ]
    for pin in report["mcu_pins"]:
        lines.append(
            f"| {pin.get('pin','')} | {pin.get('pin_name','')} | {pin.get('net','')} | {pin.get('coverage_class','')} |"
        )

    lines += [
        "",
        "## PCB-only Ports",
        "",
        "| Designator | Footprint | Pads |",
        "| --- | --- | --- |",
    ]
    for port in report["pcb_only_ports"]:
        pads = ", ".join(f"{p.get('pad')}:{p.get('net')}" for p in port.get("pads") or [])
        lines.append(f"| {port.get('designator','')} | {port.get('footprint','')} | {pads} |")

    lines += [
        "",
        "## Suspicious Nets For Review",
        "",
        "| Net | Terminals | Has MCU | Has connector |",
        "| --- | --- | --- | --- |",
    ]
    for net in report["suspicious_nets_for_review"]:
        lines.append(
            f"| {net.get('name','')} | {net.get('terminal_count','')} | {net.get('has_mcu','')} | {net.get('has_connector','')} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory_json", type=Path)
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    inventory = json.loads(args.inventory_json.read_text(encoding="utf-8"))
    report = build_report(inventory)
    text = to_markdown(report) if args.format == "md" else json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
