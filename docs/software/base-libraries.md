# STM32F407 Repository Base Libraries

**Repository Role**: STM32F407-AI-develop-workflows base
**Library Root**: `lib/`  
**Supported Firmware Stacks**: STM32F4xx Standard Peripheral Library (SPL), STM32CubeF4 HAL/LL

This document records the stable library directories kept under `lib/` and how each one should be used when creating STM32F407 projects. It is a workspace-wide reference and copy source. Project directories should still carry the library subset they need when they are expected to build outside this workflow repository.

---

## Current Library Layout

```text
lib/
├── stm32f4xx/
├── STM32CubeF4/
└── stm32f4xx-hal-driver/
```

These three directories are the supported firmware development bases. Select the project stack during initialization, then copy or reference only the dependency subset required by that stack.

---

## `lib/stm32f4xx`

### Role

`lib/stm32f4xx` is the workspace dependency source for projects that choose the Standard Peripheral Library.

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

`lib/STM32CubeF4` is a trimmed STM32CubeF4 dependency source. It is retained for CMSIS Core, STM32F4 CMSIS Device files, startup/system templates, upstream metadata, and limited package documentation.

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

- A project chooses HAL/LL.
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

## Shared Dependency Boundary

Keep `lib/` limited to reusable STM32F407 firmware dependency bases. Board-specific application projects, generated build output, personal experiments, and third-party module demos should live outside `lib/` unless they are intentionally promoted into a documented shared package.

If LCD, Flash, sensor, or other board-matched drivers are needed later, create them inside the target project first. Promote them into a shared driver package only after confirming the actual schematic pins, electrical behavior, and bus-sharing rules.

---

## Stack Selection Summary

| Project type | Dependency base |
|---|---|
| SPL project | Copy from `lib/stm32f4xx` into project-local `lib/stm32f4xx` |
| HAL/LL project using Cube CMSIS references | Copy required CMSIS parts from `lib/STM32CubeF4` |
| HAL/LL project using standalone HAL driver | Copy CMSIS from `lib/STM32CubeF4` plus HAL driver from `lib/stm32f4xx-hal-driver` |

The project-level `AGENTS.md` must state which stack is selected, which dependency paths were copied or referenced, and which macros/configuration files are active.

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-01  
**Maintainer**: Workspace documentation system
