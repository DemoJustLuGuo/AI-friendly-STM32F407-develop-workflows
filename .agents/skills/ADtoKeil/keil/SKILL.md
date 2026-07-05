---
name: keil
description: Keil MDK/uVision build skill for embedded projects. Use when the user mentions Keil, MDK, uVision, UV4, C51, 8051, target enumeration, compile, build, rebuild, clean, firmware artifact paths, HEX output, or flash/download through a Keil project. Provides scripts to scan .uvproj/.uvprojx/.uvmpw projects, list Targets, run build/rebuild/clean/flash, parse logs, and return reusable artifact paths.
---

# Keil MDK / C51 Build

Use this skill for Keil/uVision projects, including 8051/C51 projects and MDK projects. Prefer the bundled scripts instead of manually invoking `UV4.exe`.

## Capabilities

- Scan a workspace for `.uvproj`, `.uvprojx`, and `.uvmpw` projects.
- Enumerate project Targets.
- Create or update a real project file when the user asks to develop firmware and no suitable project exists; prefer a vendor demo project as a template for C51 devices.
- Run `build`, `rebuild`, `clean`, or compatible `flash`.
- Parse the build log and return errors, warnings, HEX/AXF output paths, and metrics.
- Persist the last successful build in `.embeddedskills/state.json` for workflow reuse.

## Configuration

Environment-level config is stored in this skill's `config.json`:

```json
{
  "uv4_exe": "C:\\Keil_v5\\UV4\\UV4.exe",
  "operation_mode": 1
}
```

Workspace-level config lives in `.embeddedskills/config.json`:

```json
{
  "keil": {
    "uv4_exe": "D:/Keil_v5/UV4/UV4.exe",
    "project": "path/to/project.uvproj",
    "target": "Target 1",
    "log_dir": ".embeddedskills/build"
  }
}
```

Parameter priority: CLI arguments > workspace config > skill config > `.embeddedskills/state.json` > scan result.

## Commands

Scan projects:

```powershell
python <skill_dir>\scripts\keil_project.py scan --root <workspace> --json
```

List Targets:

```powershell
python <skill_dir>\scripts\keil_project.py targets --project <project> --json
```

Build:

```powershell
python <skill_dir>\scripts\keil_build.py build `
  --project <project> `
  --target <target> `
  --workspace <workspace> `
  --json
```

Rebuild:

```powershell
python <skill_dir>\scripts\keil_build.py rebuild `
  --project <project> `
  --target <target> `
  --workspace <workspace> `
  --json
```

Clean:

```powershell
python <skill_dir>\scripts\keil_build.py clean `
  --project <project> `
  --target <target> `
  --workspace <workspace> `
  --json
```

## Rules

- If multiple plausible projects or Targets exist, list candidates instead of guessing.
- Do not edit `.uvproj`, `.uvprojx`, `.uvopt`, or `.uvoptx` unless the user explicitly asks. If the user asks for firmware development/buildable embedded software and no project exists, treat creating a `.uvproj`/`.uvprojx` as part of the deliverable.
- Do not run `clean` implicitly before build unless the user asks for rebuild or `--clean-first`.
- After a successful build, report the project, target, log file, errors/warnings, and HEX/AXF paths.
- Treat `flash` as a compatibility entry. Prefer a dedicated J-Link/OpenOCD/probe workflow when available.
- For C51 projects, inspect the build log and map file when debugging interrupt vectors, missing source files, memory model, or startup issues.
- For vendor C51 libraries such as SinOne TKDriver, ensure the active project tree visibly includes the driver folder, headers/config files, `.C` files, and all required `.LIB` files. If a manual says to copy/export `TKDriver` into the target project, do not leave project paths pointing only to `..\TKDriver`.

## C51 Review

For 8051/C51 correctness problems, use the embedded firmware skill reference `keil-c51-project-review.md` if available. Check:

- Correct Target and HEX are being built/flashed.
- Startup file and interrupt vectors match the MCU.
- Vendor `.C` or library files are included in the Keil project.
- Vendor folder location matches the product project structure, especially for exported touch libraries.
- Code Option / clock settings match firmware constants.
- Memory model, reentrancy, and interrupt function declarations are compatible with C51.

## C51 Project Creation Checklist

When creating a C51 `.uvproj`:

- Reuse a matching vendor demo `.uvproj` and `STARTUP.A51` when available.
- Set the target name, output directory/name, HEX generation, include paths, and device clock.
- Use LX51 and Large memory model when vendor libraries require it.
- Put vendor driver folders such as `TKDriver` inside the target project directory when the manual says to migrate the folder there.
- Add visible groups for Startup, App, BSP, Drivers, and vendor libraries.
- Build/rebuild with `keil_build.py` and inspect the log/map to confirm the files used are the intended in-project files.
