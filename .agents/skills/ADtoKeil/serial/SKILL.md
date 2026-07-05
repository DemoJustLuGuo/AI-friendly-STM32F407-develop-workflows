---
name: serial
description: Embedded serial-port debugging skill. Use when the user mentions serial, COM port, UART, baud rate, AT commands, Hex stream, serial logs, MCU output, binary protocol debugging, monitoring, sending data, or recording UART evidence. Provides scripts to scan ports, monitor text, send text/hex data, dump hex streams, record logs, and optionally use a serial mux.
argument-hint: "[scan|monitor|send|hex|log|mux] ..."
---

# Serial Debugging

Use this skill for UART/COM-port observation and command exchange during embedded bring-up.

## Capabilities

- Scan available serial ports.
- Monitor text output with filters and timestamps.
- Send text or hex payloads, optionally with CR/LF and response wait.
- View binary streams as hex dumps.
- Record logs to text, CSV, or JSON.
- Use a mux helper so monitor/log/send can share one hardware port when configured.

## Configuration

Workspace-level config lives in `.embeddedskills/config.json`:

```json
{
  "serial": {
    "port": "COM3",
    "baudrate": 115200,
    "bytesize": 8,
    "parity": "none",
    "stopbits": 1,
    "encoding": "utf-8",
    "timeout_sec": 1.0,
    "log_dir": ".embeddedskills/logs/serial"
  }
}
```

Parameter priority: CLI arguments > workspace config > `.embeddedskills/state.json` > defaults.

## Commands

Scan:

```powershell
python <skill_dir>\scripts\serial_scan.py --json
```

Monitor:

```powershell
python <skill_dir>\scripts\serial_monitor.py `
  --port COM3 --baudrate 115200 --timestamp --timeout 10
```

Send text:

```powershell
python <skill_dir>\scripts\serial_send.py `
  --port COM3 --baudrate 115200 "AT" --crlf --wait-response --json
```

Send hex:

```powershell
python <skill_dir>\scripts\serial_send.py `
  --port COM3 --baudrate 115200 "01 03 00 00 00 02" --hex --json
```

Hex dump:

```powershell
python <skill_dir>\scripts\serial_hex.py `
  --port COM3 --baudrate 115200 --timeout 10
```

Log:

```powershell
python <skill_dir>\scripts\serial_log.py `
  --port COM3 --baudrate 115200 --duration 30 --timestamp --json
```

## Rules

- Never send data unless the user asks or the task clearly requires it.
- Do not guess a port when multiple ports are present; ask or list candidates.
- Do not guess baud rate. Use project config, firmware constants, schematic notes, or the user's value.
- Prefer passive monitor/log before sending commands to an unknown device.
- For binary protocols, use `hex` or `send --hex` and record exact bytes.
- If a port is busy, report likely causes: another terminal, IDE monitor, flash tool, or mux state.
- When using mux, warn that multiple writers can corrupt the serial stream.

## Bring-up Pattern

For MCU firmware debugging:

1. Scan ports and confirm the expected adapter.
2. Monitor for reset/banner output.
3. If no output, verify baud rate, TX/RX direction, voltage domain, firmware UART init, and whether the current HEX was flashed.
4. Log evidence before changing firmware.
5. For commands, send one minimal request and wait for response.

