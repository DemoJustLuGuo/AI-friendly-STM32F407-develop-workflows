# STM32F407 Project Template Guide

**Target Board**: STM32F407ZGT6 Development Board  
**Repository Role**: AI-friendly STM32F407 workflow base
**Supported Toolchains**: Keil MDK-ARM v5, GNU ARM GCC (arm-none-eabi)

This document defines standard project directory structures, build system templates, and configuration files for STM32F407 firmware projects. Following these templates ensures consistency across practice projects and simplifies project setup.

---

## Shared Library Baseline

Use `docs/software/base-libraries.md` as the source of truth for the workspace-level `lib/` inventory.

For current STM32F407 practice projects, the default firmware source is:

```text
lib/stm32f4xx
```

This workspace-level directory is the source used to create project-local library copies. Small projects should normally carry the library files they need under their own `lib/` directory so the project can be sent to another machine and still build without requiring the full workspace.

This provides the SPL-oriented `CMSIS/` and `StdPeriph/` trees used by the standard project template. HAL/LL projects should intentionally select either the full `lib/STM32CubeF4` package or the `lib/STM32CubeF4` Cube CMSIS files plus `lib/stm32f4xx-hal-driver`, as described in the base library guide.

Do not use external module packages, LCD examples, or practice projects as generic template dependencies unless the target project explicitly needs them and their hardware mappings have been verified.

---

## Table of Contents

1. [Shared Library Baseline](#shared-library-baseline)
2. [Project Directory Structure](#project-directory-structure)
3. [Keil MDK-ARM Project Template](#keil-mdk-arm-project-template)
4. [GNU ARM GCC Makefile Template](#gnu-arm-gcc-makefile-template)
5. [Quick Start Guide](#quick-start-guide)
6. [Additional Resources](#additional-resources)

---

## Project Directory Structure

### Standard Layout

```
project-name/
├── AGENTS.md                   # Project-specific Codex documentation
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview and build instructions
│
├── bsp/                        # Project-local Board Support Package
│   ├── inc/
│   └── src/
│
├── lib/                        # Project-local firmware library subset
│   └── stm32f4xx/
│       ├── CMSIS/
│       └── StdPeriph/
│
├── src/                        # Application source code
│   ├── main.c
│   ├── stm32f4xx_it.c         # Interrupt handlers
│   └── system_stm32f4xx.c     # System initialization
│
├── inc/                        # Application header files
│   ├── stm32f4xx_conf.h       # SPL configuration
│   └── stm32f4xx_it.h         # Interrupt handler declarations
│
├── startup/                    # Startup and linker files
│   ├── startup_stm32f40_41xxx.s   # For Keil/ARMCC or ARMClang
│   ├── startup_stm32f407xx.s      # For GCC
│   └── STM32F407ZGTx_FLASH.ld     # GCC linker script
│
├── build/                      # Build output (generated, not in git)
│   ├── obj/                    # Object files
│   └── bin/                    # Final binaries (.hex, .bin, .elf)
│
├── Makefile                    # GNU ARM GCC build script
│
└── project-name.uvprojx        # Keil MDK-ARM project file
```

### Directory Purpose

| Directory | Purpose | In Git? |
|-----------|---------|---------|
| `bsp/` | Board Support Package drivers | Yes for self-contained projects |
| `lib/` | Project-local SPL/HAL library subset copied from workspace `lib/` | Yes for portable small projects |
| `src/` | Application source code | Yes |
| `inc/` | Application headers | Yes |
| `startup/` | Startup code and linker scripts | Yes |
| `build/` | Build artifacts (obj, bin, hex) | No |

For workspace-only experiments, a project may reference `../../lib/...` directly to avoid duplication. For practice deliverables, examples sent to others, or any project expected to build outside this workspace, copy the required library subset into the project-level `lib/` directory and point the build system at that local copy.

---

## Keil MDK-ARM Project Template

### Project Structure in Keil

```
Project Target: STM32F407ZGTx
├── Application
│   ├── src/main.c
│   ├── src/stm32f4xx_it.c
│   └── src/system_stm32f4xx.c
│
├── BSP
│   ├── bsp/src/bsp_led.c
│   ├── bsp/src/bsp_key.c
│   ├── bsp/src/bsp_beep.c
│   ├── bsp/src/bsp_dht11.c
│   ├── bsp/src/bsp_spi.c
│   ├── bsp/src/bsp_usart.c
│   └── bsp/src/bsp_systick.c
│
├── StdPeriph
│   ├── lib/stm32f4xx/StdPeriph/src/stm32f4xx_gpio.c
│   ├── lib/stm32f4xx/StdPeriph/src/stm32f4xx_rcc.c
│   ├── lib/stm32f4xx/StdPeriph/src/stm32f4xx_flash.c
│   ├── lib/stm32f4xx/StdPeriph/src/stm32f4xx_misc.c
│   └── lib/stm32f4xx/StdPeriph/src/<feature-driver>.c
│
└── Startup
    └── startup/startup_stm32f40_41xxx.s
```

### Keil Project Settings

#### Target Options

**Device**: `STMicroelectronics → STM32F407ZGTx`

**Target Settings**:
- Crystal: `8.0 MHz` (HSE)
- Use MicroLIB: `Unchecked` (or checked for smaller code size)

#### C/C++ Compiler Settings

**Include Paths**:
```
inc
bsp/inc
lib/stm32f4xx/CMSIS/inc
lib/stm32f4xx/StdPeriph/inc
```

**Preprocessor Defines**:
```
STM32F40_41xxx
USE_STDPERIPH_DRIVER
HSE_VALUE=8000000
```

**Optimization**: `Level 0 (-O0)` for debug, `Level 3 (-O3)` for release

**C99 Mode**: Enabled

**Warnings**: `All Warnings`

### Keil Build Preflight

Before the first build of a generated or copied Keil project, verify these items against the actual workspace files instead of copying paths blindly from another example:

1. **Startup file must match the Keil compiler**:
   - For Keil ARMCC/ARMClang, use an ARM assembler startup file such as `startup_stm32f40_41xxx.s` from the standard Keil examples.
   - Do not use GCC/Atollic startup files with ARMCC/ARMClang. Symptoms include assembler errors such as `A1167E: Invalid line start`, `A1137E: Unexpected characters at end of line`, or `Unknown opcode`.
2. **Clock macro must be explicit**:
   - Add `HSE_VALUE=8000000` to Keil C/C++ preprocessor defines for this board.
   - Missing this macro can produce `#error "OSC value not defined!"` from the device header.
3. **SPL source filenames must match this workspace**:
   - This workspace uses `lib/stm32f4xx/StdPeriph/src/stm32f4xx_misc.c`, not `misc.c`.
   - Add only the SPL source files used by the project, plus required common files such as `stm32f4xx_rcc.c`, `stm32f4xx_gpio.c`, `stm32f4xx_flash.c`, `stm32f4xx_misc.c`, and feature drivers such as `stm32f4xx_spi.c` or `stm32f4xx_adc.c`.
4. **SPL header names must match this workspace**:
   - Include `stm32f4xx_misc.h` from `stm32f4xx_conf.h`, not `misc.h`, unless a compatibility header exists in the project.
5. **Project XML path check**:
   - Every `<FilePath>` in `.uvprojx` should point to an existing file before opening Keil.
   - Include paths should cover project-owned headers and both project-local library include roots:
     `lib/stm32f4xx/CMSIS/inc` and `lib/stm32f4xx/StdPeriph/inc`.
   - If a temporary workspace-only project references `../../lib/...`, document that it is not self-contained.
6. **Warnings are part of the preflight result**:
   - Treat unused functions and stale copied code as cleanup items before handing off a practice project.
   - Target state for template-derived projects is `0 errors, 0 warnings`.

#### Linker Settings

**Read/Only Memory Areas**:
- IROM1: Start `0x08000000`, Size `0x100000` (1MB Flash)

**Read/Write Memory Areas**:
- IRAM1: Start `0x20000000`, Size `0x20000` (128KB SRAM)

**Scatter File**: Use default or custom scatter file for advanced memory layout

#### Debug Settings

**Debug Adapter**: `ST-Link Debugger`

**Settings**:
- Port: `SW` (Serial Wire)
- Max Clock: `10 MHz`
- Reset and Run: Enabled

**Flash Download**:
- Programming Algorithm: `STM32F4xx Flash` (auto-selected)
- Erase Full Chip: Before programming
- Verify: After programming

---

## GNU ARM GCC Makefile Template

The current standard path is Keil MDK-ARM. GCC support is allowed, but the Makefile must be generated and verified per project because startup, linker script, compiler flags, and library-copy layout must match the chosen toolchain.

For GCC projects, use the same project-local library policy:

```text
lib/stm32f4xx/CMSIS/inc
lib/stm32f4xx/StdPeriph/inc
lib/stm32f4xx/StdPeriph/src/
```

Do not treat this section as a complete GCC build file until a verified workspace GCC template exists.

---

## Quick Start Guide

### Create New Project from Template

#### Step 1: Create Project Directory

```bash
cd practice
mkdir my-new-project
cd my-new-project
```

#### Step 2: Create Project Structure

```bash
mkdir src inc bsp startup lib build
```

#### Step 3: Copy Required Library Files

For a self-contained SPL project, copy the required library subset from the workspace base library:

```bash
mkdir -p lib/stm32f4xx
cp -r ../../lib/stm32f4xx/CMSIS lib/stm32f4xx/
cp -r ../../lib/stm32f4xx/StdPeriph lib/stm32f4xx/
```

If the project does not use USB, FatFS, or DSP functions, do not copy those optional trees into the project. Add only the source files required by the Keil target.

#### Step 4: Create Boilerplate Files

Create or copy the project-owned files:
- `inc/stm32f4xx_conf.h`
- `inc/stm32f4xx_it.h`
- `src/stm32f4xx_it.c`
- `src/main.c`
- `src/system_stm32f4xx.c` or `lib/stm32f4xx/StdPeriph/src/system_stm32f4xx.c`, depending on whether the project owns system-clock customization
- `startup/startup_stm32f40_41xxx.s` for Keil ARMCC/ARMClang
- `.gitignore`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md` if the project is also maintained with Claude Code

#### Step 5: Create Build System

**For Keil**: Create a new `.uvprojx`, follow the settings in this guide, and point source/include paths to the project-local `lib/` copy.

**For GCC**: Create a Makefile only after selecting and verifying the startup file, linker script, and compiler flags for the project.

#### Step 6: Configure Library Paths

**In Keil**: Add include paths:

```
inc
bsp/inc
lib/stm32f4xx/CMSIS/inc
lib/stm32f4xx/StdPeriph/inc
```

Add common SPL sources from the project-local copy:

```text
lib/stm32f4xx/StdPeriph/src/stm32f4xx_rcc.c
lib/stm32f4xx/StdPeriph/src/stm32f4xx_gpio.c
lib/stm32f4xx/StdPeriph/src/stm32f4xx_flash.c
lib/stm32f4xx/StdPeriph/src/stm32f4xx_misc.c
```

Then add feature drivers such as `stm32f4xx_tim.c`, `stm32f4xx_spi.c`, `stm32f4xx_usart.c`, or `stm32f4xx_adc.c` only when used.

#### Step 7: Build and Test

```bash
# Keil
# Press F7 in Keil IDE
```

The target state for a template-derived project is `0 errors, 0 warnings`.

#### Step 8: Create Agent Documentation

Create `AGENTS.md` for Codex and, when Claude Code compatibility is required, create a matching `CLAUDE.md`.

Document project-specific details in both files or explicitly make one file point to the other:
- Purpose and goals
- Hardware used
- Build commands
- Verification steps

For Codex work, `AGENTS.md` is the primary instruction file. For Claude Code work, `CLAUDE.md` may mirror the same operational rules. Keep them consistent when project setup, build commands, or hardware assumptions change.

---

## Additional Resources

- **Base Libraries**: `docs/software/base-libraries.md`
- **Hardware Reference**: `docs/hardware/schematic-stm32f407-board-c-v1.0.md`
- **BSP Guide**: `docs/software/board-bsp-guide.md`
- **SPL Reference**: `docs/software/spl-quick-reference.md`
- **Workspace Guide**: `AGENTS.md`

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-01  
**Maintainer**: Workspace documentation system
