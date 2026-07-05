# STM32F407 Workspace Base Libraries

**Workspace**: `F:\CODE\STM32F407`  
**Library Root**: `lib/`  
**Default Practice Stack**: STM32F4xx Standard Peripheral Library (SPL)

This document records the stable library directories kept under `lib/` and how each one should be used when creating STM32F407 projects. It is a workspace-wide reference and copy source. Small project directories should still carry the library subset they need when they are expected to build outside this workspace.

---

## Current Library Layout

```text
lib/
├── stm32f4xx/
├── STM32CubeF4/
├── stm32f4xx-hal-driver/
└── AD9959模块驱动+PDF-V2.6/
```

The first three directories are firmware development bases. `AD9959模块驱动+PDF-V2.6/` is a retained external module reference package and should not be treated as part of the standard STM32F407 base template.

---

## `lib/stm32f4xx`

### Role

`lib/stm32f4xx` is the default dependency source for current STM32F407 practice work using the Standard Peripheral Library.

Observed package set:

- `Cortex-MCMSISV3.20`
- `STM32F4xxCMSISV1.3.0`
- `STM32F4xx_StdPeriphV1.3.0`
- `STM32_USB_DeviceV1.1.0`
- `STM32_USB_OTGV2.1.0`

Important subdirectories:

| Path | Purpose |
|---|---|
| `CMSIS/inc/` | CMSIS core and STM32F4 device headers |
| `CMSIS/src/` | CMSIS support and optional DSP-related sources |
| `StdPeriph/inc/` | SPL peripheral headers |
| `StdPeriph/src/` | SPL peripheral sources |
| `USB_Device/`, `USB_OTG/`, `USB_Generic/` | Legacy USB device/OTG support |
| `FatFS/` | FatFS middleware |
| `Examples/` | Small examples from this library package |

### Usage Rules

For new SPL projects, copy the required subset into the project before final handoff:

```text
<project>/lib/stm32f4xx/CMSIS/
<project>/lib/stm32f4xx/StdPeriph/
```

Use project-local include paths in self-contained projects:

```text
lib/stm32f4xx/CMSIS/inc
lib/stm32f4xx/StdPeriph/inc
```

Workspace-relative paths such as `../../lib/stm32f4xx/...` are acceptable only for temporary local experiments or when the project is intentionally not self-contained.

Use preprocessor defines:

```text
STM32F40_41xxx
USE_STDPERIPH_DRIVER
HSE_VALUE=8000000
```

Add only the SPL source files needed by the project, plus common required files such as:

```text
stm32f4xx_rcc.c
stm32f4xx_gpio.c
stm32f4xx_flash.c
stm32f4xx_misc.c
```

Add feature drivers only when used, for example `stm32f4xx_tim.c`, `stm32f4xx_spi.c`, `stm32f4xx_usart.c`, or `stm32f4xx_adc.c`.

- Use local names `stm32f4xx_misc.h` and `stm32f4xx_misc.c`; do not copy older examples that use `misc.h` or `misc.c` unless adapting them intentionally.
- Keep project-owned files such as `stm32f4xx_conf.h`, `stm32f4xx_it.c`, `stm32f4xx_it.h`, startup files, and build metadata inside the project.

---

## `lib/STM32CubeF4`

### Role

`lib/STM32CubeF4` is the full ST STM32CubeF4 MCU package. It is retained as the authoritative HAL/LL package source and official example/reference tree.

Important subdirectories:

| Path | Purpose |
|---|---|
| `Drivers/CMSIS/` | CMSIS core and STM32F4 device support for Cube/HAL projects |
| `Drivers/STM32F4xx_HAL_Driver/` | HAL/LL driver headers and sources |
| `Drivers/BSP/` | ST board BSP drivers for supported official boards |
| `Middlewares/` | Cube middleware such as FatFS, USB, RTOS-related components |
| `Projects/` | Official examples, applications, and demonstrations for ST boards |
| `Utilities/` | Utility components used by Cube examples |
| `Documentation/` | Package documentation |

### Usage Rules

Use `STM32CubeF4` when:

- A project explicitly chooses HAL/LL instead of SPL.
- Official ST examples are needed as behavioral references.
- Cube middleware or official board BSP code is needed.
- The project needs CMSIS Device files from the Cube layout.

For HAL/LL projects targeting STM32F407ZGTx, the local Cube paths are:

```text
lib/STM32CubeF4/Drivers/CMSIS/Include/
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/system_stm32f4xx.c
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/gcc/startup_stm32f407xx.s
lib/STM32CubeF4/Drivers/STM32F4xx_HAL_Driver/Inc/
lib/STM32CubeF4/Drivers/STM32F4xx_HAL_Driver/Src/
```

Use the HAL/CMSIS device macro:

```text
STM32F407xx
```

Do not mix SPL project files and HAL project files in the same firmware unless the project has a deliberate compatibility layer.

---

## `lib/stm32f4xx-hal-driver`

### Role

`lib/stm32f4xx-hal-driver` is ST's standalone HAL/LL driver component. It contains only the HAL/LL driver `Inc/` and `Src/` trees plus release and license metadata.

Important subdirectories:

| Path | Purpose |
|---|---|
| `Inc/` | HAL/LL headers, including `stm32f4xx_hal.h`, `stm32f4xx_hal_conf_template.h`, and LL headers |
| `Src/` | HAL/LL source files |

### Usage Rules

Use this directory as the copy source when a HAL/LL project wants the smaller standalone driver component instead of referencing the HAL driver copy inside the full `STM32CubeF4` package.

When using it, still get CMSIS Core and CMSIS Device files from `lib/STM32CubeF4`. For a self-contained project, copy those needed directories into the project-local `lib/` tree and then use local paths equivalent to:

```text
lib/STM32CubeF4/Drivers/CMSIS/Include/
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/
lib/stm32f4xx-hal-driver/Inc/
lib/stm32f4xx-hal-driver/Src/
```

Choose one HAL driver source per project:

- Either `lib/STM32CubeF4/Drivers/STM32F4xx_HAL_Driver/`
- Or `lib/stm32f4xx-hal-driver/`

Do not compile both HAL driver trees into the same target.

---

## `lib/AD9959模块驱动+PDF-V2.6`

### Role

This directory is an external AD9959 DDS module dependency package. It is retained for future DDS-related projects, but it is not a workspace base library for ordinary STM32F407 firmware templates.

Observed contents:

| Path | Purpose |
|---|---|
| `README.md` | Package-level dependency guide |
| `AGENTS.md` | Package maintenance and future project usage rules |
| `AD9959移植到STM32F407指南.md` | Workspace-specific porting guide |
| `1.AD9959代码/` | Vendor example code |
| `2.芯片手册/` | AD9959 datasheets |
| `3.原理图PDF/` | Module and driver-board schematics, plus schematic-reading Markdown |
| `4.尺寸及定位图PDF/` | Mechanical drawings |
| `5.AD9959模块-STM32接线说明/` | Vendor STM32 wiring notes and Markdown table |
| `AD9959模块用户手册-简易_V1.1.pdf` | Module user manual |

The vendor examples are documented as Keil 5 projects for a DDS driver board and ST firmware library 3.5.0. Treat them as reference material that must be ported before use on this STM32F407 board.

For a future AD9959 project:

- Copy this package, or a documented subset of it, into the project-local dependency tree when the project must be portable.
- Read `README.md`, `AGENTS.md`, `AD9959移植到STM32F407指南.md`, the module schematic notes, and the English datasheet first.
- Map every AD9959 signal to this board's actual available GPIO pins.
- Wrap the ported DDS control code in a project-owned driver under `drivers/` or `bsp/`.
- Do not place AD9959-specific behavior into the generic SPL project template.

The typical reuse path is:

```text
vendor AD9959 example function -> AD9959 register/protocol intent -> project-owned driver -> STM32F407 BSP port -> application behavior
```

Do not reuse the vendor STM32F1 Keil project as the project template for STM32F407 work.

---

## Removed Non-Base Directories

These directories were removed from `lib/` because they were not suitable as workspace base libraries:

| Removed path | Reason |
|---|---|
| `lib/ili9341-official` | ST ILI9341 component only; not a complete board-matched F407 LCD stack |
| `lib/ili9341-hal` | Third-party HAL/CubeMX example, with STM32F7-specific files |
| `lib/ili9341-spi-spl` | Third-party SPL example targeting STM32F103, not STM32F407 |
| `lib/practice` | Practice/project material does not belong under shared library dependencies |

If LCD support is needed later, create or import a board-matched LCD driver in the target project or in a clearly named shared driver package after confirming the actual schematic pins and SPI3 sharing rules.

---

## Stack Selection Summary

| Project type | Default base |
|---|---|
| Current practice project using SPL | Copy from `lib/stm32f4xx` into project-local `lib/stm32f4xx` |
| HAL/LL project using full Cube references | Copy required parts from `lib/STM32CubeF4` |
| HAL/LL project using standalone HAL driver | Copy CMSIS from `lib/STM32CubeF4` plus HAL driver from `lib/stm32f4xx-hal-driver` |
| AD9959 DDS module project | Copy `lib/AD9959模块驱动+PDF-V2.6` or its required subset into the project, then add a project-owned AD9959 driver/port layer |

For this workspace, SPL remains the preferred stack for current STM32F407 practice work unless the user explicitly chooses HAL/LL.

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-01  
**Maintainer**: Workspace documentation system
