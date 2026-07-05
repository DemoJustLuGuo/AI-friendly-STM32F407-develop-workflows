# Hardware To Firmware Checklist

## Evidence Extraction

For PDF datasheets and application notes:

- Extract text and record page count.
- Check per-page text length; low text length usually means the important instructions are embedded in screenshots.
- Render pages as images and inspect diagrams, flowcharts, UI screenshots, code snippets, Keil settings, and red callouts.
- Do not rely only on text extraction when a manual is mostly screenshots.
- Preserve page images or a contact sheet when the visual content drives implementation.

For every MCU pin:

```text
MCU pin number
MCU pin name and alternate functions
Schematic net
Series resistor/filter/protection
Destination component or connector
PCB pad/object evidence
Firmware symbol/function
Polarity/pull/bias requirement
Uncertainty and required measurement
```

For each product feature:

- Display: chip, interface pins, command set, grid/segment mapping, brightness, startup state.
- Buzzer: active level, drive mode, desired tone frequency, timer/PWM source, series resistor/transistor, safe maximum duration. If the buzzer pin shares a GPIO port with display/control pins, use bit-addressable `sbit` operations for buzzer toggling; avoid whole-port read-modify-write operations that can disturb neighboring pins.
- LEDs: active level, common anode/cathode assumptions, reset state.
- Touch/keys: physical electrode/spring, series resistor, MCU TK/GPIO channel, library channel index, thresholds, scan period.
- UART/WiFi: TX/RX naming direction, voltage domains, enable pin polarity, startup timing.
- Power: MCU VDD net, LDO enable, brownout/reset assumptions, unconnected or PCB-only nets.

## Firmware Task Conversion

Convert hardware evidence into these implementation tasks:

1. Create `Config/board_config.h` mappings.
2. Implement `BSP_GPIO_Init()` with safe startup outputs and unused-pin handling.
3. Implement one driver per external IC.
4. Wrap vendor libraries behind BSP functions.
5. Copy vendor driver folders into the target firmware project when the vendor manual says to migrate/export them into the target project; update Keil include paths and project groups to point at the in-project copy.
6. Add diagnostics for each hardware block.
7. Build and confirm artifacts.
8. Create a board-test script/procedure.

## Review Checklist

Before declaring a board feature done:

- Does the code use the schematic net names or a documented mapping table?
- Are alternate-function pins configured for the intended peripheral?
- Are pull/bias states supported by hardware evidence or known-good firmware?
- Are vendor library service/restart calls present?
- Is there a visible diagnostic path if the feature fails?
- Are generated files excluded from manual source changes?
- Does the Keil target include the intended source and library files?
- If a vendor manual says to copy/export a driver folder into the target project, is the active project using that in-project folder rather than a sibling or stale original export?

## Known-Good Comparison

When a working firmware exists, compare:

- GPIO direction/pull/output latch writes.
- Vendor init, service, scan, clear, restart order.
- Interrupt enables and vector linkage in `.map`.
- Threshold/config arrays.
- Startup file and linker memory model.
- Optimization and memory model settings.
- The exact HEX being flashed.
