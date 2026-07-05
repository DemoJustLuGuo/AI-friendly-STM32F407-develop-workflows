# Firmware Design From Hardware Evidence

Use this reference when a schematic/PCB investigation must become embedded firmware design. Keep conclusions evidence-led: every firmware feature should point back to a net, component chain, connector, local label, or PCB clue.

## Required Output Tables

### MCU Pin Configuration

| MCU pin | Net | Evidence | Firmware mode | Reset/safe state | Active polarity | Driver/sensor chain | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |

Rules:
- Include every MCU pin found by `port_inventory.py`, even if the function is unknown.
- Use `Input`, `Output`, `ADC`, `PWM`, `Timer capture`, `UART`, `I2C`, `SPI`, `Interrupt`, or `NC/Reserved`.
- For actuator outputs, state the safe reset level before peripherals are initialized.
- For feedback inputs, state expected electrical level/range and filtering/debounce.

### External Port / Connector Function

| Connector | Pin | Net | Evidence chain | Probable external device | Firmware responsibility | Test method |
| --- | --- | --- | --- | --- | --- | --- |

Rules:
- Do not name the external device from a connector name alone. Confirm by nearby labels, PCB silkscreen, cable grouping, load driver, protection, or repeated topology.
- Mark board-only pads, jumpers, debug headers, and programming ports separately from user/application ports.

### Control And Fault Matrix

| Function | Output signal | Feedback signal | Enable condition | Fault condition | Firmware reaction | Evidence |
| --- | --- | --- | --- | --- | --- | --- |

Include:
- Actuators: relay, pump, fan, motor, valve, heater, buzzer, LED, power-enable.
- Sensors: NTC, voltage/current sample, water/level switch, tach/FG, zero-cross, keys, communication status.
- Protection: over-current, open/short sensor, timeout, stalled fan/motor, brownout, communication loss, over-temperature.

## Reasoning Checklist

1. Start from MCU pins and external connectors, then meet in the middle through drivers/sensors.
2. Trace each actuator output to the final load side or isolated domain; do not stop at the first transistor/opto/relay.
3. Trace each sensor input back to its real-world source or connector; do not stop at the divider/filter.
4. Confirm active polarity from transistor orientation, optocoupler LED direction, pull-up/pull-down, relay coil diode, and supply rail.
5. Confirm whether PWM is real PWM, analog VSP, timer capture, or just an on/off GPIO by topology and MCU alternate function.
6. Use PCB evidence when the schematic function is unclear: connector placement, silkscreen, wide traces, high-voltage clearance, thermal/load areas, and grouped routing.
7. If local labels or Chinese annotations exist near the net, render/crop the region with `render_region.py` and cite what the image supports.
8. Separate confirmed facts from likely firmware behavior. Never turn a likely hardware interpretation into a hard software requirement.

## Coverage Gate

Before finalizing a firmware document:
- Run `port_inventory.py`.
- Run `coverage_report.py` on the resulting JSON.
- Confirm every MCU pin appears in the MCU pin table.
- Confirm every schematic connector and PCB-only port appears in the connector table or in an explicit `not firmware related / mechanical / power only` list.
- Any pin/net not understood must be marked `待确认`, with the next evidence needed.

Useful coverage metrics:
- MCU pins total / connected / power-reset-debug / firmware-relevant / unknown.
- Schematic connectors total and pins total.
- PCB ports total and pads total.
- Suspicious nets found from names such as `FG`, `VSP`, `PWM`, `AD`, `SW`, `PUMP`, `RELAY`, `TX`, `RX`, `SCL`, `SDA`.

## Reverse Verification

For every named function, verify it from both directions:
- MCU output -> resistor/driver/opto/relay/contact/connector/load.
- External input -> connector/sensor/filter/protection/pull-up/down -> MCU pin.
- Feedback -> real source or connector -> shaping/filtering -> MCU timer/ADC/GPIO.
- Communication -> connector/transceiver/pull-ups/ESD -> MCU peripheral pins.
- Power enable -> MCU/driver -> regulator enable or switched rail -> downstream load.

If the final load or source cannot be found, keep the function as `推测` or `待确认`.

## Datasheet Evidence Strategy

Use datasheets when part identity changes firmware behavior:
- MCU pin mux, ADC capability, timer capture/PWM channel, reset/debug pins.
- Driver IC truth table, enable polarity, protection outputs, fault pins.
- Power IC enable threshold, power-good behavior, sequencing.
- Sensor curve, pull-up value, ADC conversion formula, open/short detection range.
- Communication transceiver voltage domain and fail-safe behavior.

If the exact part number is not visible in schematic parameters, BOM, PCB marking, or local labels, write `datasheet: 待确认型号`.

## Firmware Bring-Up Plan

For each board, provide a staged bring-up sequence:

1. Power rails and reset: verify rail names, MCU VDD, brownout/reset pins, clock source, debug/program header.
2. Passive inputs first: read keys, switches, level signals, ADC sensors with logging only.
3. Low-risk outputs: LEDs/buzzer/status pins with current-limited checks.
4. Power enables and isolated drivers: toggle with load disconnected when possible, verify polarity and voltage.
5. Actuators: enable one at a time with timeout, feedback check, and emergency off path.
6. Closed-loop functions: fan RPM/FG, current/voltage feedback, temperature compensation, communication protocols.
7. Fault injection: disconnect sensor, short input through safe resistance, stall feedback if allowed, simulate connector missing.

## Debug Hooks

Recommend firmware hooks that match the hardware:
- A pin-map self-test command that prints raw GPIO/ADC/timer values by net name.
- Manual actuator commands gated by safety interlocks and timeout.
- ADC raw/min/max logging for every analog channel.
- Timer capture period/frequency logging for FG/tach signals.
- Event log entries for every state-machine transition and fault latch.
- Production test mode that exercises outputs in a safe order and verifies feedback where the schematic provides it.

## Firmware Report Sections

For a full Chinese report, include:

1. 资料来源和解析置信度。
2. 端口覆盖率摘要。
3. MCU 引脚逐项确认表。
4. 外部连接器/端子功能确认表。
5. 功能模块划分。
6. MCU 外设资源分配。
7. 上电初始化和安全态。
8. 控制状态机。
9. 传感器采样、滤波、校准。
10. 故障保护和恢复策略。
11. 调试命令和日志字段。
12. 量产测试步骤。
13. 确认 / 推测 / 待确认问题清单。

## Common Output Language

Use Chinese practical engineering wording when the user is Chinese:
- `确认`: backed by netlist/PCB/screenshot evidence.
- `推测`: topology strongly suggests it, but one evidence item is missing.
- `待确认`: must be checked by datasheet, measurement, connector definition, or original engineer.

Example sentence:

`确认：MCU pin X / NET_Y 经过 R/Q/OPTO 驱动到 CNn pin m，因此软件应配置为 GPIO 输出；极性由 Q 的连接关系判断为高有效/低有效。待确认：外部负载名称需要结合线束或丝印。`
