---
name: workflow
description: Thin orchestration layer for embeddedskills. Use only when the user explicitly asks for one-click build/flash, automatic diagnosis, build -> flash -> debug -> observe, or /workflow. It discovers configured build/flash/debug/observe backends, calls lower-level skills, chains results through .embeddedskills/state.json, and summarizes the stage that succeeded or failed.
argument-hint: "[plan|build|build-flash|build-debug|observe|diagnose] ..."
---

# Embedded Workflow

This skill is a coordinator. It should not duplicate the Keil, serial, J-Link, OpenOCD, or firmware-analysis logic. It selects backends, calls the lower-level scripts, and aggregates results.

## Commands

```powershell
python <skill_dir>\scripts\workflow_run.py plan --json
python <skill_dir>\scripts\workflow_run.py build --json
python <skill_dir>\scripts\workflow_run.py build-flash --json
python <skill_dir>\scripts\workflow_run.py build-debug --json
python <skill_dir>\scripts\workflow_run.py observe --json
python <skill_dir>\scripts\workflow_run.py diagnose --json
```

Supported backend selector arguments:

```text
--build-backend auto|keil|gcc
--flash-backend auto|jlink|openocd|probe-rs
--debug-backend auto|jlink|openocd|probe-rs
--observe-backend auto|jlink|openocd|probe-rs
```

## Configuration

Workspace config lives in `.embeddedskills/config.json`:

```json
{
  "workflow": {
    "preferred_build": "keil",
    "preferred_flash": "auto",
    "preferred_debug": "auto",
    "preferred_observe": "auto"
  }
}
```

The workflow also reads other skill config sections such as `keil`, `serial`, `jlink`, or `openocd` when present.

## Rules

- Trigger only for explicit workflow requests such as one-click build/flash, automatic diagnosis, or build -> flash -> debug -> observe.
- If there are multiple projects, Targets, or backends, return candidates rather than guessing.
- Use `.embeddedskills/state.json` to chain build artifacts into flash/debug stages.
- `observe` should provide recommended observation commands and not hold a long-running session unless the user asked for it.
- If any stage fails, report that stage first and include the lower-level script log path or structured error.
- Do not hide an uncertain flash/debug backend behind a successful build result.

## Current Boundary

Build through Keil is working when configured. Flash/debug/observe backends are orchestration placeholders unless a dedicated backend skill or script is configured in the workspace.
