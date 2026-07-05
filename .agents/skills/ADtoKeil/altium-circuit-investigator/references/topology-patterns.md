# Topology Patterns For Circuit Function Inference

Use these patterns as clues. Confirm with netlist endpoints, component values, local labels, connector destinations, and datasheets.

## MCU Output To Relay / Solenoid / Motor Switch

Evidence chain:

```text
MCU GPIO/PWM net -> resistor -> BJT base or MOSFET gate
transistor source/emitter -> GND or supply
transistor drain/collector -> relay/coil/load
other coil/load terminal -> supply rail
diode/TVS/snubber across coil/load
relay contacts or connector pins -> AC/DC load path
```

Interpretation:

- Low-side driver if transistor pulls coil/load to ground.
- High-side driver if transistor/source arrangement switches supply.
- Firmware needs safe default off, active polarity confirmation, flyback awareness, start blanking for current checks, and fault handling.

## MCU PWM To Analog Control Voltage

Evidence chain:

```text
MCU PWM-capable pin -> resistor/RC filter/op-amp/transistor -> connector/control pin
feedback or tach signal may return separately
```

Interpretation:

- Likely speed, dimming, setpoint, DAC-like reference, or analog command.
- Confirm voltage range, filter cutoff, output stage, and load input specification.

## Tach / Pulse Feedback

Evidence chain:

```text
connector sensor/tach pin -> resistor/divider/opto/transistor/filter -> MCU interrupt/timer pin
pull-up present
```

Interpretation:

- Speed, flow, zero-cross, encoder, or pulse feedback.
- Firmware needs edge filtering, timeout, pulses-per-revolution or conversion factor, and stall/no-pulse fault.

## ADC Sensor Divider

Evidence chain:

```text
supply rail -> resistor -> sensor connector/node -> resistor/NTC/LDR/to ground
node -> series resistor -> MCU ADC pin
capacitor from ADC node to ground
```

Interpretation:

- Temperature, level, pressure, current sense, or analog state.
- Need open/short thresholds, filtering, calibration, and only one active ADC function per physical net.

## Current Sense / Load Feedback

Evidence chain:

```text
load path -> shunt/current transformer/Hall sensor/op-amp/rectifier/filter -> MCU ADC or metering IC
```

Interpretation:

- Over-current, under-current, load-present, power calculation, or production calibration.
- Consider startup blanking, RMS vs DC average, isolation, and ADC scaling.

## Optocoupler / Isolation Boundary

Evidence chain:

```text
high-voltage or external domain -> resistor -> optocoupler LED
opto transistor side -> isolated logic rail -> MCU/net
separate grounds or net names such as GND/GND1
```

Interpretation:

- Isolated communication, zero-cross, pulse feedback, mains detect, or metering bridge.
- Do not merge grounds conceptually unless netlist proves they are same net.

## Communication Bus

Evidence chain:

```text
MCU UART/I2C/SPI-capable pins -> pull-ups/series resistors/level shifting/isolation -> IC or connector
```

Interpretation:

- Confirm direction from actual IC pin names, not schematic net names alone.
- For I2C, look for pull-ups and shared SDA/SCL.
- For UART, TX/RX labels may be from either device perspective.

## AC Load / Mains Switching

Evidence chain:

```text
relay/triac/contact -> AC-L/AC-N/fuse/connector/load terminal
snubber/MOV/NTC nearby
large creepage/clearance or isolation slot on PCB
```

Interpretation:

- Mains load switch or protection.
- Firmware must prioritize safe off state, debounce/control delays, minimum restart intervals for compressors, and fault lockouts.

## Water / Float / Level Detection

Evidence chain:

```text
connector -> pull-up/pull-down/filter/protection -> MCU GPIO/ADC
multiple level nets may form normal/full/error combinations
```

Interpretation:

- Tank, reservoir, leak, float switch, conductivity, or analog level.
- Firmware needs debounce, impossible-state detection, and output lockout policy.

## How To Avoid False Inference

- Do not call a relay “compressor” only because it is a large load; trace the contact to connector labels/load labels.
- Do not call `PUMP` a compressor or motor unless connector/load context confirms it.
- Do not assume `TX` is MCU TX; inspect both endpoint pin names.
- Do not assume a same-net dual MCU pin is intentional firmware dual-use; configure one function and keep the other safe unless design proves otherwise.
- Do not ignore local text labels; they often encode the designer's intended function.
