# Evidence Checklist

Use this before finalizing circuit explanations, reviews, or software design documents.

## Minimum Evidence For A Net Function

- Net name and all terminals have been listed.
- MCU/processor pin number and pin mux function have been identified if relevant.
- Intermediate passive parts and active drivers have been followed.
- Final endpoint has been identified: IC pin, connector pin, relay contact, sensor, load, rail, or test point.
- Local schematic labels or screenshots have been checked when function is unclear.
- PCB placement/routing has been checked when load domain, connector identity, or isolation matters.
- Datasheet or component marking is noted when a part number determines function.

## Output Discipline

Write:

- “Confirmed” for direct netlist/PCB/screenshot facts.
- “Likely” for strong topology matches missing one external confirmation.
- “Need confirmation” for voltage ranges, active polarity, sensor curves, communication mode, and external load identity.

Avoid:

- Naming a function from a net label alone.
- Using component designator names as proof.
- Conflating control output with feedback input.
- Conflating pump, fan, compressor, heater, valve, and relay loads without contact/connector evidence.
- Hiding uncertainty in confident prose.

## Firmware Mapping Checklist

For each hardware signal, record:

| Field | Required detail |
| --- | --- |
| Net | exact schematic net name |
| MCU pin | designator, pin number, mux function |
| Direction | output/input/ADC/PWM/UART/I2C/SPI/timer |
| External circuit | driver, filter, divider, opto, relay, connector |
| Active polarity | confirmed or to measure |
| Safe state | reset/default state |
| Faults | open/short/no-current/over-current/no-pulse/stuck |
| Parameters | thresholds, debounce, blanking, calibration |
| Evidence | netlist endpoints, screenshot label, PCB clue |

## Reflection Questions

- What evidence would make this conclusion wrong?
- Is there another endpoint on the same net that changes the interpretation?
- Is the net on an isolated ground or high-voltage domain?
- Is the signal a control output, a feedback input, or both through different paths?
- Did I verify the load side, not just the driver side?
- Did I distinguish confirmed facts from reasonable guesses?
