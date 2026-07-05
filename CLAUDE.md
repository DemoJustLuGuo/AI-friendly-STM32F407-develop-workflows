# STM32F407 Workspace Instructions

## Workspace Role

This directory is the public, AI-friendly workflow base for STM32F407 board projects.

- `example/minimal_spl_keil/` is a clone-ready Keil MDK-ARM v5 SPL minimal project template. It contains its own startup files, project-owned configuration files, and a minimal local SPL/CMSIS library subset under `Libraries/`.
- `example/minimal_hal_keil/` is a clone-ready Keil MDK-ARM v5 HAL minimal project template. It contains its own startup files, project-owned HAL configuration, CMSIS files, and a minimal local HAL driver subset under `Drivers/`.
- `practice/` is intentionally not included in this public release. Users may create it locally by copying `example/minimal_spl_keil/` or `example/minimal_hal_keil/` into a new project directory.
- `docs/hardware/schematic-stm32f407-board-c-v1.0.md` is the complete hardware reference for firmware development, containing pin mappings, peripheral electrical specifications, power system architecture, SPI bus arbitration rules, clock configuration, boot mode settings, and a 23-item firmware initialization checklist. Read this document before starting any firmware project to confirm hardware electrical characteristics.
- `docs/software/` contains the shared software development references for BSP design, SPL usage, and standard project templates.
- `docs/hardware/Schematic_STM32F407开发板-C-V1.0-2606_2026-06-22.pdf` is the original schematic PDF, used only for visual verification, PCB routing analysis, or when the Markdown index lacks a specific detail.

Keep this root document focused on workspace routing and shared hardware references. Do not record the business logic, exercise content, or implementation details of a single project here.

## Shared Firmware Dependencies

The workspace has shared firmware libraries under `lib/`.

### Standard Peripheral Library

Use `lib/stm32f4xx` as the default dependency base for current STM32F407 firmware work unless the user explicitly requests another stack.

Observed contents:

- `lib/stm32f4xx/README.md` identifies the package set as `Cortex-MCMSISV3.20`, `STM32F4xxCMSISV1.3.0`, `STM32F4xx_StdPeriphV1.3.0`, `STM32_USB_DeviceV1.1.0`, and `STM32_USB_OTGV2.1.0`.
- `lib/stm32f4xx/CMSIS/inc/` contains CMSIS core headers such as `core_cm4.h`.
- `lib/stm32f4xx/StdPeriph/inc/` contains STM32F4 SPL headers such as `stm32f4xx.h`, `system_stm32f4xx.h`, `stm32f4xx_gpio.h`, `stm32f4xx_rcc.h`, and `stm32f4xx_usart.h`.
- `lib/stm32f4xx/StdPeriph/src/` contains SPL sources such as `system_stm32f4xx.c`, `startup_stm32f4xx.s`, `stm32f4xx_gpio.c`, `stm32f4xx_rcc.c`, and `stm32f4xx_usart.c`.

Project-level SPL work should normally start from `example/minimal_spl_keil/` or copy the required SPL/CMSIS files into the project. Treat root `lib/` as the source library pool and reference material, not as a path that every portable Keil project should depend on. A project intended to be cloned, copied, or shared must include its own `stm32f4xx_conf.h`, interrupt handlers, startup file, required SPL `.c` files, linker/scatter settings, and build settings. For STM32F407ZGTx with this SPL tree, use the `STM32F40_41xxx` device-family macro unless a project-level reason says otherwise.

### STM32CubeF4 HAL/LL

`lib/stm32f4xx-hal-driver` is the STM32F4 HAL/LL driver component and can be used as the HAL/LL driver source when a project explicitly chooses the HAL/LL stack.

Observed contents:

- `lib/stm32f4xx-hal-driver/README.md` identifies it as ST's `stm32f4xx_hal_driver` MCU component, providing the HAL-LL Drivers part of STM32CubeF4.
- `lib/stm32f4xx-hal-driver/Inc/` contains HAL/LL headers, including `stm32f4xx_hal.h`, `stm32f4xx_hal_conf_template.h`, and `stm32f4xx_ll_gpio.h`.
- `lib/stm32f4xx-hal-driver/Src/` contains HAL/LL sources, including `stm32f4xx_hal.c`, `stm32f4xx_hal_gpio.c`, and `stm32f4xx_ll_gpio.c`.

In the official STM32CubeF4 package layout after extraction, the HAL/LL driver files normally live under:

```text
Drivers/STM32F4xx_HAL_Driver/Inc/
Drivers/STM32F4xx_HAL_Driver/Src/
```

CMSIS core and device files normally live under:

```text
Drivers/CMSIS/
```

In this workspace, the HAL/LL driver component has been downloaded separately as:

```text
lib/stm32f4xx-hal-driver/Inc/
lib/stm32f4xx-hal-driver/Src/
```

Treat that directory as the local equivalent of `Drivers/STM32F4xx_HAL_Driver` when wiring HAL/LL include paths and source files.

CMSIS Device for STM32F4 is available in the CubeF4 tree:

```text
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/
```

Observed required STM32F407 files:

- `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f407xx.h`
- `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f4xx.h`
- `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/system_stm32f4xx.h`
- `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/system_stm32f4xx.c`
- `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/gcc/startup_stm32f407xx.s`

For HAL/LL projects, use this dependency combination:

- CMSIS Core: `lib/STM32CubeF4/Drivers/CMSIS/Include/`
- CMSIS Device: `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/`
- System source: `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/system_stm32f4xx.c`
- GCC startup source: `lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/gcc/startup_stm32f407xx.s`
- HAL/LL headers: `lib/stm32f4xx-hal-driver/Inc/`
- HAL/LL sources: `lib/stm32f4xx-hal-driver/Src/`

Project-level HAL/LL work must still provide project-owned `stm32f4xx_hal_conf.h`, interrupt handlers, MSP initialization, linker script/scatter file, and build settings. For STM32F407ZGTx with this HAL/CMSIS tree, use the `STM32F407xx` macro unless a project-level reason says otherwise.

For clone-ready HAL/Keil projects, normally start from `example/minimal_hal_keil/`. Do not copy ST Eval-board `Projects/*/Templates` directly without removing Eval BSP dependencies, board macros, unsupported clock assumptions, and unused HAL modules.

## Shared Software Development References

The workspace has shared software guidance under `docs/software/`. Treat these files as reusable workspace conventions, not as project-specific implementation records.

- `docs/software/board-bsp-guide.md` defines the STM32F407 board BSP architecture, common `BSP_StatusTypeDef`, module naming, file layout, API style, and onboard peripheral interfaces for LED, key, buzzer, DHT11, shared SPI3, USART2, and SysTick.
- `docs/software/project-template.md` defines the standard firmware project layout, Keil MDK-ARM v5 target settings, GCC/`arm-none-eabi` template expectations, include paths, preprocessor defines, startup/linker placement, and quick-start project creation flow.
- `docs/software/spl-quick-reference.md` provides quick SPL API references and board-specific initialization templates for RCC, GPIO, USART, SPI, timers, NVIC, and common onboard peripheral examples.
- `docs/software/base-libraries.md` explains the role and source of the shared library directories published under `lib/`.

For current STM32F407 practice work, prefer the SPL stack and the BSP style described in these documents unless the user explicitly chooses HAL/LL or another architecture.

When creating or reshaping project software:

1. Use `docs/software/project-template.md` for directory layout, project metadata, build files, and Keil/GCC settings.
2. Use `docs/software/board-bsp-guide.md` for reusable board-facing code. Keep board pins, active levels, shared-bus selection, delays, and peripheral init inside `bsp/inc/` and `bsp/src/` rather than scattering them through application code.
3. Use `docs/software/spl-quick-reference.md` for SPL initialization patterns and board-specific code examples.
4. Keep application behavior in `src/` or an application-owned module. Do not put exercise-specific business logic into the shared BSP.
5. For clone-ready Keil projects, copy only the SPL source files actually needed by the project into the project tree, plus required common files such as `stm32f4xx_misc.c`, startup code, `system_stm32f4xx.c`, `stm32f4xx_conf.h`, and interrupt handlers. Do not leave the active project depending on a developer-specific shared-library path.
6. For shared SPI3 devices, always centralize chip-select handling so Flash and LCD are never selected at the same time.

For Codex work, `AGENTS.md` is the primary instruction file. `CLAUDE.md` may be created or kept alongside it for Claude Code compatibility when a project is intended to support both tools. When both files exist, keep their operational rules consistent; project setup, build commands, hardware assumptions, and verification steps should not diverge between them.

## Project Routing

When the user asks to create, modify, debug, or explain a concrete firmware project:

1. Read the hardware index first: before starting any firmware work, read `docs/hardware/schematic-stm32f407-board-c-v1.0.md` to confirm board-level electrical characteristics such as LED polarity, key logic, SPI bus sharing, power limits, and initialization requirements.
2. Read the relevant software guide before changing code structure or BSP/peripheral logic:
   - `docs/software/project-template.md` for new project layout or build settings.
   - `docs/software/board-bsp-guide.md` for reusable onboard peripheral drivers.
   - `docs/software/spl-quick-reference.md` for SPL initialization details.
3. Identify the target project directory first.
4. Work from inside that project directory.
5. If the target directory contains `AGENTS.md`, read it before inspecting or changing project files.
6. If the target directory does not contain `AGENTS.md`, create a project-level `AGENTS.md` before continuing with project changes.
7. Keep project-specific decisions in the project-level `AGENTS.md`, not in this root file.

If the requested project does not yet exist and the user wants an SPL/Keil project, copy `example/minimal_spl_keil/` into the requested project directory first, then update its project-level `AGENTS.md`, README, Keil output name, and source files for the new purpose.

If the requested project does not yet exist and the user wants a HAL/Keil project, copy `example/minimal_hal_keil/` into the requested project directory first, then update its project-level `AGENTS.md`, README, Keil output name, HAL module selection, and source files for the new purpose.

If the target architecture is neither SPL/Keil nor HAL/Keil, create the new project directory under the user-specified parent, then create its project-level `AGENTS.md` as part of initialization.

## Project-Level AGENTS.md Minimum Contents

A project-level `AGENTS.md` should be short but operational. Include at least:

- Project purpose and target board/chip.
- Toolchain and IDE, such as Keil v5, VS Code + EIDE, ARMCC, ARMClang, GCC, or `arm-none-eabi`.
- Build, clean, flash, and debug commands or manual IDE steps.
- Source entrypoints, BSP modules used, software stack selection, and important generated/vendor directories.
- Hardware dependencies from the board schematic. Reference specific sections of `docs/hardware/schematic-stm32f407-board-c-v1.0.md` that apply to the project, including GPIO mappings, active-high or active-low logic, peripheral electrical parameters, and shared-bus constraints. If the project uses board peripherals such as LEDs, keys, buzzer, DHT11, Flash, LCD, or USART, explicitly document the confirmed electrical behavior.
- Software references used from `docs/software/`, especially whether the project follows the standard template, BSP guide, and SPL quick-reference patterns.
- Directories or files that should not be edited casually, such as packs, generated build output, IDE metadata, or vendor libraries.
- Verification steps for the project, including compile, flash, debug connection, and hardware behavior.

When a project-level file is created from this rule, prefer conservative facts discovered from that project and this workspace. Always cross-reference `docs/hardware/schematic-stm32f407-board-c-v1.0.md` for hardware electrical characteristics rather than making assumptions. If hardware behavior is uncertain despite consulting the Markdown index, mark it as requiring physical-board verification and test the actual behavior before documenting it.

## Hardware Reference Rules

### Markdown Hardware Index (Primary Reference)

For all routine firmware development, use the Markdown hardware index as the first reference:

```text
docs/hardware/schematic-stm32f407-board-c-v1.0.md
```

This document contains comprehensive hardware information for firmware development:

- Complete pin mapping: all 144 GPIO pins with package pin numbers, physical grouping, and board-level signal assignments.
- Peripheral electrical specifications: circuit topologies, component values such as resistors and capacitors, driving logic, and current limits.
- Power system architecture: power tree from USB_5V to VDD/VDDA/VCAP/VBAT, decoupling capacitors, voltage regulator specifications, and current budgets.
- Clock configuration: HSE/LSE frequencies, load capacitor values, and firmware requirements such as the `HSE_VALUE` definition.
- Boot mode configuration: BOOT0/BOOT1 default states, boot mode truth table, and ISP entry procedure.
- SPI bus arbitration rules: shared SPI3 on PC10/PC11/PC12 between W25Q64 Flash and LCD, chip-select mutual exclusion, clock speed compatibility, and firmware best practices.
- Reset circuit timing and debounce behavior.
- Expansion connector specifications, including physical dimensions, pin counts, and special signal locations such as VREF+ and NRST.
- Firmware initialization checklist covering clock, GPIO, SPI, and USART configuration.
- Design notes and caveats for common pitfalls, hardware limitations, and workarounds.

The Markdown index is sufficient for daily firmware development without repeatedly consulting the PDF. Use it to configure GPIO pins correctly, initialize peripherals with correct electrical parameters, avoid hardware conflicts such as SPI bus sharing or JTAG pin reuse, verify power budget and supply decoupling, and debug hardware-related firmware issues.

### Schematic PDF (Authority Reference)

Use the schematic PDF only when:

- The Markdown index is missing a specific detail.
- Markdown information conflicts with observed board behavior.
- Visual verification of PCB routing or component placement is needed.
- Electrical connection direction must be traced for debugging.

```text
docs/hardware/Schematic_STM32F407开发板-C-V1.0-2606_2026-06-22.pdf
```

PDF verification is recommended for signal direction confirmation when debugging communication failures, connector physical pinout and orientation before external wiring, exact pull-up or pull-down resistor values if fine tuning is needed, component package and footprint for hardware modifications, and PCB trace routing for high-speed signal integrity analysis.

### Known Extraction Limits

- The PDF has a text layer, but some Chinese text is garbled when extracted.
- Automatic text extraction can list net names and component names, but it cannot reliably prove schematic connection direction or polarity.
- Critical electrical parameters such as LED polarity, key logic, resistor values, capacitor values, SPI connections, and power routing are documented in the Markdown index.
- If a project depends on exact electrical behavior, document the checked PDF location or the physical test result in the project-level `AGENTS.md`.

### Usage Guideline

Before starting any new firmware project or feature:

1. Read the relevant sections of `docs/hardware/schematic-stm32f407-board-c-v1.0.md`.
2. Confirm electrical characteristics of peripherals you will use, such as active levels, pull resistors, and SPI sharing.
3. Check the firmware initialization checklist to ensure required configurations are covered.
4. Consult the PDF only if the Markdown index lacks a specific detail you need.

During debugging:

1. Consult the Markdown index first for electrical parameters and known caveats.
2. If behavior contradicts documentation, verify with the PDF or physical board measurement.
3. Document any newly discovered hardware behavior in the project-level `AGENTS.md`.

## Root-Level Change Policy

- Add or update root-level docs only for workspace-wide rules, hardware references, or shared operating conventions.
- Do not modify `example/minimal_spl_keil/` or `example/minimal_hal_keil/` while performing root documentation work unless the user explicitly asks for template or project-level changes.
- Do not assume `practice/` exists in this public repository; it is normally a local user-created directory.
- Do not run firmware builds from the root unless the target project and build method are clear.
