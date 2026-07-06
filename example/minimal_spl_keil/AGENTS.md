# minimal_spl_keil Project Instructions

## Project Purpose

Minimal self-contained Keil MDK-ARM v5 template for STM32F407ZGT6 projects using the STM32F4 Standard Peripheral Library.

The default firmware is only a board heartbeat: configure the system clock, initialize LED1/LED2, and toggle both LEDs in the main loop. Replace or extend this behavior when creating a real project.

## Toolchain

- IDE/toolchain: Keil MDK-ARM v5 / uVision
- Project file: `minimal_spl_keil.uvprojx`
- Target: `Target 1`
- Firmware stack: STM32F4 Standard Peripheral Library copied into this project under `Libraries/`
- Device macro: `STM32F40_41xxx`
- Other required defines: `USE_STDPERIPH_DRIVER`, `HSE_VALUE=8000000`

## Environment Initialization Status

Status: not initialized after copy.

The first coding agent working on this project must probe the current machine and replace this section with confirmed facts:

- Keil MDK-ARM v5 installed: yes/no; `UV4.exe` or `UV5.exe` path if available.
- Keil compiler selected by this project: ARMCC5 or ARMClang6; note whether `.uvprojx` migration is required.
- STM32F4 Device Family Pack installed: yes/no and version if known.
- VS Code + EIDE available: yes/no; compiler path used by EIDE if applicable.
- `arm-none-eabi-gcc`, `make`, and `cmake` available: yes/no with paths if used.
- Flash/debug tool available: ST-Link, J-Link, OpenOCD, pyOCD, or manual IDE-only flow.
- Verified build command or manual build steps for this machine.

## Source Entrypoints

- `User/main.c`: clock setup, LED GPIO init, and heartbeat loop
- `User/stm32f4xx_it.c`: default exception handlers
- `User/stm32f4xx_conf.h`: SPL header selection
- `User/system_stm32f4xx.c`: project-owned system clock support source
- `Startup/startup_stm32f4xx.s`: Keil/ARM assembler startup and vector table

## Hardware Dependencies

Read `../../docs/hardware/schematic-stm32f407-board-c-v1.0.md` before changing pins.

Confirmed hardware behavior used by this template:

- LED1 is PA5, active-high. GPIO high turns LED on; GPIO low turns LED off.
- LED2 is PA4, active-high. GPIO high turns LED on; GPIO low turns LED off.
- HSE is an 8MHz crystal on PH0/PH1. Keep `HSE_VALUE=8000000`.

No SPI3, LCD, Flash, USART, key, buzzer, or DHT11 behavior is enabled in this minimal template.

## Software References

This project follows:

- `../../docs/software/project-template.md`
- `../../docs/software/board-bsp-guide.md`
- `../../docs/software/spl-quick-reference.md`

The local `Libraries/` directory is intentional. It keeps the template portable after clone or copy. When adding a new peripheral, copy the required SPL `.c` file into `Libraries/STM32F4xx_StdPeriph_Driver/src/` and enable the matching header in `User/stm32f4xx_conf.h`.

## Build And Flash

Manual Keil flow:

1. Open `minimal_spl_keil.uvprojx`.
2. Select target `Target 1`.
3. Build with F7.
4. Download through ST-Link/SWD.

Expected generated artifacts:

- `Output/minimal_spl_keil.hex`
- `Output/minimal_spl_keil.axf`

## Verification

After flashing, LED1 on PA5 and LED2 on PA4 should toggle together. The exact rate is not a timing contract; it is only a visible heartbeat.

## Do Not Edit Casually

- `Output/`, `Listings/`, `Objects/`, and `build/`
- Keil generated `.uvoptx`, `.uvguix.*`, listing, object, dependency, HEX, AXF, and map files
- Startup file and `system_stm32f4xx.c` unless changing chip family, compiler, clock tree, or memory layout
