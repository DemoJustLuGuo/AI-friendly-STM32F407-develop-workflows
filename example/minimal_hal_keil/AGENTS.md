# minimal_hal_keil Project Instructions

## Project Purpose

Minimal self-contained Keil MDK-ARM v5 template for STM32F407ZGT6 projects using STM32CubeF4 HAL.

The default firmware is only a board heartbeat: initialize HAL, configure the system clock, initialize LED1/LED2, and toggle both LEDs in the main loop.

## Toolchain

- IDE/toolchain: Keil MDK-ARM v5 / uVision
- Project file: `minimal_hal_keil.uvprojx`
- Target: `Target 1`
- Firmware stack: STM32CubeF4 HAL copied into this project under `Drivers/`
- Device macro: `STM32F407xx`
- Other required defines: `USE_HAL_DRIVER`, `HSE_VALUE=8000000`

## Source Entrypoints

- `User/main.c`: HAL initialization, clock setup, LED GPIO init, and heartbeat loop
- `User/stm32f4xx_hal_conf.h`: project-owned HAL module selection and clock constants
- `User/stm32f4xx_hal_msp.c`: minimal MSP initialization
- `User/stm32f4xx_it.c`: default exception handlers and SysTick tick forwarding
- `User/system_stm32f4xx.c`: CMSIS system source copied from STM32CubeF4
- `Startup/startup_stm32f407xx.s`: Keil/ARM startup and vector table

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
- `../../docs/software/base-libraries.md`

The local `Drivers/` directory is intentional. It keeps the template portable after clone or copy. When adding a new HAL peripheral, copy the required HAL `.c` file into `Drivers/STM32F4xx_HAL_Driver/Src/` and enable the matching module macro in `User/stm32f4xx_hal_conf.h`.

## Build And Flash

Manual Keil flow:

1. Open `minimal_hal_keil.uvprojx`.
2. Select target `Target 1`.
3. Build with F7.
4. Download through ST-Link/SWD.

Expected generated artifacts:

- `Output/minimal_hal_keil.hex`
- `Output/minimal_hal_keil.axf`

## Verification

After flashing, LED1 on PA5 and LED2 on PA4 should toggle together. The exact rate is not a timing contract; it is only a visible heartbeat.

## Do Not Edit Casually

- `Output/`, `Listings/`, `Objects/`, and `build/`
- Keil generated `.uvoptx`, `.uvguix.*`, listing, object, dependency, HEX, AXF, and map files
- Startup file and `system_stm32f4xx.c` unless changing chip family, compiler, clock tree, or memory layout
