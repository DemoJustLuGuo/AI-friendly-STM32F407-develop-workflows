# Keil C51 Project Review

Use this when a Keil 8051/C51 project builds but the board behaves incorrectly, or when porting vendor demo code into a product project.

## First Checks

- Confirm the project file and Target are the ones being built.
- Confirm the HEX being flashed is the HEX from the latest successful build.
- Confirm generated `.lst`, `.map`, and `.hex` timestamps match the current source.
- Compare the current project against a known-good project before changing logic.

## Source Inclusion

Check that the Keil Target includes:

- `STARTUP.A51` or the MCU/vendor startup file expected by the chip.
- MCU SFR header matching the exact device family.
- Vendor driver `.C` files, not only headers.
- Vendor `*.LIB` files required by exported libraries such as `TKDriver`.
- Vendor driver folders copied into the target project when the vendor manual requires migration into the target project. Avoid a fragile project that only references a sibling folder outside the firmware project.
- Board BSP files that contain the current pin setup.
- The intended app file, not an old demo app.

Use the `.map` file to confirm important functions are linked:

- Interrupt service routines.
- Vendor library init/service/restart functions.
- BSP wrappers used by `App/`.

## Interrupt Review

- C51 interrupt numbers must match the datasheet vector table, not only the vector address.
- Confirm global `EA` and peripheral enable bits are both set.
- Confirm flags that require software clearing are cleared in the ISR or service loop.
- Confirm flags that are hardware auto-cleared are not incorrectly polled as sticky state.
- Confirm ISR functions are not optimized out and appear in `.map`.
- Avoid heavy application logic inside ISR; call vendor service only when required by the vendor flow.

## Clock And Code Option

For clock-sensitive code, verify:

- Keil/ISP Code Option clock selection.
- `SYS_CLOCK_HZ` and delay constants.
- Timer reload values.
- UART baud generator source and reload.
- TWI/SPI clock dividers.
- Touch scan timing and threshold assumptions.

If the product depends on HRC/IRC frequency, note voltage and temperature drift and prefer tolerant timeouts.

## Memory Model And C51 Pitfalls

- Check SMALL/COMPACT/LARGE memory model against vendor library assumptions.
- For SinOne Magic Box TKDriver, use LX51 and Large memory model / variables in XDATA when the manual or library requires it.
- Check `data`, `idata`, `xdata`, and `code` qualifiers in vendor APIs.
- Large arrays should usually live in `xdata` or `code`.
- Shared ISR/main variables should be `volatile`.
- Multi-byte values shared with ISR should be read atomically or with a stable-copy pattern.
- C51 `bit` variables and `sbit` hardware aliases should stay in low-level modules.
- Watch stack usage when adding diagnostics or formatted output.

## Register And Pin Review

- Raw SFR writes should stay in BSP/vendor adapter files.
- Comments must explain non-obvious register values, especially when a known-good project contradicts generic datasheet intuition.
- For alternate-function pins, verify both the pin mux/mode and the required GPIO latch/bias state.
- For unused pins, document safe defaults instead of leaving reset state unexplained.

## Build Log Review

Treat warnings as important in embedded work:

- Missing prototypes can hide wrong calling conventions.
- Implicit int / pointer conversion can corrupt C51 memory-space accesses.
- Uncalled segment removal can reveal functions not reached by app code.
- Multiple definitions can mean both demo and product drivers are linked.

## Minimal Review Output

When reporting a C51 project review, include:

```text
Project/Target:
Build result:
HEX path:
Clock assumption:
Startup/vector status:
Vendor files included:
Vendor folder location:
Critical ISR/vector evidence:
Pin/register risks:
Known-good differences:
Board-test procedure:
```
