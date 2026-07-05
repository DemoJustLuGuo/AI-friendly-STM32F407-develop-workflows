# ADtoKeil · Hardware → Firmware Skill Suite

> **Languages:** **English** · [简体中文](README.zh-CN.md)

> An **embedded hardware development skill suite** for AI agents (Claude Code / Codex): from reading Altium schematics, to evidence-led circuit analysis, hardware-driven firmware, Keil builds, serial debugging, and one-click workflow orchestration — enabling AI to understand and develop embedded systems from **verifiable circuit evidence** rather than guesswork.

[![Skills](https://img.shields.io/badge/skills-6-2de2e6)](#skill-overview)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776ab)](#requirements)
[![Platform](https://img.shields.io/badge/platform-Windows-0a7bd6)](#requirements)
[![License](https://img.shields.io/badge/license-AGPL--3.0-orange)](#license--compliance)

---

## Table of Contents

- [What is this](#what-is-this)
- [Core Principles](#core-principles)
- [Skill Overview](#skill-overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Skills in Detail](#skills-in-detail)
- [Typical Workflow](#typical-workflow)
- [Configuration](#configuration)
- [License & Compliance](#license--compliance)
- [Contributing](#contributing)
- [Star History](#star-history)
- [Acknowledgements](#acknowledgements)

---

## What is this

`ADtoKeil` is a collection of **skills** callable by AI coding assistants (Claude Code, Codex, etc.). Each skill consists of a `SKILL.md` (capability declaration + invocation contract) and a set of Python scripts, covering the key stages of embedded development:

```
Schematic Reading → Circuit Analysis → Firmware Generation → Keil Build → Serial Debug → Workflow Orchestration
```

The core problem it solves: **stop the AI from "guessing the circuit from filenames/screenshots", and instead reason from structured netlists, pin-level connectivity, PCB pads, and local annotations — all verifiable evidence.**

## Core Principles

- **Evidence-led** — Net names, part values, and symbol shapes are only clues. A conclusion must be proven by netlist endpoints, full symbol-pin coverage, PCB pads, local labels, or datasheets.
- **Explicit uncertainty** — Conclusions are graded `Confirmed` / `Likely` / `Hypothesis` / `Unknown`. Never present a hypothesis as fact.
- **Hardware is the source of truth** — The schematic/PCB defines pins and nets; vendor libraries are treated as state machines with init / service / restart / IO-bias contracts.
- **Layered, observable firmware** — Verify clock and safe GPIO defaults first, bring up output/input paths layer by layer, and only then let the application layer depend on them.
- **Don't guess, list candidates** — When multiple projects / targets / ports / backends exist, list candidates for the user to choose instead of deciding arbitrarily.

---

## Skill Overview

| # | Skill | Purpose | When it triggers |
|---|-------|---------|------------------|
| 1 | **altium-schematic-reader** | Parse `.PrjPcb` / `.SchDoc` → compact JSON slices | Understand, explain, review, or query an Altium design (components/nets/pins/BOM/power) |
| 2 | **altium-circuit-investigator** | Evidence-led net tracing + full pin coverage + PCB cross-check | Prove circuit function, map MCU pins, define external ports before writing a report/design doc |
| 3 | **embedded-firmware-from-hardware** | Build/review maintainable MCU firmware from hardware evidence | Turn hardware knowledge into BSP/HAL code, pin config, peripheral drivers, board diagnostics |
| 4 | **keil** | Drive Keil MDK/uVision to scan · build · emit HEX | Anything involving Keil/MDK/UV4/C51/8051, compile, build/rebuild/clean, artifact paths |
| 5 | **serial** | UART/COM port scan · monitor · send/receive · log | Serial debugging, baud rate, AT commands, hex streams, capturing UART evidence |
| 6 | **workflow** | Thin orchestrator: build → flash → debug → observe | Explicit requests for "one-click build/flash / auto-diagnosis" |

---

## Architecture

```
Presentation / Orchestration
  └─ workflow            (select backends, chain skills, aggregate results)
        │
        ├─ keil          (build backend: scan project / enumerate targets / build·rebuild·clean / parse log → HEX)
        ├─ serial        (observe backend: scan / monitor / send-receive / log)
        └─ flash·debug   (placeholder: J-Link / OpenOCD / probe-rs — needs an extra backend skill)

Understanding / Design
  ├─ altium-schematic-reader      (structured facts: netlist / components / nets / connections / BOM)
  ├─ altium-circuit-investigator  (evidence reasoning: trace / coverage / port inventory / region render)
  └─ embedded-firmware-from-hardware (hardware → firmware: layered BSP / Drivers / App + board diagnostics)

State Hub
  └─ .embeddedskills/state.json   (chains per-stage artifacts and context within a workspace)
```

**Dependency direction:** `workflow` calls lower-level skills; the understanding layer feeds facts to the firmware layer; skills collaborate via workspace config and state files under `.embeddedskills/`.

---

## Requirements

- **OS:** Windows (examples use PowerShell; Keil invocation depends on `UV4.exe`)
- **Python:** 3.12+ (caches show 3.12 / 3.14 both run)
- **Optional dependencies:**
  - `altium-monkey` (required by skills 1 & 2 to parse Altium files)
  - `pyserial` (skill 5 serial I/O)
  - Keil MDK / C51 (skill 4 `UV4.exe`)

> On Windows, if the default `python` is too new or missing a dependency, try another launcher such as `py -3.12` before concluding the dependency is absent.

---

## Installation

```powershell
# 1) Get the suite (drop it into your AI assistant's skills directory, or clone locally)
git clone https://github.com/Tansuo2021/ADtoKeil.git

# 2) Required to parse Altium files (skills 1 / 2)
pip install altium-monkey
# When using an altium_monkey source checkout:
$env:PYTHONPATH="path\to\altium_monkey\src\py"

# 3) Required for serial debugging (skill 5)
pip install pyserial

# 4) Keil build (skill 4): install Keil MDK and point keil/config.json at UV4.exe
```

Every skill's scripts run standalone. The unified command pattern is:

```powershell
python <skill_dir>\scripts\<script>.py <command> [args] [--json]
```

> `<skill_dir>` is the absolute or relative path to that skill's folder in your environment.

---

## Quick Start

```powershell
# Read an Altium project: always start with summary
python <skill_dir>\scripts\read_schematic.py summary path\to\Project.PrjPcb

# Inspect all connections of an MCU
python <skill_dir>\scripts\read_schematic.py connections path\to\Project.PrjPcb --designator U7

# One-click build (when a Keil backend is configured)
python <skill_dir>\scripts\workflow_run.py build --json

# Scan serial ports and monitor the boot banner
python <skill_dir>\scripts\serial_scan.py --json
python <skill_dir>\scripts\serial_monitor.py --port COM3 --baudrate 115200 --timestamp --timeout 10
```

---

## Skills in Detail

### 1. altium-schematic-reader
Reads Altium files via `altium-monkey` and emits **compact JSON slices** for AI reasoning. All commands print JSON to stdout (errors to stderr).

| Command | Purpose |
|---------|---------|
| `summary <prj>` | Project overview (preferred entry; includes power/ground nets) |
| `components <prj> [--brief\|--sheet\|--designator]` | Component list |
| `nets <prj> [--contains\|--name]` | Net list / all terminals on a net |
| `connections <prj> --designator U7 [--pin C9]` | Component / single-pin connectivity |
| `bom <prj> [--variant]` | BOM and variants |
| `sheet <schdoc>` | Use only when a single `.SchDoc` is available |
| `raw <prj> design\|netlist` | Last-resort escape hatch (output can be large) |

**Reasoning rules:** cite designators, pin numbers, net names, sheet filenames; prefer project-level over single-sheet; distinguish "not in netlist" from "not on symbol" (mark unconnected pins as `NC`).

### 2. altium-circuit-investigator
Complements skill 1: collect structured net/component data first, then prove circuit meaning with topology, local labels, PCB evidence, and coverage checks.

**Non-negotiable coverage gates (before a report):** port inventory → cover every MCU symbol pin (mark missing nets `NC`) → cover every connector pin → schematic vs PCB pad comparison → render local context for every "unknown" signal → deep-trace each firmware-relevant control/feedback signal at least one active device beyond the MCU → list open questions explicitly.

| Script | Purpose |
|--------|---------|
| `port_inventory.py` | Collect connectors, full symbol pins, MCU pins, suspicious nets, local labels, PCB pads |
| `coverage_report.py` | Summarize completeness; highlight MCU pins / PCB-only ports / suspicious nets |
| `trace_net_deep.py` | Multi-hop trace through passives, drivers, optocouplers, relays, switches, connectors |
| `render_region.py` | Render schematic SVG around a net endpoint/coordinate |
| `schdoc_probe.py` | Single-sheet `.SchDoc` tracing/rendering when project-level tools are unavailable |
| `generate_firmware_design_report.py` | Generate a Chinese firmware-design document scaffold |

### 3. embedded-firmware-from-hardware
Turns hardware knowledge into a **maintainable firmware architecture**. Core rule: the schematic/PCB is the source of truth for pins and nets; vendor libraries are state machines with init/service/restart/IO-bias contracts — do not replace their flow with intuition.

**Firmware ownership (layered):** `App/` (product logic) · `BSP/` (board pins & MCU registers) · `Drivers/` (external chips/protocols) · vendor libs (e.g. `Firmware/TKDriver/`) inside the target project, wrapped by a BSP adapter · `Config/board_config.h` as the board contract.

**Bring up in layers:** clock/safe GPIO/unused pins → one output path (display/buzzer) → one input path with on-board diagnostics → only then let `App/` depend on it.

### 4. keil
Drives Keil/uVision (8051/C51 and MDK). Prefer the scripts over invoking `UV4.exe` by hand.

| Script / Command | Purpose |
|------------------|---------|
| `keil_project.py scan --root <ws> --json` | Scan `.uvproj/.uvprojx/.uvmpw` projects |
| `keil_project.py targets --project <p> --json` | Enumerate targets |
| `keil_build.py build\|rebuild\|clean --project <p> --target <t> --workspace <ws> --json` | Build and parse log; return HEX/AXF paths & metrics |

After success: report project, target, log file, errors/warnings, HEX/AXF paths; persist to `.embeddedskills/state.json` for workflow reuse.

> Parameter priority: CLI > workspace config > skill config > `state.json` > scan result.
> Never edit `.uvproj/.uvprojx/.uvopt/.uvoptx` unless the user explicitly asks.

### 5. serial
UART/COM observation and command exchange during bring-up.

| Script | Purpose |
|--------|---------|
| `serial_scan.py --json` | Scan available ports |
| `serial_monitor.py --port COM3 --baudrate 115200 --timestamp` | Text monitor (filters/timestamps) |
| `serial_send.py "AT" --crlf --wait-response --json` | Send text (optional response wait) |
| `serial_send.py "01 03 00 00 00 02" --hex --json` | Send hex |
| `serial_hex.py` | View binary stream as a hex dump |
| `serial_log.py --duration 30 --timestamp --json` | Record logs (text/CSV/JSON) |

**Bring-up pattern:** scan & confirm adapter → monitor reset banner → if no output, check baud / TX-RX / voltage domain / firmware UART init / whether the current HEX was flashed → log evidence before changing firmware → send one minimal request and wait.

> Safety: never send data unless required; don't guess the port when several exist; don't guess baud rate; prefer passive monitoring.

### 6. workflow
A **thin coordinator** — it does not duplicate lower-level logic; it selects backends, calls lower-level scripts, and chains results via `.embeddedskills/state.json`.

```powershell
python <skill_dir>\scripts\workflow_run.py plan|build|build-flash|build-debug|observe|diagnose --json
```

Backend selectors: `--build-backend auto|keil|gcc`, `--flash-backend`/`--debug-backend`/`--observe-backend auto|jlink|openocd|probe-rs`.

> Current boundary: Keil build works when configured; flash/debug/observe are orchestration placeholders until a dedicated backend is configured. On any failure, report that stage first with the lower-level log path.

---

## Typical Workflow

```text
Goal: take an unfamiliar board and produce working firmware

1. Read the circuit   altium-schematic-reader        summary → connections / nets
                            ↓ structured facts
2. Analyze evidence   altium-circuit-investigator     port_inventory → coverage_report
                            ↓ full pin coverage + deep net trace + PCB cross-check (Confirmed/Likely/Hypothesis)
3. Derive firmware    embedded-firmware-from-hardware layered BSP/Drivers/App + board_config.h
                            ↓
4. Build artifact     keil                            scan → build → parse log → out/firmware.hex
                            ↓ writes .embeddedskills/state.json
5. Flash & observe    serial                          scan → monitor boot banner → log evidence
                            ↓
6. Orchestrate        workflow                        build → flash → debug → observe (aggregated)
```

---

## Configuration

Workspace-level config lives in `.embeddedskills/config.json`:

```json
{
  "keil": {
    "uv4_exe": "C:/Keil_v5/UV4/UV4.exe",
    "project": "path/to/project.uvproj",
    "target": "Target 1",
    "log_dir": ".embeddedskills/build"
  },
  "serial": {
    "port": "COM3",
    "baudrate": 115200,
    "encoding": "utf-8",
    "log_dir": ".embeddedskills/logs/serial"
  },
  "workflow": {
    "preferred_build": "keil",
    "preferred_flash": "auto",
    "preferred_debug": "auto",
    "preferred_observe": "auto"
  }
}
```

- See each skill's `config.example.json` for reference.
- `keil` also supports an environment-level `keil/config.json` pointing at `UV4.exe`. **This file holds real machine paths and is git-ignored** — copy `config.example.json` to `config.json` locally.
- Cross-stage state is maintained in `.embeddedskills/state.json` (also git-ignored).

---

## License & Compliance

This project is released under the **GNU Affero General Public License v3.0 (AGPL-3.0)** — see [`LICENSE`](LICENSE).

> **Why AGPL-3.0:** skills 1 & 2 depend on **`altium-monkey`**, which is licensed under **AGPL-3.0-or-later**. Adopting AGPL-3.0 for this project keeps it compatible with that dependency. Note that AGPL is "viral": if you **distribute** a modified version, or **expose its functionality through a network service**, you must make the corresponding source available under AGPL-3.0. Review the license before distributing or hosting.

Also note: the previous repo state contained hardcoded local paths and a personal username; these have been removed for public release. Keep machine-specific config (`keil/config.json`, `.embeddedskills/`, `.env`) out of version control via [`.gitignore`](.gitignore).

---

## Contributing

Issues / PRs welcome:

- **New skill:** include a `SKILL.md` (with `name` + `description` frontmatter) and standalone scripts; commands should support `--json`.
- **Code style:** scripts emit structured JSON, errors to stderr; list candidates instead of guessing when ambiguous.
- **Docs:** add domain knowledge under `references/`; keep the "evidence-first, explicit-uncertainty" style.
- **Tests:** cover the happy path and edges (null values, missing PCB, busy port, build failure, etc.).
- **Compliance:** never commit personal paths, usernames, secrets, or machine-specific config.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Tansuo2021/ADtoKeil&type=Date)](https://star-history.com/#Tansuo2021/ADtoKeil&Date)

If this project helps you, please consider giving it a ⭐ — it really helps!

---

## Acknowledgements

- Thanks to the **[linux.do](https://linux.do)** community — for the sharing, discussion, and inspiration that made this suite possible. 🙏
- Built to be driven by AI coding agents such as Claude Code and Codex.
- Altium parsing powered by the open-source [`altium-monkey`](https://pypi.org/project/altium-monkey/) project.
