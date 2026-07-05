---
name: embedded-firmware-from-hardware
description: Build and review maintainable embedded MCU firmware from schematic, PCB, netlist, pin-map, BOM, Keil/C51/MDK projects, vendor demo code, or hardware debug evidence. Use when Codex must convert hardware design knowledge into firmware architecture, BSP/HAL code, pin configuration, peripheral drivers, board diagnostics, touch-key/keypad/display/buzzer/WiFi bring-up, or investigate why firmware does not match schematic/PCB behavior.
---

# Embedded Firmware From Hardware

## Core Rule

Treat the schematic/PCB as the source of truth for pins and nets, and treat vendor libraries as state machines with required setup, service, restart, and IO-bias contracts. Do not replace a vendor peripheral flow with intuition such as "this should be high impedance" unless the working reference, datasheet, or measured behavior supports it.

## Workflow

1. **Extract hardware evidence**
   - Build a pin map: MCU pin, alternate function, schematic net, series parts, destination component, PCB pad, and uncertainty.
   - Trace each user-visible function end-to-end: input electrode/switch -> resistor/filter -> MCU pin -> firmware symbol -> behavior.
   - Mark polarity, pull state, power domain, level shifting, reset/default state, and "needs measurement" items.
   - For MCU datasheets, app notes, and vendor PDFs, extract text first; if text is sparse or screenshots contain instructions, render pages as images and read the visual content before deciding the implementation. Prefer `scripts/pdf_evidence.py` for repeatable extraction/rendering. For Chinese filenames on Windows, enumerate PDFs with Python `Path.glob()` or use a Python launcher/environment that preserves Unicode paths.

2. **Choose firmware ownership**
   - Put product logic in `App/`.
   - Put board pins and MCU registers in `BSP/`.
   - Put external chips/protocols in `Drivers/`.
   - Keep vendor libraries under a clear folder inside the target firmware project, such as `Firmware/TKDriver/`, and wrap them with a BSP adapter. Do not leave a Keil project depending on a sibling `../TKDriver` path when the vendor manual says to copy/export the driver into the target project.
   - Keep `Config/board_config.h` as the board contract: clocks, pin/channel mappings, timings, display mapping, diagnostic flags.

3. **Bring up in layers**
   - First verify clock, power-safe GPIO defaults, and unused-pin handling.
   - Then bring up one visible output path such as display or buzzer.
   - Then bring up one input path with an on-board diagnostic display before integrating product behavior.
   - Only after each layer is observable should `App/` depend on it.

4. **Use board diagnostics**
   - Prefer diagnostics that work without a debugger: display status codes, beep patterns, LED patterns, or UART logs.
   - Distinguish "interrupt not firing", "scan not completing", "raw event present", and "mapped application event present".
   - Never diagnose "no input response" only from product behavior; add counters/status at the BSP boundary.

5. **Compare against known-good evidence**
   - When a known-good firmware exists, diff BSP pin setup, vendor library call order, restart/service calls, thresholds, project options, startup files, and linker output.
   - Favor the smallest transferable differences rather than wholesale copying generated output.

6. **Create the buildable project when requested**
   - If the user asks for embedded software development and a Keil/C51 toolchain is present, create or update a real `.uvproj`/`.uvprojx` project unless the user explicitly says not to.
   - Put vendor groups such as `TKDriver` visibly in the project tree, include headers/config files for review, include all required `.C` and `.LIB` files for build, then run UV4 build/rebuild to prove the HEX path.

## Implementation Standards

Use [references/architecture.md](references/architecture.md) when designing or refactoring firmware structure.

Use [references/hardware-to-firmware-checklist.md](references/hardware-to-firmware-checklist.md) when converting a schematic/PCB report into code tasks.

Use [references/pdf-datasheet-workflow.md](references/pdf-datasheet-workflow.md) when a PDF datasheet or app note must be read with both text extraction and rendered page evidence.

Use [references/vendor-touch-libraries.md](references/vendor-touch-libraries.md) when working with capacitive touch, spring touch keys, TK libraries, or scan/restart/threshold problems.

Use [references/sinone-sc95f861xb.md](references/sinone-sc95f861xb.md) when working with SinOne/SOC SC95F861xB 8051 MCUs, especially GPIO, TK, UART0, USCI SPI/TWI/UART, clock options, interrupts, and Keil C51 register setup.

Use [references/keil-c51-project-review.md](references/keil-c51-project-review.md) when a Keil C51/8051 project builds but hardware behavior is wrong, or when comparing a current project against a known-good Keil project.

## Debugging Heuristics

- If a visible app keeps running but input has no effect, confirm the BSP input event before touching app logic.
- If a capacitive touch channel never fires, inspect IO mode, pull/bias state, selected channel mask, threshold bytes, interrupt enable, status bit handling, and required restart call.
- If changing thresholds does nothing, assume the scan flow or IO-bias contract may be wrong.
- If a diagnostic build still shows old product behavior, suspect the wrong HEX was flashed or the flash operation did not take.
- If a register comment says "input" but known-good code sets output/pull bits, trust measured/known-good behavior until the datasheet register semantics are confirmed.

## Deliverables

When using this skill, finish with:

- The hardware evidence used.
- The firmware files changed or proposed.
- The reason each pin/register/library call is needed.
- Build result and artifact path.
- A board-test procedure with observable expected results.
