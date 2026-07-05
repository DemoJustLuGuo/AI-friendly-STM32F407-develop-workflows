# Vendor Touch Library Reference

## General Pattern

Capacitive touch and spring-touch libraries are usually not GPIO readers. Treat them as scan engines:

```text
configure selected channels
configure required IO bias
enable touch interrupt
vendor init
wait for scan-complete status
clear status as required by vendor flow
read mapped key flags
restart scan if required
```

Do not assume:

- Touch electrodes should always be high impedance.
- A lower threshold always fixes no-touch.
- `TouchKeyScan()` alone starts the next scan.
- GPIO comments from unrelated demo code apply to TK alternate functions.

## Required Checks

For a no-response touch key:

1. Confirm physical net: electrode/spring -> resistor/filter -> MCU TK pin.
2. Confirm channel mask selects the actual TK numbers.
3. Confirm `SOCAPI_SET_TOUCHKEY_TOTAL` equals selected channels.
4. Confirm each config row's channel byte matches the selected TK number.
5. Confirm threshold bytes are real values, not placeholders such as `0xff,0xff`.
6. Confirm TK interrupt enable and global interrupt enable.
7. Confirm the interrupt vector is linked in `.map`.
8. Confirm the scan-complete bit is cleared in the correct order.
9. Confirm the vendor restart/service call happens after a scan if required.
10. Compare IO bias setup against a known-good firmware.

## SinOne Magic Box TKDriver Migration

When a SinOne Magic Box touch manual or exported `TKDriver` folder is present:

- Treat the manual screenshots as implementation evidence. If text extraction is sparse, render every relevant page and inspect the red callouts and Keil option screenshots.
- Copy/export the complete `TKDriver` folder into the target firmware project directory, for example `Firmware/TKDriver/`. Do not only reference a sibling `../TKDriver` folder from the Keil project.
- Preserve the exported folder structure when possible. If the export is flattened, keep it as a visible `TKDriver` group in Keil and document the deviation.
- Include `TKDriver.C` and every vendor `*.LIB` in the Keil Target. Add `TKDriver.h` and config headers such as `S_TouchKeyCFG.h` to the project tree so configuration is reviewable.
- Add include paths for both the driver root and the folder containing `TKDriver.h`, for example `.\TKDriver` and `.\TKDriver\TKDriver`.
- Enable the extended LX51 linker and set C51 Memory Model to Large / variables in XDATA when the vendor library is Large.
- Keep application key behavior in `App/` or a user-code function. Do not edit the vendor scan engine to implement product behavior.

## SC95F861xB / TKDriver Lesson

For the SC95F8613B display-board touch springs:

- Hardware nets:
  - `KEY1=TK23/P2.7`
  - `KEY2=TK22/P2.6`
  - `KEY3=TK21/P2.5`
  - `KEY4=TK18/P2.2`
  - `KEY5=TK19/P2.3`
  - `KEY6=TK20/P2.4`
  - `KEY7=TK28/P0.4`
  - `KEY8=TK29/P0.5`
- Channel mask: `0x30FC0000UL`.
- Working threshold example: `0x0190`.
- Known-good IO setup sets the TK-related `P0CON/P2CON` bits and `P0PH/P2PH` bits, then latches the pins high.
- Working scan sequence:

```c
if (SOCAPI_TouchKeyStatus & 0x80) {
    SOCAPI_TouchKeyStatus &= 0x7F;
    g_touch_keys = TouchKeyScan();
    TouchKeyRestart();
    g_touch_scan_count++;
}
```

This sequence corresponds to the Magic Box quick-start flow: initialize TK, wait for scan complete, clear the complete flag, read key information, run user key logic, then start the next conversion with `TouchKeyRestart()`.

The failed intuition was:

```c
P0CON &= (u8)~0x30;
P2CON &= (u8)~0xFC;
g_touch_keys = TouchKeyScan();
SOCAPI_TouchKeyStatus &= 0x7F;
```

That missed the library's IO-bias contract and restart flow.
