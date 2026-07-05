# Firmware Architecture Reference

## Folder Layout

Use this structure for small MCU products:

```text
Bootloader/   optional upgrade/IAP layer
Config/       board constants, timing, pin/channel/display mapping
BSP/          MCU registers, board GPIO, timers, UART, touch adapters
Drivers/      external IC drivers and protocol implementations
App/          product state machine and user behavior
H/            MCU vendor headers
Vendor/       unmodified vendor libraries, when practical
```

Keep `main.c` thin:

```c
void main(void)
{
    Bootloader_Init();
    if (!Bootloader_ShouldStay()) {
        App_Init();
        while (1) {
            App_Run();
        }
    }
    while (1) {
        Bootloader_Service();
    }
}
```

## Layer Contracts

`Config/board_config.h` should contain:

- MCU clock and timing constants.
- Product timing values.
- Net-to-channel mappings.
- Display grid/segment mapping.
- Diagnostic feature flags.

`BSP/` should expose board-level functions, not raw product actions:

```c
void BSP_GPIO_Init(void);
void BSP_Touch_Init(void);
u32  BSP_Touch_ReadKeys(void);
u16  BSP_Touch_GetScanCount(void);
void BSP_Buzzer_BeepMs(u16 ms);
```

`Drivers/` should hide external chip timing:

```c
void AIP1624_Init(void);
void AIP1624_Clear(void);
void AIP1624_DisplayTwoDigits(u8 value);
```

`App/` should not write MCU registers directly. It should consume BSP/driver events and commands:

```c
static void App_ProcessTouch(void)
{
    u32 keys = BSP_Touch_ReadKeys();
    if (keys != 0) {
        /* product behavior */
    }
}
```

## Register Code Rules

- Keep all raw SFR access in BSP or vendor adapters.
- Write comments explaining why a non-obvious register value is required, especially when a known-good version contradicts intuition.
- Preserve vendor-recommended initialization order.
- Use readback/debug helpers for fragile peripherals.

## Diagnostics

Add diagnostics before product behavior:

- Display `channel_count` after touch init.
- Display status codes for interrupt/scan/key states.
- Beep on first recognized input edge.
- Count ISR and scan-complete events separately.

Example status scheme for two-digit displays:

```text
10       touch interrupt has not fired
20..99   interrupt fires, scan not yet mapped to a key
80..99   scan completes, no key detected
01..08   key index detected
```

## Build Hygiene

- Keep a known-good HEX and source folder when hardware behavior is verified.
- Build after every pin/library-flow change.
- Record artifact path and metrics.
- Do not rely on generated `.lst`, `.map`, or object files as source of truth, but use them to confirm interrupt vectors and linked vendor functions.
