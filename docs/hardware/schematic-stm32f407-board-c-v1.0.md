# STM32F407 Board Schematic Working Index

Source PDF:

```text
Schematic_STM32F407开发板-C-V1.0-2606_2026-06-22.pdf
```

This document is the primary working index for firmware pin/peripheral lookup in this workspace. The source PDF remains the reference for electrical details, connector orientation, and any unclear or conflicting mapping.

## PDF Status

- Pages: 1
- Page box: approximately `1652.6 x 1169.6`
- Producer metadata: `jsPDF 0.0.0`
- Creation date metadata: `2026-06-22 20:39:54 +08:00`
- Text extraction: usable for net names and component labels; some Chinese labels are garbled.

## Onboard Peripheral Summary

| Block | Component / connector | MCU signals |
| --- | --- | --- |
| MCU | `STM32F407ZGT6`, reference split as `U4.1`, `U4.2`, `U4.3` | All GPIO and power pins listed below |
| SPI Flash | `W25Q64FWSSIQ`, `U3` | `PA7=Flash-CS`, `PC10=Flash-SCK`, `PC11=Flash-MISO`, `PC12=Flash-MOSI`; WP# and HOLD# tied to +3V3 (write protection disabled); 100nF decoupling (C27) |
| LCD / touch connector | `J2` | `PA15=LCD_SPI3_CS/CSX`, `PC8=LCD_RESET`, `PC9=LCD_DC/WRX`, `PC10=LCD_SPI3_CLK/DCX`, `PC11=LCD_SPI3_MISO`, `PC12=LCD_SPI3_MOSI`, `PA8=T_CLK`, `PA9=T_CS`, `PA10=T_MOSI`, `PA11=T_MISO`, `PA12=T_IRQ`, plus `LCD_BL`; **LCD_BL is not connected to MCU GPIO** (hardware-controlled backlight) |
| USB to serial | `CH340C`, `U1`; USB connector `J5` | `PA2` and `PA3` connect through 1kΩ resistors (R6, R7) to CH340 serial pins; **PA2=USART2_TX**, **PA3=USART2_RX**; USB side exposes `USB_5V`, `D-`, `D+`, `GND` |
| SWD | `J1` | `PA13=SWDIO`, `PA14=SWCLK`, `+3V3`, `GND` |
| Reset | `RST`, `R2`, `C5` | `NRST`; 10kΩ pull-up (R2), 100nF debounce capacitor (C5); RC time constant τ=1ms |
| User LED | `LED1`, `LED2` | `PA5=LED1`, `PA4=LED2`; **Active-High** (GPIO high = LED on); 1kΩ current limiting resistors R9/R10 |
| Power LED | `LED3` | Power indicator, not an MCU GPIO |
| User keys | `KEY1`, `KEY2` | `PA0=KEY1`, `PA1=KEY2`; **Active-Low** with 10kΩ pull-down resistors (R12, R3); requires internal pull-up; pressed = LOW, released = HIGH |
| Buzzer | `BEEP` | `PA6=BEEP`; **Active-Low** (pull LOW to sound); 1kΩ limiting resistor R14; active buzzer connected to +3V3 |
| DHT11 | `U5` | `PC13=DHT11 DATA`; **4.7kΩ pull-up resistor (R13) to +3V3**; single-wire protocol requires GPIO open-drain or push-pull with input switching |
| HSE | `X1 8MHz` | `PH0`, `PH1`; 20pF load capacitors (C1, C2) on each side |
| LSE | `X2 32.768kHz` | `PC14`, `PC15`; 20pF load capacitors (C3, C4) on each side |
| Backup battery | `BT1 CR1220-F DIP` | `VBAT` |
| 5V to 3.3V regulator | `BL8072CLTR33`, `U2` | `USB_5V/+5V` to `+3V3` power path; input capacitor C24 (10µF), output capacitor C25 (1µF); typical output current 200-300mA |

## Board Peripheral Electrical Specifications

### LED Circuit

- **LED1 (PA5)**: Active-High, GPIO high = LED on, GPIO low = LED off
  - Current limiting resistor: R9 = 1kΩ
  - Forward current: ≈1.3mA (assuming Vf=2V)
  - Circuit: `PA5 → R9 (1kΩ) → LED1 → GND`

- **LED2 (PA4)**: Active-High, GPIO high = LED on, GPIO low = LED off
  - Current limiting resistor: R10 = 1kΩ
  - Forward current: ≈1.3mA
  - Circuit: `PA4 → R10 (1kΩ) → LED2 → GND`

### Key Circuit

- **KEY1 (PA0)**: Active-Low, pressed = LOW, released = HIGH
  - Pull-down resistor: R12 = 10kΩ to GND
  - **GPIO configuration required**: Input mode with internal pull-up enabled
  - Switch model: TS-1101-C-W tactile switch
  - Debouncing: Software debounce required (no hardware RC filter)

- **KEY2 (PA1)**: Active-Low, pressed = LOW, released = HIGH
  - Pull-down resistor: 10kΩ to GND
  - **GPIO configuration required**: Input mode with internal pull-up enabled
  - Switch model: TS-1101-C-W tactile switch
  - Debouncing: Software debounce required

### Buzzer Circuit

- **BEEP (PA6)**: Active-Low, pull LOW to sound, HIGH or float to silence
  - Current limiting resistor: R14 = 1kΩ
  - Circuit: `PA6 → R14 (1kΩ) → BEEP (pin 1) → +3V3 (pin 2)`
  - Type: Active buzzer (推测)
  - **GPIO configuration**: Output mode, push-pull, initial HIGH (silent)

### DHT11 Temperature/Humidity Sensor

- **DATA (PC13)**: Single-wire bidirectional protocol
  - Pull-up resistor: R13 = 4.7kΩ to +3V3 (board-mounted)
  - **GPIO configuration**: Open-drain output mode, or push-pull with input switching
  - Protocol timing: Start signal requires ≥18ms LOW pulse
  - Power supply: Direct +3V3, no enable control
  - Decoupling: Check schematic for local capacitor

### W25Q64 SPI Flash

- **SPI signals**:
  - CS: PA7 (active-low chip select)
  - SCK: PC10 (shared with LCD SPI3)
  - MISO: PC11 (shared with LCD SPI3)
  - MOSI: PC12 (shared with LCD SPI3)
- **Clock speed**: Up to 104MHz (software configurable, limited by shared bus requirements)
- **WP# (Write Protect)**: Tied to +3V3 → write protection **permanently disabled**
- **HOLD# (Hold)**: Tied to +3V3 → hold function **permanently disabled**
- **Power supply**: +3V3
- **Decoupling**: C27 = 100nF ceramic capacitor near VCC pin

### LCD/Touch Connector J2

**LCD Control Signals (SPI mode)**:
- CS: PA15 (LCD_SPI3_CS/CSX, active-low)
- RESET: PC8 (LCD_RESET, active-low)
- DC: PC9 (LCD_DC/WRX, data/command select)
- SCK: PC10 (shared with Flash)
- MISO: PC11 (shared with Flash)
- MOSI: PC12 (shared with Flash)
- Backlight: LCD_BL (not connected to MCU GPIO, hardware-controlled)

**Touch Screen Control Signals (independent SPI)**:
- CLK: PA8 (T_CLK)
- CS: PA9 (T_CS, active-low)
- MOSI: PA10 (T_MOSI)
- MISO: PA11 (T_MISO)
- IRQ: PA12 (T_IRQ, interrupt request from touch controller)

**Power supply**: +5V and +3V3 available on J2 connector

**Note**: Touch screen uses independent SPI, no bus conflict with LCD/Flash SPI3.

### CH340C USB-to-Serial Bridge

- **MCU USART**: USART2
  - PA2 = USART2_TX (MCU transmit)
  - PA3 = USART2_RX (MCU receive)
- **Signal path**:
  - TX: `PA2 → R7 (1kΩ) → CH340C RXD (pin 2)`
  - RX: `PA3 ← R6 (1kΩ) ← CH340C TXD (pin 3)`
- **Series resistors**: R6 = R7 = 1kΩ for current limiting and protection
- **Baud rate**: CH340C supports up to 2Mbps
- **USB connector**: J5, USB Mini-B
- **Decoupling**: C22 = 100nF (VCC), C23 = 100nF (V3 pin)

## Pin Selection Guide for Hardware Design

When selecting GPIO pins for external hardware (keypads, sensors, displays), consider **physical pin proximity** on the STM32F407ZGT6 LQFP144 package to minimize PCB routing complexity.

### Pin Groups by Physical Location

Pins are grouped by their physical proximity on the package. Use consecutive pins from the same group for multi-pin interfaces.

**Bottom-Left Corner (pins 1-22)**:
- PE2(1), PE3(2), PE4(3), PE5(4), PE6(5)
- PC13(7), PC14(8), PC15(9)
- PF0(10), PF1(11), PF2(12), PF3(13), PF4(14), PF5(15)
- PF6(18), PF7(19), PF8(20), PF9(21), PF10(22)

**Left Side (pins 26-50)**:
- PC0(26), PC1(27), PC2(28), PC3(29)
- PA0(34), PA1(35), PA2(36), PA3(37)
- PA4(40), PA5(41), PA6(42), PA7(43)
- PC4(44), PC5(45)
- PB0(46), PB1(47), PB2(48)
- PF11(49), PF12(50)

**Top-Left (pins 53-68)**:
- PF13(53), PF14(54), PF15(55)
- PG0(56), PG1(57)
- PE7(58), PE8(59), PE9(60)
- PE10(63), PE11(64), PE12(65), PE13(66), PE14(67), PE15(68)

**Top Side (pins 69-93)**:
- PB10(69), PB11(70)
- PB12(73), PB13(74), PB14(75), PB15(76)
- PD8(77), PD9(78), PD10(79), PD11(80), PD12(81), PD13(82)
- PD14(85), PD15(86)
- PG2(87), PG3(88), PG4(89), PG5(90), PG6(91), PG7(92), PG8(93)

**Top-Right (pins 96-124)**:
- PC6(96), PC7(97), PC8(98), PC9(99)
- PA8(100), PA9(101), PA10(102), PA11(103), PA12(104)
- PA13(105), PA14(109), PA15(110)
- PC10(111), PC11(112), PC12(113)
- PD0(114), PD1(115), PD2(116), PD3(117), PD4(118), PD5(119)
- PD6(122), PD7(123)
- PG9(124)

**Right Side (pins 133-142)**:
- PB3(133), PB4(134), PB5(135), PB6(136), PB7(137)
- PB8(139), PB9(140)
- PE0(141), PE1(142)

### Pin Selection Examples

**Good**: Keypad using PE0(141), PE1(142), PE2(1), PE3(2), PE4(3), PE5(4), PE6(5), PF0(10)
- All 8 pins within 10 positions on bottom-right corner

**Bad**: Keypad using PE0-PE6, PE7(58)
- PE7 is 56 pins away from PE6, requires routing across entire chip side

**Good**: SPI bus using PC10(111), PC11(112), PC12(113)
- 3 consecutive pins

**Good**: I2C + control pins using PB6(136), PB7(137), PB8(139), PB9(140)
- All within 4-pin span

## Complete MCU GPIO Map

Use this table for signal assignment. "Expansion" means the signal is routed to an IO header and no onboard peripheral was identified from the extracted schematic text. Package pin numbers are provided for physical layout reference.

| MCU pin | Package pin | Physical group | Board signal / peripheral |
| --- | ---: | --- | --- |
| `PA0` | 34 | Left-34-43 | `KEY1`; user key |
| `PA1` | 35 | Left-34-43 | `KEY2`; user key |
| `PA2` | 36 | Left-34-43 | CH340 serial path, likely MCU TX to USB-serial bridge RX |
| `PA3` | 37 | Left-34-43 | CH340 serial path, likely MCU RX from USB-serial bridge TX |
| `PA4` | 40 | Left-34-43 | `LED2`; user LED |
| `PA5` | 41 | Left-34-43 | `LED1`; user LED |
| `PA6` | 42 | Left-34-43 | `BEEP`; buzzer |
| `PA7` | 43 | Left-34-43 | `Flash-CS`; W25Q64 chip select |
| `PA8` | 100 | TopRight-96-113 | `T_CLK`; LCD/touch connector `J2` |
| `PA9` | 101 | TopRight-96-113 | `T_CS`; LCD/touch connector `J2` |
| `PA10` | 102 | TopRight-96-113 | `T_MOSI`; LCD/touch connector `J2` |
| `PA11` | 103 | TopRight-96-113 | `T_MISO`; LCD/touch connector `J2` |
| `PA12` | 104 | TopRight-96-113 | `T_IRQ`; LCD/touch connector `J2` |
| `PA13` | 105 | TopRight-96-113 | `SWDIO`; also `JTMS` |
| `PA14` | 109 | TopRight-96-113 | `SWCLK`; also `JTCK` |
| `PA15` | 110 | TopRight-96-113 | `LCD_SPI3_CS/CSX`; also `JTDI` |
| `PB0` | 46 | Left-44-50 | Expansion header `J3` |
| `PB1` | 47 | Left-44-50 | Expansion header `J3` |
| `PB2` | 48 | Left-44-50 | `BOOT1`; expansion header `J3` |
| `PB3` | 133 | Right-133-142 | Expansion header `J4`; also `JTDO/TRACESWO` |
| `PB4` | 134 | Right-133-142 | Expansion header `J4`; also `NJTRST` |
| `PB5` | 135 | Right-133-142 | Expansion header `J4` |
| `PB6` | 136 | Right-133-142 | Expansion header `J4` |
| `PB7` | 137 | Right-133-142 | Expansion header `J4` |
| `PB8` | 139 | Right-133-142 | Expansion header `J4` |
| `PB9` | 140 | Right-133-142 | Expansion header `J4` |
| `PB10` | 69 | Top-69-93 | Expansion header `J3` |
| `PB11` | 70 | Top-69-93 | Expansion header `J3` |
| `PB12` | 73 | Top-69-93 | Expansion header `J3` |
| `PB13` | 74 | Top-69-93 | Expansion header `J3` |
| `PB14` | 75 | Top-69-93 | Expansion header `J3` |
| `PB15` | 76 | Top-69-93 | Expansion header `J3` |
| `PC0` | 26 | Left-26-29 | Expansion header `J4` |
| `PC1` | 27 | Left-26-29 | Expansion header `J4` |
| `PC2` | 28 | Left-26-29 | Expansion header `J4` |
| `PC3` | 29 | Left-26-29 | Expansion header `J4` |
| `PC4` | 44 | Left-44-50 | Expansion header `J3` |
| `PC5` | 45 | Left-44-50 | Expansion header `J3` |
| `PC6` | 96 | TopRight-96-113 | Expansion header `J3` |
| `PC7` | 97 | TopRight-96-113 | Expansion header `J3` |
| `PC8` | 98 | TopRight-96-113 | `LCD_RESET`; LCD connector `J2` |
| `PC9` | 99 | TopRight-96-113 | `LCD_DC/WRX`; LCD connector `J2` |
| `PC10` | 111 | TopRight-96-113 | `LCD_SPI3_CLK/DCX` and `Flash-SCK`; shared SPI clock net |
| `PC11` | 112 | TopRight-96-113 | `LCD_SPI3_MISO` and `Flash-MISO`; shared SPI MISO net |
| `PC12` | 113 | TopRight-96-113 | `LCD_SPI3_MOSI` and `Flash-MOSI`; shared SPI MOSI net |
| `PC13` | 7 | BottomLeft-1-22 | `DHT11 DATA` |
| `PC14` | 8 | BottomLeft-1-22 | `OSC32_IN`; LSE crystal `X2` |
| `PC15` | 9 | BottomLeft-1-22 | `OSC32_OUT`; LSE crystal `X2` |
| `PD0` | 114 | TopRight-114-124 | Expansion header `J4` |
| `PD1` | 115 | TopRight-114-124 | Expansion header `J4` |
| `PD2` | 116 | TopRight-114-124 | Expansion header `J4` |
| `PD3` | 117 | TopRight-114-124 | Expansion header `J4` |
| `PD4` | 118 | TopRight-114-124 | Expansion header `J4` |
| `PD5` | 119 | TopRight-114-124 | Expansion header `J4` |
| `PD6` | 122 | TopRight-114-124 | Expansion header `J4` |
| `PD7` | 123 | TopRight-114-124 | Expansion header `J4` |
| `PD8` | 77 | Top-69-93 | Expansion header `J3` |
| `PD9` | 78 | Top-69-93 | Expansion header `J3` |
| `PD10` | 79 | Top-69-93 | Expansion header `J3` |
| `PD11` | 80 | Top-69-93 | Expansion header `J3` |
| `PD12` | 81 | Top-69-93 | Expansion header `J3` |
| `PD13` | 82 | Top-69-93 | Expansion header `J3` |
| `PD14` | 85 | Top-69-93 | Expansion header `J3` |
| `PD15` | 86 | Top-69-93 | Expansion header `J3` |
| `PE0` | 141 | Right-133-142 | Expansion header `J4` |
| `PE1` | 142 | Right-133-142 | Expansion header `J4` |
| `PE2` | 1 | BottomLeft-1-22 | Expansion header `J4` |
| `PE3` | 2 | BottomLeft-1-22 | Expansion header `J4` |
| `PE4` | 3 | BottomLeft-1-22 | Expansion header `J4` |
| `PE5` | 4 | BottomLeft-1-22 | Expansion header `J4` |
| `PE6` | 5 | BottomLeft-1-22 | Expansion header `J4` |
| `PE7` | 58 | TopLeft-53-68 | Expansion header `J3` |
| `PE8` | 59 | TopLeft-53-68 | Expansion header `J3` |
| `PE9` | 60 | TopLeft-53-68 | Expansion header `J3` |
| `PE10` | 63 | TopLeft-53-68 | Expansion header `J3` |
| `PE11` | 64 | TopLeft-53-68 | Expansion header `J3` |
| `PE12` | 65 | TopLeft-53-68 | Expansion header `J3` |
| `PE13` | 66 | TopLeft-53-68 | Expansion header `J3` |
| `PE14` | 67 | TopLeft-53-68 | Expansion header `J3` |
| `PE15` | 68 | TopLeft-53-68 | Expansion header `J3` |
| `PF0` | 10 | BottomLeft-1-22 | Expansion header `J4` |
| `PF1` | 11 | BottomLeft-1-22 | Expansion header `J4` |
| `PF2` | 12 | BottomLeft-1-22 | Expansion header `J4` |
| `PF3` | 13 | BottomLeft-1-22 | Expansion header `J4` |
| `PF4` | 14 | BottomLeft-1-22 | Expansion header `J4` |
| `PF5` | 15 | BottomLeft-1-22 | Expansion header `J4` |
| `PF6` | 18 | BottomLeft-1-22 | Expansion header `J4` |
| `PF7` | 19 | BottomLeft-1-22 | Expansion header `J4` |
| `PF8` | 20 | BottomLeft-1-22 | Expansion header `J4` |
| `PF9` | 21 | BottomLeft-1-22 | Expansion header `J4` |
| `PF10` | 22 | BottomLeft-1-22 | Expansion header `J4` |
| `PF11` | 49 | Left-44-50 | Expansion header `J3` |
| `PF12` | 50 | Left-44-50 | Expansion header `J3` |
| `PF13` | 53 | TopLeft-53-68 | Expansion header `J3` |
| `PF14` | 54 | TopLeft-53-68 | Expansion header `J3` |
| `PF15` | 55 | TopLeft-53-68 | Expansion header `J3` |
| `PG0` | 56 | TopLeft-53-68 | Expansion header `J3` |
| `PG1` | 57 | TopLeft-53-68 | Expansion header `J3` |
| `PG2` | 87 | Top-69-93 | Expansion header `J3` |
| `PG3` | 88 | Top-69-93 | Expansion header `J3` |
| `PG4` | 89 | Top-69-93 | Expansion header `J3` |
| `PG5` | 90 | Top-69-93 | Expansion header `J3` |
| `PG6` | 91 | Top-69-93 | Expansion header `J3` |
| `PG7` | 92 | Top-69-93 | Expansion header `J3` |
| `PG8` | 93 | Top-69-93 | Expansion header `J3` |
| `PG9` | 124 | TopRight-114-124 | Expansion header `J4` |
| `PG10` | 125 | Expansion header `J4` |
| `PG11` | 126 | Expansion header `J4` |
| `PG12` | 127 | Expansion header `J4` |
| `PG13` | 128 | Expansion header `J4` |
| `PG14` | 129 | Expansion header `J4` |
| `PG15` | 132 | Expansion header `J4` |
| `PH0` | 23 | `OSC_IN`; HSE crystal `X1 8MHz` |
| `PH1` | 24 | `OSC_OUT`; HSE crystal `X1 8MHz` |

## Expansion Header Grouping

The extracted schematic text shows two main GPIO expansion headers. Use this as a signal grouping index; verify physical pin numbering from the PDF before wiring.

| Header | Signals |
| --- | --- |
| `J3` | `PC4`, `PC5`, `PB0`, `PB1`, `PB2`, `PF11`, `PF12`, `PF13`, `PF14`, `PF15`, `PG0`, `PG1`, `PE7`, `PE8`, `PE9`, `PE10`, `PE11`, `PE12`, `PE13`, `PE14`, `PE15`, `PB10`, `PB11`, `PB12`, `PB13`, `PB14`, `PB15`, `PD8`, `PD9`, `PD10`, `PD11`, `PD12`, `PD13`, `PD14`, `PD15`, `PG2`, `PG3`, `PG4`, `PG5`, `PG6`, `PG7`, `PG8`, `PC6`, `PC7`, plus power nets |
| `J4` | `PC3`, `VREF`, `PC1`, `PC2`, `NRST`, `PC0`, `PF9`, `PF10`, `PF7`, `PF8`, `PF5`, `PF6`, `PF3`, `PF4`, `PF1`, `PF2`, `PE6`, `PF0`, `PE4`, `PE5`, `PE2`, `PE3`, `PE0`, `PE1`, `PB8`, `PB9`, `PB6`, `PB7`, `PB4`, `PB5`, `PG15`, `PB3`, `PG13`, `PG14`, `PG11`, `PG12`, `PG9`, `PG10`, `PD6`, `PD7`, `PD4`, `PD5`, `PD2`, `PD3`, `PD0`, `PD1`, plus power nets |

## Special Nets And Power Pins

| Net / pin | Meaning |
| --- | --- |
| `NRST` | Reset net; reset button circuit and expansion header |
| `BOOT0` | Boot mode pin, 10kΩ pull-down resistor (R4) to GND; also exposed on J4 expansion header for jumper override |
| `BOOT1` / `PB2` | Boot mode related pin, 10kΩ pull-down resistor (R3) to GND; also routed to expansion |
| `VBAT` | Backup battery input from `BT1` (CR1220, 3V lithium coin cell, ~40mAh); powers RTC, backup registers, and backup SRAM (4KB) when VDD is absent |
| `VREF` / `VREF+` | Analog reference net; derived from VDDA through diode D1; 2.2µF decoupling (C8); also exposed on J4 pin 2 for external use |
| `VDDA`, `VSSA` | Analog supply and ground; filtered via L1 (600Ω@100MHz ferrite bead) and C21/C26 (100nF each) |
| `VCAP_1`, `VCAP_2` | Core regulator capacitor pins; each requires C6/C7 = 2.2µF ±10% ceramic capacitor with ESR <1Ω |
| `PDR_ON` | Power-down reset control pin; left floating (not connected) |
| `USB_5V`, `+5V`, `+3V3`, `GND` | Main power nets |

## Boot Mode Configuration

### Boot Pin Default States

- **BOOT0 (pin 138)**: 10kΩ pull-down to GND (R4) → default LOW
- **BOOT1 / PB2 (pin 48)**: 10kΩ pull-down to GND (R3) → default LOW

### Boot Mode Truth Table

| BOOT0 | BOOT1 (PB2) | Boot Mode | Memory Start Address | Use Case |
|:-----:|:-----------:|-----------|:--------------------:|----------|
| 0 (GND) | X (any) | **Main Flash Memory** | 0x0800 0000 | Normal operation |
| 1 (VDD) | 0 (GND) | **System Memory (ISP)** | 0x1FFF 0000 | Bootloader for firmware upload via USART/USB |
| 1 (VDD) | 1 (VDD) | **Embedded SRAM** | 0x2000 0000 | Debug/testing (code runs from RAM) |

**Default behavior**: Board boots from main Flash (user application) on power-up or reset.

**Entering ISP mode**: Connect BOOT0 to +3V3 via jumper on J4 expansion header before reset.

## Power System Architecture

### Power Supply Chain

```
USB_5V (J5 USB connector or external +5V input)
  ↓
BL8072CLTR33 (U2) LDO Regulator
  Input: C24 = 10µF
  Output: C25 = 1µF
  Max current: 200-300mA (typical)
  ↓
+3V3 (3.3V main power rail)
  ├→ VDD (digital supply, 11 pins)
  │   └→ C9-C20: 100nF decoupling per pin
  │
  ├→ L1 (600Ω@100MHz ferrite bead) → VDDA (analog supply)
  │   ├→ C21, C26 (100nF each)
  │   └→ D1 → VREF+ (pin 32)
  │       └→ C8 (2.2µF)
  │
  ├→ VCAP_1 (pin 71) → C6 (2.2µF) → GND
  ├→ VCAP_2 (pin 106) → C7 (2.2µF) → GND
  │
  └→ Peripherals (Flash, DHT11, CH340C, etc.)

VBAT (pin 6) ← CR1220 backup battery (3V)
  └→ RTC + Backup Domain
```

### VDD Digital Supply Decoupling

All 11 VDD pins (pins 17, 30, 39, 52, 62, 72, 84, 95, 108, 121, 131, 144) are decoupled with dedicated 100nF ceramic capacitors (C9-C20) placed close to the MCU package.

### VDDA Analog Supply Filtering

- **Ferrite bead**: L1 = 600Ω @ 100MHz (isolates analog supply from digital noise)
- **Decoupling**: C21 || C26 = 100nF + 100nF
- **VREF+ generation**: VDDA → Diode D1 → VREF+ (pin 32) → C8 (2.2µF)
  - Diode D1 provides single-direction protection
  - VREF+ is also exposed on J4 expansion header pin 2 for external ADC reference

### Internal Regulator Capacitors

- **VCAP_1 (pin 71)**: C6 = 2.2µF ±10%, ESR <1Ω
- **VCAP_2 (pin 106)**: C7 = 2.2µF ±10%, ESR <1Ω
- **Requirement**: STM32F407 datasheet mandates 2.2µF ceramic capacitors on both VCAP pins for internal voltage regulator stability

### Backup Battery

- **Model**: CR1220 lithium coin cell (BT1)
- **Voltage**: 3V nominal
- **Capacity**: ~40mAh
- **Function**: Maintains power to:
  - RTC (Real-Time Clock) for continuous timekeeping
  - Backup registers (20 x 32-bit)
  - Backup SRAM (4KB)
- **Automatic switchover**: VBAT powers backup domain when VDD drops below threshold

### Power Indicator

- **LED3**: Power-on indicator, connected to +3V3 via R8 (1kΩ), always on when +3V3 is present

## Clock System Configuration

### HSE (High-Speed External Oscillator)

- **Crystal**: X1, 8MHz
- **MCU pins**: PH0 (OSC_IN, pin 23), PH1 (OSC_OUT, pin 24)
- **Load capacitors**: C1 = C2 = 20pF to GND
- **Effective load capacitance**: CL ≈ 12-15pF (including PCB stray capacitance)
- **Firmware requirement**: Define `HSE_VALUE 8000000` in `system_stm32f4xx.c`

### LSE (Low-Speed External Oscillator)

- **Crystal**: X2, 32.768kHz (standard RTC frequency)
- **MCU pins**: PC14 (OSC32_IN, pin 8), PC15 (OSC32_OUT, pin 9)
- **Load capacitors**: C3 = C4 = 20pF to GND
- **Effective load capacitance**: CL ≈ 12-15pF
- **Use case**: RTC clock source for calendar and wakeup functions

## SPI Bus Sharing and Arbitration

### SPI3 Shared Bus (PC10/PC11/PC12)

**Shared signals**:
- SCK: PC10 (SPI3_SCK)
- MISO: PC11 (SPI3_MISO)
- MOSI: PC12 (SPI3_MOSI)

**Connected devices**:

| Device | CS Signal | Max Clock | Notes |
|--------|-----------|-----------|-------|
| W25Q64 Flash (U3) | PA7 (Flash-CS) | 104MHz | Board-mounted |
| LCD Module (J2) | PA15 (LCD_SPI3_CS) | 10-50MHz | Connector, speed depends on LCD model |

### Arbitration Rules

1. **Chip Select Mutual Exclusion**:
   - Only ONE CS signal may be LOW at any time
   - Before asserting target CS, ensure all other CS signals are HIGH
   - Add small delay (1-10µs) between CS transitions for signal settling

2. **Clock Speed Compatibility**:
   - W25Q64 supports up to 104MHz
   - LCD controller typically limits to 10-50MHz (check specific LCD datasheet)
   - **Recommended approach**: Configure SPI clock to ≤10MHz for safety, or dynamically reconfigure SPI prescaler when switching devices

3. **MISO Bus Contention Prevention**:
   - Non-selected SPI devices must tri-state their MISO output (high-impedance)
   - W25Q64 automatically tri-states MISO when CS# is HIGH ✓
   - LCD controller behavior depends on specific model (verify datasheet)

4. **Firmware Best Practices**:
   ```c
   // Switch to Flash
   GPIO_SetBits(GPIOA, GPIO_Pin_15);   // LCD CS = HIGH
   delay_us(1);                         // Settling time
   GPIO_ResetBits(GPIOA, GPIO_Pin_7);  // Flash CS = LOW
   spi_transfer(...);
   GPIO_SetBits(GPIOA, GPIO_Pin_7);    // Flash CS = HIGH
   
   // Switch to LCD
   GPIO_SetBits(GPIOA, GPIO_Pin_7);    // Flash CS = HIGH
   delay_us(1);                         // Settling time
   GPIO_ResetBits(GPIOA, GPIO_Pin_15); // LCD CS = LOW
   spi_transfer(...);
   GPIO_SetBits(GPIOA, GPIO_Pin_15);   // LCD CS = HIGH
   ```

5. **Potential Conflicts**:
   - ⚠️ If LCD module is disconnected or CS not properly pulled high, Flash communication may fail
   - ⚠️ CPOL/CPHA (SPI mode) must be compatible for both devices:
     - W25Q64: Mode 0 (CPOL=0, CPHA=0) or Mode 3 (CPOL=1, CPHA=1)
     - LCD: Check specific controller datasheet (e.g., ILI9341 uses Mode 0 or Mode 3)

## Reset Circuit

**Circuit topology**:
```
+3V3 → R2 (10kΩ) → NRST (pin 25)
                      ↓
              RST button → GND
                      ↓
                  C5 (100nF) → GND
```

**Component values**:
- Pull-up resistor: R2 = 10kΩ
- Debounce capacitor: C5 = 100nF
- RC time constant: τ = R × C = 10kΩ × 100nF = **1ms**

**Operation**:
- Normal state: NRST pulled HIGH to +3V3 (MCU running)
- Button pressed: NRST shorted to GND (MCU in reset)
- Button released: NRST rises exponentially with time constant τ
- MCU exits reset when NRST exceeds VIH threshold (~2.0V) after ~0.7τ ≈ 0.7ms

**Debouncing**: C5 filters mechanical bounce and electrical noise on NRST line.

## Expansion Connector Physical Specifications

### J3 Expansion Header

- **Connector model**: KH-2.54PH180-2X24P-L11.5
- **Total pins**: 48 (2 rows × 24 columns)
- **Pin pitch**: 2.54mm (0.1 inch)
- **Orientation**: 180° through-hole vertical
- **Pin height**: 11.5mm
- **Pin layout**: Odd pins (1, 3, 5...47) on one row, even pins (2, 4, 6...48) on opposite row

**GPIO signals**: See "Expansion Header Grouping" table below for complete pin list.

**Power pins**: +5V, +3V3, GND distributed on J3 (exact positions require visual inspection of schematic PDF or physical board).

### J4 Expansion Header

- **Connector model**: PH2.54-01-25PZS
- **Total pins**: 50 (2 rows × 25 columns)
- **Pin pitch**: 2.54mm (0.1 inch)
- **Orientation**: Through-hole vertical

**Special signals**:
- **Pin 2**: VREF+ (analog reference voltage output from MCU)
- **Pin 5**: NRST (reset signal, can be driven externally to reset MCU)

**Power pins**: +5V, +3V3, GND distributed on J4.

**GPIO signals**: See "Expansion Header Grouping" table below for complete pin list.

## Firmware Initialization Checklist

When developing firmware for this board, verify the following configurations:

### Clock Configuration
- [ ] HSE configured as 8MHz external crystal (`RCC_HSE_ON`, not `RCC_HSE_Bypass`)
- [ ] System clock PLL configured to derive from HSE (typical: 8MHz × PLL → 168MHz SYSCLK)
- [ ] `HSE_VALUE` defined as `8000000` in `system_stm32f4xx.c` or build settings
- [ ] LSE enabled if RTC is used (PC14/PC15, 32.768kHz)

### GPIO Peripheral Configuration
- [ ] **LED1 (PA5)**: Output, push-pull, initial LOW (LED off)
- [ ] **LED2 (PA4)**: Output, push-pull, initial LOW (LED off)
- [ ] **KEY1 (PA0)**: Input, pull-up enabled (reads HIGH when released)
- [ ] **KEY2 (PA1)**: Input, pull-up enabled (reads HIGH when released)
- [ ] **BEEP (PA6)**: Output, push-pull, initial HIGH (buzzer silent)
- [ ] **DHT11 (PC13)**: Open-drain output or push-pull with input switching, no pull resistor needed (hardware R13 = 4.7kΩ)
- [ ] **Flash CS (PA7)**: Output, push-pull, initial HIGH (deselected)
- [ ] **LCD CS (PA15)**: Output, push-pull, initial HIGH (deselected)
- [ ] **LCD RESET (PC8)**: Output, push-pull, initial HIGH (not in reset)
- [ ] **LCD DC (PC9)**: Output, push-pull
- [ ] **Touch CS (PA9)**: Output, push-pull, initial HIGH (deselected)
- [ ] **Touch IRQ (PA12)**: Input, pull-up or floating (depends on touch controller)

### SPI3 Configuration (Flash & LCD)
- [ ] PC10 configured as SPI3_SCK alternate function (AF6)
- [ ] PC11 configured as SPI3_MISO alternate function (AF6)
- [ ] PC12 configured as SPI3_MOSI alternate function (AF6)
- [ ] SPI3 clock speed initially set to ≤10MHz for LCD compatibility
- [ ] SPI3 mode configured (check Flash and LCD datasheets for CPOL/CPHA)

### Touch SPI Configuration (Independent)
- [ ] PA8 configured as GPIO output (T_CLK, bit-bang SPI) or SPI1_SCK if using hardware SPI
- [ ] PA10 configured as GPIO output (T_MOSI) or SPI1_MOSI
- [ ] PA11 configured as GPIO input (T_MISO) or SPI1_MISO

### USART2 Configuration (CH340C USB-Serial)
- [ ] PA2 configured as USART2_TX alternate function (AF7)
- [ ] PA3 configured as USART2_RX alternate function (AF7)
- [ ] USART2 baud rate configured (common: 115200, 9600)

### Power and Clock Verification
- [ ] Verify +3V3 power rail voltage with multimeter (~3.3V ±5%)
- [ ] Check HSE startup in `RCC->CR` register (`HSERDY` bit set)
- [ ] Verify system clock frequency with output on MCO pin or timer measurement

## Special Nets And Power Pins

| Net / pin | Meaning |
| --- | --- |
| `NRST` | Reset net; reset button circuit and expansion header |
| `BOOT0` | Boot mode pin, pulled by onboard resistor network |
| `BOOT1` / `PB2` | Boot mode related pin, also routed to expansion |
| `VBAT` | Backup battery input from `BT1` |
| `VREF` / `VREF+` | Analog reference net |
| `VDDA`, `VSSA` | Analog supply and ground |
| `VCAP_1`, `VCAP_2` | Core regulator capacitor pins |
| `PDR_ON` | Power-down reset control pin |
| `USB_5V`, `+5V`, `+3V3`, `GND` | Main power nets |

## Known Caveats and Design Notes

### SPI Bus Sharing
- **PC10, PC11, and PC12** are shared by the LCD SPI signals and the W25Q64 Flash SPI signals, with separate chip-select signals (PA15 for LCD, PA7 for Flash).
- **Critical**: Both devices must be compatible with the same SPI clock polarity/phase (CPOL/CPHA). Verify from datasheets before enabling both peripherals.
- **Best practice**: Always ensure the non-active device has its CS line HIGH before activating the other device. Add 1-10µs delay between CS transitions.
- **Clock speed**: Limit SPI3 clock to the slower device's maximum (typically LCD at 10-50MHz). Flash supports up to 104MHz but will be constrained by the shared bus.

### Flash Write Protection Permanently Disabled
- W25Q64's **WP# pin is tied to +3V3**, meaning write protection is permanently disabled at the hardware level.
- Software cannot enable block write protection even if desired.
- **Implication**: Extra care needed in firmware to prevent accidental Flash erasure during power glitches or firmware bugs.

### LED Active Level Confirmed
- **LED1 (PA5)** and **LED2 (PA4)** are **active-high**: GPIO output HIGH turns LED on.
- Circuit topology: `GPIO → 1kΩ resistor → LED anode → cathode → GND`
- Forward current is approximately 1.3mA, which is low-brightness but sufficient for indicator LEDs.

### Key Active Level Requires Pull-Up
- **KEY1 (PA0)** and **KEY2 (PA1)** have **10kΩ pull-down resistors to GND**.
- GPIO must be configured with **internal pull-up enabled** to read HIGH when button is released.
- **Pressed state**: GPIO reads LOW (button connects GPIO to GND)
- **Released state**: GPIO reads HIGH (internal pull-up overcomes external pull-down)
- **No hardware debounce**: Firmware must implement software debouncing (typically 10-50ms delay or state machine).

### Buzzer Active-Low Drive
- **BEEP (PA6)** is **active-low**: Pull GPIO LOW to make sound.
- Circuit: `PA6 → 1kΩ → BEEP → +3V3`
- When PA6 is LOW, current flows from +3V3 through buzzer to PA6 (sink current).
- When PA6 is HIGH or floating, minimal current flows (buzzer silent).
- **Active buzzer type** (推测): Does not require PWM; simple HIGH/LOW control produces fixed-frequency tone.

### DHT11 Hardware Pull-Up Present
- **R13 = 4.7kΩ** pull-up resistor is present on the board, connecting PC13 to +3V3.
- Firmware does **not** need to enable internal pull-up on PC13.
- Configure PC13 as **open-drain output** for cleanest DHT11 protocol implementation, or use push-pull with direction switching.

### LCD Backlight Control Not Software-Controllable
- **LCD_BL** signal on J2 connector is **not connected to any MCU GPIO**.
- Backlight is likely controlled by hardware jumper or always-on.
- If PWM dimming is needed, consider external modification or using an available expansion GPIO with MOSFET circuit.

### CH340C USB-Serial Bridge Connections Verified
- **PA2 = USART2_TX** (MCU transmit to PC)
- **PA3 = USART2_RX** (MCU receive from PC)
- 1kΩ series resistors (R6, R7) provide short-circuit protection.
- CH340C maximum baud rate: 2Mbps (though typical USART use cases are 9600-921600 baud).
- **Driver required**: Windows/Linux/macOS need CH340 USB driver installed.

### VREF+ Exported to J4 Expansion Header
- **VREF+ (pin 32)** is derived from VDDA through diode D1 and exposed on J4 pin 2.
- Can be used as external ADC reference voltage source.
- **Do not** drive VREF+ from external source; diode D1 provides single-direction protection but reverse current should be avoided.

### BOOT0 Default State and ISP Mode Entry
- **BOOT0** has 10kΩ pull-down (R4), default state is LOW → boots from Flash.
- To enter **System Memory (ISP bootloader)** for firmware upload:
  1. Power off board or hold RESET
  2. Connect BOOT0 to +3V3 via jumper on J4 expansion header
  3. Release RESET or power on
  4. MCU boots into built-in USART/USB bootloader
  5. After programming, remove jumper and reset again

### Crystal Load Capacitors
- **HSE (8MHz)**: C1 = C2 = 20pF gives effective load capacitance ~12-15pF
- **LSE (32.768kHz)**: C3 = C4 = 20pF gives effective load capacitance ~12-15pF
- These values are typical and should work with most standard crystals. If clock stability issues occur, verify crystal datasheet's specified load capacitance and adjust if needed.

### USB_5V and +3V3 Current Limits
- **USB_5V**: Limited by USB host port (typically 500mA for USB 2.0)
- **+3V3 regulator (BL8072CLTR33)**: Typical maximum 200-300mA (verify datasheet for exact spec)
- **Total board consumption estimation**:
  - STM32F407ZGT6 @ 168MHz: ~50-80mA
  - W25Q64 active: ~15mA
  - LCD backlight (if always-on): 20-100mA depending on module
  - LEDs, DHT11, etc.: ~10mA
  - **Design headroom**: Keep total draw under 200mA for safe operation from USB power

### Expansion Header Power Pin Locations
- Power pins (+5V, +3V3, GND) are distributed on J3 and J4 expansion headers.
- **Exact pin numbering not confirmed from text extraction** — visually inspect schematic PDF page 1 or physical board silkscreen before wiring external modules.
- **ESD protection**: No explicit ESD diodes visible on expansion GPIO pins; handle boards with ESD precautions.

### SWD Debug Interface
- **PA13 (SWDIO)** and **PA14 (SWCLK)** are dedicated to SWD debug interface (J1 connector).
- These pins also serve JTAG functions (JTMS, JTCK) but JTAG is typically disabled by default in STM32F4.
- **PA15 (JTDI)** is used for LCD CS — if JTAG debug is needed, LCD cannot be used simultaneously without remapping.
- **PB3 (JTDO)**, **PB4 (NJTRST)** are routed to J4 expansion — same conflict applies.

### Reset Circuit Behavior
- RC time constant τ = 1ms means NRST rises to ~63% of VDD in 1ms, ~99% in 5ms.
- MCU exits reset when NRST crosses VIH threshold (~0.7×VDD ≈ 2.3V), typically within 0.7-1ms after button release.
- If external circuit drives NRST through J4 expansion header, ensure it doesn't conflict with onboard pull-up R2.

### VCAP Capacitor Requirements
- **C6 and C7 must be 2.2µF ±10% ceramic capacitors with ESR <1Ω**.
- Using incorrect capacitance or high-ESR capacitors can cause core voltage instability and erratic MCU behavior.
- If replacing capacitors, use X5R or X7R dielectric (Y5V dielectric has poor temperature stability).

### Temperature and Environmental Limits
- Board designed for typical lab/indoor use (~0-50°C).
- DHT11 sensor operating range: -20 to 60°C, 5-95% RH (verify from DHT11 datasheet).
- No conformal coating visible — not suitable for harsh industrial environments without additional protection.

### Chinese Schematic Labels
- Some component labels and net names in the PDF have garbled Chinese text due to font encoding issues during PDF export.
- Use English net names and component designators (R1, C1, PA0, etc.) for unambiguous reference.
- When in doubt, cross-reference with physical board silkscreen or component placement.

### Potential Design Improvements (for custom PCB revisions)
- Add a GPIO-controlled MOSFET for LCD backlight PWM dimming
- Add hardware debounce RC filters on KEY1/KEY2 (10kΩ + 100nF = 1ms)
- Add ESD protection diodes on expansion headers
- Add solder jumper to enable/disable W25Q64 write protection via WP# pin
- Expose additional USART ports (USART1, USART3) on expansion headers for multi-serial applications

## Quick Search Keywords

```text
PA0 PA1 PA2 PA3 PA4 PA5 PA6 PA7 PA8 PA9 PA10 PA11 PA12 PA13 PA14 PA15
PB0 PB1 PB2 PB3 PB4 PB5 PB6 PB7 PB8 PB9 PB10 PB11 PB12 PB13 PB14 PB15
PC0 PC1 PC2 PC3 PC4 PC5 PC6 PC7 PC8 PC9 PC10 PC11 PC12 PC13 PC14 PC15
PD0 PD1 PD2 PD3 PD4 PD5 PD6 PD7 PD8 PD9 PD10 PD11 PD12 PD13 PD14 PD15
PE0 PE1 PE2 PE3 PE4 PE5 PE6 PE7 PE8 PE9 PE10 PE11 PE12 PE13 PE14 PE15
PF0 PF1 PF2 PF3 PF4 PF5 PF6 PF7 PF8 PF9 PF10 PF11 PF12 PF13 PF14 PF15
PG0 PG1 PG2 PG3 PG4 PG5 PG6 PG7 PG8 PG9 PG10 PG11 PG12 PG13 PG14 PG15
PH0 PH1 NRST BOOT0 BOOT1 SWDIO SWCLK W25Q64 Flash-CS Flash-SCK Flash-MISO Flash-MOSI
LCD_SPI3_CS/CSX LCD_RESET LCD_DC/WRX LCD_SPI3_CLK/DCX LCD_SPI3_MISO LCD_SPI3_MOSI
T_CLK T_CS T_MOSI T_MISO T_IRQ LED1 LED2 KEY1 KEY2 BEEP DHT11 CH340C USB_5V
```
