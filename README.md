# AI-friendly STM32F407 Develop Workflows

This repository is a public, AI-friendly STM32F407 development workflow core. It packages the reusable board reference, software conventions, and local agent skills needed to create, inspect, and maintain STM32F407 firmware projects with Codex, Claude Code, or similar coding agents.

It is not a full mirror of the original local workspace. Training projects, local build outputs, temporary runtime state, and external AD9959 material are intentionally excluded.

## What Is Included

```text
.
├── AGENTS.md
├── CLAUDE.md
├── docs/
│   ├── hardware/
│   └── software/
├── lib/
│   ├── STM32CubeF4/
│   ├── stm32f4xx/
│   └── stm32f4xx-hal-driver/
└── .agents/
    └── skills/
        └── ADtoKeil/
```

## Agent Workflow Files

- `AGENTS.md` is the primary operating guide for Codex-style agents. It defines workspace routing, hardware-reference rules, firmware dependency choices, and project-level documentation expectations.
- `CLAUDE.md` mirrors the same operational assumptions for Claude Code compatibility. Keep it aligned with `AGENTS.md` when shared rules change.

These files are intentionally focused on workspace-wide conventions. Project-specific behavior belongs in the target project's own `AGENTS.md`.

## Hardware References

`docs/hardware/schematic-stm32f407-board-c-v1.0.md` is the daily firmware-development reference. It records pin mappings, electrical behavior, power architecture, clock and boot settings, SPI bus sharing, and initialization checks for the STM32F407 board.

`docs/hardware/Schematic_STM32F407开发板-C-V1.0-2606_2026-06-22.pdf` is retained as the visual schematic authority when the Markdown index is missing a detail, when behavior conflicts with documentation, or when routing and component placement must be inspected.

## Software References

`docs/software/` contains reusable firmware-development guidance:

- `project-template.md` defines expected project layout, metadata, build-file placement, and Keil/GCC setup conventions.
- `board-bsp-guide.md` defines the board BSP architecture and reusable peripheral-driver style.
- `spl-quick-reference.md` provides STM32F4 Standard Peripheral Library initialization patterns and board-specific examples.
- `base-libraries.md` documents the shared firmware-library sources available in `lib/`.

Current practice work should normally use the SPL stack and BSP style documented here unless a project explicitly chooses HAL/LL or another architecture.

## Firmware Libraries

`lib/stm32f4xx/` is the default SPL/CMSIS dependency base for STM32F407 firmware work in this workflow.

`lib/STM32CubeF4/` provides the STM32CubeF4 CMSIS tree, including STM32F4 device headers, startup sources, and system templates required by HAL/LL projects.

`lib/stm32f4xx-hal-driver/` is the local equivalent of `Drivers/STM32F4xx_HAL_Driver` and contains the STM32F4 HAL/LL driver component.

Third-party ST, CMSIS, SPL, Cube, HAL, and LL files retain their upstream notices, README files, and license terms. This repository's workflow documentation does not rewrite or replace those third-party license obligations.

## Agent Skills

`.agents/skills/ADtoKeil/` contains reusable local skills and helper scripts for Altium-to-firmware analysis, embedded firmware generation, Keil builds, serial debugging, and workflow orchestration. Nested Git metadata, Python bytecode, and runtime caches are excluded.

## What Is Excluded

The following local materials are intentionally not part of this release:

- `practice/` training projects.
- `example/` project outputs and build products.
- `.embeddedskills/` local runtime state.
- `tmp/` scratch files.
- AD9959 external materials, including `lib/AD9959模块驱动+PDF-V2.6/` and `AD9959模块驱动+PDF-V2.6.rar`.
- Keil user-state files, debugger local settings, generated listings, object files, HEX/AXF artifacts, and build logs.

When adding public examples later, clean each project separately and keep only source, project metadata, project-level `AGENTS.md`, and reproducible build instructions.
