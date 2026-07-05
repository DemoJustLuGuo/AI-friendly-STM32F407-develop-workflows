---
name: altium-schematic-reader
description: Read and reason about Altium Designer projects and schematics using structured data from .PrjPcb and .SchDoc files. Use when the user asks an AI to understand, explain, review, debug, summarize, inspect, or query an Altium circuit design, including components, nets, pin-level connectivity, BOMs, variants, sheet hierarchy, power rails, or questions like what is connected to a pin.
---

# Altium Schematic Reader

Use this skill to answer questions about Altium schematic designs with grounded circuit facts instead of guesses from filenames or screenshots.

The bundled script reads Altium files through `altium-monkey` and returns compact JSON slices for AI reasoning.

## Prerequisites

`altium-monkey` must be importable in the Python environment.

Preferred installation:

```powershell
pip install altium-monkey
```

When working inside an `altium_monkey` source checkout, set `PYTHONPATH` to its `src/py` directory before running the script.

```powershell
$env:PYTHONPATH="path\to\altium_monkey\src\py"
```

## Locate The Design

If the user does not name a project, find candidate Altium projects:

```powershell
Get-ChildItem -Recurse -Filter *.PrjPcb
```

If there is more than one plausible project, ask which one to inspect. For a single `.SchDoc`, use the `sheet` command.

## Command Pattern

Run from any working directory:

```powershell
python <skill_dir>\scripts\read_schematic.py <command> [args]
```

All commands print JSON to stdout. Errors print JSON to stderr.

## Workflow

Always start with `summary` for a project you have not inspected in this session.

```powershell
python <skill_dir>\scripts\read_schematic.py summary path\to\Project.PrjPcb
```

Then choose targeted follow-up queries:

- Use `components --brief` to understand what is on a sheet.
- Use `nets` to list named nets or search rail/signal names.
- Use `nets --name NET_NAME` to inspect every terminal on a net.
- Use `connections --designator U1` to inspect all connected pins of a component.
- Use `connections --designator U1 --pin 5` for one pin.
- Use `bom` for bill of materials and variant questions.
- Use `sheet` only when no `.PrjPcb` is available.
- Use `raw design` or `raw netlist` only as a last resort because the output can be large.

For MCU, processor, connector, and header tables, do not rely only on netlist
connections. Netlists omit unconnected pins. Inspect the component symbol pins
(`component.pins` through `altium-monkey`, or `altium-circuit-investigator`
`port_inventory.py`) and merge those pins with netlist endpoints so every pin is
listed, including `NC/未连接` pins.

## Commands

Project summary:

```powershell
python <skill_dir>\scripts\read_schematic.py summary path\to\Project.PrjPcb
```

Components:

```powershell
python <skill_dir>\scripts\read_schematic.py components path\to\Project.PrjPcb --brief
python <skill_dir>\scripts\read_schematic.py components path\to\Project.PrjPcb --sheet Power.SchDoc --brief
python <skill_dir>\scripts\read_schematic.py components path\to\Project.PrjPcb --designator U7
```

Nets:

```powershell
python <skill_dir>\scripts\read_schematic.py nets path\to\Project.PrjPcb
python <skill_dir>\scripts\read_schematic.py nets path\to\Project.PrjPcb --contains P3V3
python <skill_dir>\scripts\read_schematic.py nets path\to\Project.PrjPcb --name GND
```

Pin-level connectivity:

```powershell
python <skill_dir>\scripts\read_schematic.py connections path\to\Project.PrjPcb --designator U7
python <skill_dir>\scripts\read_schematic.py connections path\to\Project.PrjPcb --designator U7 --pin C9
```

BOM:

```powershell
python <skill_dir>\scripts\read_schematic.py bom path\to\Project.PrjPcb
python <skill_dir>\scripts\read_schematic.py bom path\to\Project.PrjPcb --variant PCBA_Build
```

Single sheet:

```powershell
python <skill_dir>\scripts\read_schematic.py sheet path\to\Sheet.SchDoc
```

Raw escape hatch:

```powershell
python <skill_dir>\scripts\read_schematic.py raw path\to\Project.PrjPcb design
python <skill_dir>\scripts\read_schematic.py raw path\to\Project.PrjPcb netlist
```

## Reasoning Rules

- Cite designators, pin numbers, net names, and sheet filenames in answers.
- Prefer project-level commands over single-sheet inspection because designators and hierarchy are resolved at project level.
- Do not infer connectivity from symbol graphics or component names when a netlist query is available.
- Distinguish "not present in the netlist" from "not present on the symbol": an unconnected symbol pin must still be reported as NC when pin coverage matters.
- For any unclear signal name such as `CTRL`, `OUT`, `IN`, `FB`, `AD`, `QD`, or `AUX`, inspect local schematic labels or use `altium-circuit-investigator` before naming the function.
- For "what does this circuit do", inspect `summary`, then sheet-level component briefs, then connections for the main ICs.
- For power questions, inspect `summary.power_and_ground_nets`, rail-like net names, and POWER pins on target ICs.
- For review questions, look for evidence first, then separate confirmed issues from hypotheses.

## Known Boundaries

- Complex hierarchical channels and `.Annotation`-driven mappings may need manual validation.
- Variant support depends on `altium-monkey` and may be limited for unusual variant setups.
- Parse failures should be reported with the failing file path and exact JSON error.
- `altium-monkey` is AGPL-3.0-or-later; review license obligations before embedding it in a distributed or network service.

## References

Read `references/software_design.md` when designing a backend, API, cache, UI, or AI workflow around this skill.
