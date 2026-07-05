---
name: altium-circuit-investigator
description: Evidence-led analysis of Altium schematic and PCB designs using netlist tracing, full symbol-pin coverage, connector and PCB pad inventories, local schematic screenshots/SVG labels, component topology, and explicit uncertainty. Use when Codex must understand, document, review, or map hardware from .SchDoc, .PcbDoc, .PrjPcb, Gerber, screenshots, or exported schematic images, including MCU pin maps, external port definitions, firmware/software functions, sensors, actuators, power rails, and unclear circuit blocks.
---

# Altium Circuit Investigator

Use this skill to understand Altium designs without guessing. It complements `altium-schematic-reader`: first collect structured net/component data, then prove circuit meaning with topology, local labels, PCB evidence, and coverage checks.

## Prime Directive

Do not state a circuit function as fact until it is supported by evidence. A net name, part value, or symbol shape is only a clue. Confirm with:

- exact netlist endpoints: designator, pin, pin name, net
- full symbol pin coverage, including NC/unconnected pins
- local schematic text/labels/screenshots
- topology through passives, transistors, optocouplers, relays, sensors, and connectors
- PCB pads, side, placement, and net names
- datasheet or measurement when polarity or behavior is not proven

Use evidence levels:

- **Confirmed**: proven by netlist, symbol pins, PCB, local image/text, or datasheet.
- **Likely**: topology strongly supports it but polarity, external harness, or exact behavior is not proven.
- **Hypothesis**: plausible but weakly supported.
- **Unknown / needs review**: do not decide yet.

## Non-Negotiable Coverage Gates

Before writing a final report or design document:

1. Run a port inventory when possible.
2. Include every MCU/processor symbol pin, not only pins that appear in the netlist. Mark missing nets as `NC/未连接`.
3. Include every schematic connector pin, including empty/no-connect pins when the symbol exposes them.
4. Compare schematic connector pins with PCB pads and call out mismatches.
5. Render or inspect local schematic context for every signal still described as "unknown", "aux", "control", "out", "in", "feedback", or only by a cryptic name.
6. Deep-trace each firmware-relevant control/feedback signal at least one active device beyond the MCU.
7. List open questions explicitly. Do not silently drop pins, ports, PCB-only jumpers, or parser warnings.

## Investigation Workflow

1. Identify inputs:
   - Prefer `.PrjPcb` for full hierarchy.
   - Use `.SchDoc` when only one sheet is available.
   - Use `.PcbDoc` to confirm physical connectors, pads, PCB-only jumpers, layer side, and net names.
   - Treat screenshots/rendered SVG as required evidence when local labels or block titles matter.
   - On Windows, if `altium_monkey` is missing under the default `python`, check other installed launchers such as `py -3.12` before falling back. Do not assume the dependency is absent until the Python environment has been checked.

2. Build the first map:
   - Run `scripts/port_inventory.py --schdoc ... --pcbdoc ... --out inventory.json` when possible. Use the Python interpreter that can import `altium_monkey`, e.g. `py -3.12 script.py ...` on machines where default `python` is too new or lacks the package.
   - Run `scripts/coverage_report.py inventory.json --format md --out coverage.md`.
   - Check summary counts: MCU pins, connector pins, PCB-only ports, suspicious nets.
   - If there is no `.PcbDoc`, still run schematic inventory and mark PCB confirmation as unavailable.

3. Create full MCU/processor coverage:
   - Use symbol pins as the source of completeness.
   - Merge each symbol pin with its netlist endpoint when connected.
   - For every pin, document: pin number, pin name/alternate functions, net, function, evidence, and firmware implication.
   - Mark unconnected pins as `NC/未连接`; for oscillator/reset/debug pins, say what must be configured or verified.
   - Watch for same-net surprises, such as one analog net tied to two MCU pins.

4. Inventory external and board-level ports:
   - List schematic connector pins and PCB pad nets side by side.
   - Distinguish external ports from PCB-only jumpers, 0-ohm links, copper straps, test pads, fiducials, and marks.
   - Preserve pin-order mismatches or footprint extra pads instead of normalizing them away.

5. Trace target nets:
   - Start from the user-named net, MCU pin, connector pin, or unknown signal.
   - Run `scripts/trace_net_deep.py` for multi-hop traces.
   - Follow through passives, transistor bases/gates, optocouplers, relays, sensors, switches, protection parts, and connector/load endpoints.
   - Stop at processors/large IC internals unless a datasheet or pin function is being checked.

6. Inspect local schematic context:
   - Run `scripts/render_region.py` around target nets or coordinates.
   - Search the SVG text for nearby Chinese/English labels, block titles, notes, connector labels, and part values.
   - Use image/SVG labels as evidence, not as a replacement for netlist facts.
   - For any generic label like `QD_CTRL`, `QD_OUT`, `AUX`, `IN`, `OUT`, `CTRL`, `FB`, or `AD`, inspect the local region before naming the function.

7. Infer function:
   - Combine netlist endpoints, topology, local labels, and PCB confirmation.
   - Confirm the final endpoint: load, sensor, communication interface, supply rail, feedback path, debug header, or board-only jumper.
   - State active polarity only when topology proves it. If a sensor's physical orientation or threshold matters, require datasheet or measurement.

8. Reflect before output:
   - Ask what evidence would disprove the conclusion.
   - Reverse-check every claimed function from external connector/load back to MCU.
   - Check that all MCU pins, connectors, and suspicious nets from the coverage report are represented somewhere in the output.

## Output Contract

For a targeted circuit explanation:

```text
Conclusion:
Evidence:
- netlist: ...
- topology: ...
- image/local label: ...
- pcb: ...
Reasoning:
Firmware/software meaning:
Risks / To confirm:
```

For a Markdown design document:

1. Source files and parser confidence.
2. System/block summary.
3. Full MCU/processor pin table.
4. External connector table with schematic and PCB evidence.
5. PCB-only jumpers/test pads/terminals.
6. Power rails and domains.
7. Functional blocks: actuators, sensors, communications, metering, protections.
8. Key net traces with evidence.
9. Firmware/software mapping: GPIO/ADC/PWM/UART/I2C/timers, safe states, filters, faults, production tests.
10. Confirmed facts, likely conclusions, and open questions.

## Firmware-Oriented Rules

When turning hardware into firmware requirements:

- Include startup safe state for every output.
- Include pull-up/pull-down and expected idle level when proven.
- Include debounce/filtering for switches, sensors, tach/FG, water level, tilt, and fault inputs.
- Include ADC scaling/calibration only when resistor topology and reference are known.
- Include production-test hooks for every actuator/sensor.
- Mark active polarity as **measurement_needed** when a physical sensor, relay contact, optocoupler direction, or external harness can invert behavior.

## Bundled Resources

- Use `scripts/port_inventory.py` to collect schematic connectors, full symbol pins, MCU pins, suspicious named nets, local labels, and PCB ports/pads.
- Use `scripts/coverage_report.py` to summarize completeness and highlight MCU pins, PCB-only ports, and suspicious nets.
- Use `scripts/trace_net_deep.py` to trace a net through passives, drivers, optocouplers, relays, switches, and connectors.
- Use `scripts/render_region.py` to render a full or cropped schematic SVG around a net endpoint or coordinate.
- Use `scripts/schdoc_probe.py` for single-sheet `.SchDoc` net tracing and SVG rendering when project-level tools are unavailable.
- Use `scripts/generate_firmware_design_report.py` when a Chinese Markdown firmware-design scaffold is useful.
- Read `references/topology-patterns.md` when inferring function from connected components.
- Read `references/evidence-checklist.md` before finalizing a design document or disputed answer.
- Read `references/firmware-from-hardware.md` when generating embedded firmware/software design details.
