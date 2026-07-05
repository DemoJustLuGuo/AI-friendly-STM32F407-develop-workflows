# STM32F407 Repository Base Libraries

**Repository Role**: AI-friendly STM32F407 workflow base
**Library Root**: `lib/`  
**Default Practice Stack**: STM32F4xx Standard Peripheral Library (SPL)

This document records the stable library directories kept under `lib/` and how each one should be used when creating STM32F407 projects. It is a workspace-wide reference and copy source. Small project directories should still carry the library subset they need when they are expected to build outside this workspace.

---

## Current Library Layout

```text
lib/
├── stm32f4xx/
├── STM32CubeF4/
└── stm32f4xx-hal-driver/
```

These three directories are firmware development bases. External AD9959 module packages are intentionally not published in this repository and should not be treated as part of the standard STM32F407 base template.

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

Repository-relative paths such as `../../lib/stm32f4xx/...` are acceptable only for temporary local experiments or when the project is intentionally not self-contained.

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

`lib/STM32CubeF4` is a trimmed STM32CubeF4 dependency source. It is retained for CMSIS Core, STM32F4 CMSIS Device files, startup/system templates, upstream metadata, and limited package documentation. Official board examples, applications, demonstrations, and media utilities are not retained in this public workflow repository.

Important subdirectories:

| Path | Purpose |
|---|---|
| `Drivers/CMSIS/` | CMSIS core and STM32F4 device support for Cube/HAL projects |
| `Drivers/STM32F4xx_HAL_Driver/` | HAL/LL driver headers and sources |
| `Drivers/BSP/` | ST board BSP drivers for supported official boards |
| `Middlewares/` | Cube middleware such as FatFS, USB, RTOS-related components |
| `Documentation/` | Package documentation |

### Usage Rules

Use `STM32CubeF4` when:

- A project explicitly chooses HAL/LL instead of SPL.
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

## Removed Non-Base Directories

These directories were removed from `lib/` because they were not suitable as workspace base libraries:

| Removed path | Reason |
|---|---|
| `lib/ili9341-official` | ST ILI9341 component only; not a complete board-matched F407 LCD stack |
| `lib/ili9341-hal` | Third-party HAL/CubeMX example, with STM32F7-specific files |
| `lib/ili9341-spi-spl` | Third-party SPL example targeting STM32F103, not STM32F407 |
| `lib/practice` | Practice/project material does not belong under shared library dependencies |
| External AD9959 module package | Third-party module reference material; intentionally excluded from this public workflow base |

If LCD support is needed later, create or import a board-matched LCD driver in the target project or in a clearly named shared driver package after confirming the actual schematic pins and SPI3 sharing rules.

---

## Stack Selection Summary

| Project type | Default base |
|---|---|
| Current practice project using SPL | Copy from `lib/stm32f4xx` into project-local `lib/stm32f4xx` |
| HAL/LL project using Cube CMSIS references | Copy required CMSIS parts from `lib/STM32CubeF4` |
| HAL/LL project using standalone HAL driver | Copy CMSIS from `lib/STM32CubeF4` plus HAL driver from `lib/stm32f4xx-hal-driver` |

For this workspace, SPL remains the preferred stack for current STM32F407 practice work unless the user explicitly chooses HAL/LL.

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-01  
**Maintainer**: Workspace documentation system
