# SinOne SC95F861xB Firmware Notes

Source basis: `SC95F8617B_8616B_8615B_8613B_8612Bv1.0cn.pdf`, checked by text extraction plus rendered page images.

## GPIO

- `PxCON` controls direction. `PxCy = 1` is strong push-pull output. `PxCy = 0` is input.
- `PxPH` controls pull-up only when the pin is in input mode. `PxHy = 1` enables pull-up; `PxHy = 0` is floating/input-only.
- Reset values are generally zero, so pins default to input/floating unless firmware or option configuration changes them.
- For alternate-function pins, do not infer the final electrical state from generic GPIO rules alone. Vendor libraries can require a latch/bias state before the peripheral takes over.

## Clock And Timing

- Internal HRC default is 32 MHz at nominal conditions.
- System clock divider comes from Code Option `SCLKS[1:0]`: `00=HRC/1`, `01=HRC/2`, `10=HRC/4`, `11=HRC/8`.
- Firmware constants such as `SYS_CLOCK_HZ`, timer reloads, UART baud generators, and TWI `TWCK` must match Code Option clock selection.
- TK/PWM peripheral timing can depend on HRC. Do not change clock options without retesting touch thresholds and scan period.

## Interrupts

- Global interrupt enable is `EA`.
- Timer0 overflow uses vector address `000BH`, C51 interrupt number `1`, and enable bit `IE.1` (`ET0`). Timer0 `TF0` is hardware-cleared on interrupt entry.
- TK interrupt uses `IE1.4` (`ETK`), vector address `005BH`, C51 interrupt number `11`, flag `TKIF`.
- TK flag is hardware auto-cleared on interrupt entry, but the vendor library still has its own scan-complete status bit.
- UART0 `RI/TI` and USCI `SPIF/TWIF` are not automatically cleared by the application flow; clear them in software according to the peripheral section.
- USCI interrupt enables live across `IE1/IE2`: USCI0 in `IE1`, USCI1~5 in `IE2`.

## Timer0 Buzzer Pattern

For a passive buzzer that needs a 4 kHz tone on a GPIO pin, Timer0 mode 1 can generate a half-period interrupt and the ISR can toggle only the buzzer bit.

- Use `SYS_CLOCK_HZ` that matches the SC95 Code Option clock divider. For the common display-board setting `SYS_CLOCK_HZ = 32000000UL`, a 4 kHz square wave has a 125 us half-period.
- With `TMCON.0 T0FD = 1`, Timer0 counts from `fSYS`; half-period counts are `32000000 / (4000 * 2) = 4000`.
- Timer0 16-bit reload for that half-period is `65536 - 4000 = 0xF060`, so load `TH0=0xF0`, `TL0=0x60` on start and in the Timer0 ISR.
- Configure Timer0 as timer mode 1 with `TMOD = (TMOD & ~0x0F) | 0x01`, set `TMCON |= 0x01`, enable `ET0`, then set `TR0`.
- If the buzzer shares a GPIO port with another timing-sensitive signal, such as `BUZ=P3.1` and AiP1624 `STB=P3.2`, define an `sbit` for the buzzer and toggle that bit only. Do not use whole-port operations such as `P3 ^= 0x02`, because read-modify-write on the shared port can disturb display/control lines and cause visible flicker.
- On stop, clear `TR0` and `ET0`, then drive the buzzer bit to the inactive level.

## UART0

- UART0 is the 8051-style serial port: `SCON`, `SBUF`, `PCON.SMOD`, `RI`, `TI`, `REN`.
- Mode 1 is the normal 8N1-style asynchronous mode: set `SM0/SM1 = 01` and `REN = 1` when receiving.
- Baud rate can come from Timer1 or Timer2/3/4 depending on `TCLK/RCLK`.
- `SBUF` write starts transmit; read returns the receive latch. Clear `TI` after transmit and clear `RI` after receive.

## USCI Selection

- There are six USCI blocks. Each can be selected as SPI, TWI, or UART through `USMDn[1:0]`: `00=off`, `01=SPI`, `10=TWI`, `11=UART`.
- USCI0 and USCI1 have dedicated register addresses.
- USCI2~5 share `USXCON0~3`; set `USXINX[2:0]` first: `010=USCI2`, `011=USCI3`, `100=USCI4`, `101=USCI5`. Accessing `USXCON*` before selecting the pointer writes the wrong interface.
- The same register addresses hold mode-specific meanings. Re-check `USMDn` before interpreting `USnCONx`.

## SPI Through USCI

- Enable SPI with `SPEN=1`; choose master/slave with `MSTR`.
- Set `CPOL/CPHA` to match the external device's SPI mode.
- `SPR[2:0]` selects clock divider from `fSYS` down to `/128`.
- `DORD` selects bit order. Use MSB first unless the device datasheet says otherwise.
- For 16-bit SPI, write high byte before low byte; low-byte write starts transfer.
- `SPIF` indicates transfer complete. `WCOL` means write collision and must be cleared by software.
- USCI0 SPI has stronger output drive and FIFO behavior; do not assume USCI1~5 are identical.

## TWI / I2C Through USCI

- TWI mode uses `USTXn` as SDA and `USCKn` as SCL. The bus idles high and needs pull-ups.
- Enable with `TWEN=1`. `TWIF` is the event/interrupt flag and must be cleared by software.
- `STA=1` generates START and switches to master mode. `STO=1` generates STOP. After STOP, master `TWIF` does not set again.
- `TWCK[3:0]` sets master clock: `0000=fSYS/1024`, `0001=/512`, `0010=/256`, `0011=/128`, `0100=/64`, `0101=/32`, `0110=/16`; other values are reserved. Max TWI clock is 400 kHz.
- For master transmit: select TWI mode, enable `TWEN`, set `TWCK` and `STA`, write `(addr << 1) | 0` to `TWDAT`, wait `TWIF`, then write data bytes and wait/clear `TWIF` each byte.
- For master receive: write `(addr << 1) | 1`, set `AA=1` for bytes that should be ACKed, set `AA=0` before the last byte so the master returns NACK, then issue STOP.
- Use timeouts around every `TWIF` wait; a missing slave ACK otherwise locks firmware.

## TK Touch

- SC95F861xB TK supports up to 31 channels. Datasheet gives the hardware capability; practical channel setup is in the vendor TKDriver/app manual.
- TK9 and TK11 are shared with TK debug communication pins; avoid them when the debug interface is needed.
- For the display-board spring keys, working evidence uses:
  - `SOCAPI_SET_TOUCHKEY_CHANNEL 0x30FC0000UL`
  - `SOCAPI_SET_TOUCHKEY_TOTAL 8`
  - threshold `0x0190`
  - TK pins `P0.4/P0.5/P2.2~P2.7` with `P0CON/P2CON` bits set, `P0PH/P2PH` bits set, and latches high before scan.
- Correct service flow:

```c
if (SOCAPI_TouchKeyStatus & 0x80) {
    SOCAPI_TouchKeyStatus &= 0x7F;
    keys = TouchKeyScan();
    TouchKeyRestart();
}
```

Missing `TouchKeyRestart()` or changing the IO-bias setup can make all springs appear dead even when the interrupt fires.
