# ADtoKeil · 嵌入式硬件→固件 技能套件

> **语言：** [English](README.md) · **简体中文**

> 一套面向 AI Agent（Claude Code / Codex）的**嵌入式硬件开发技能集**：从读懂 Altium 原理图，到证据驱动的电路分析、由硬件推导固件、Keil 构建、串口调试，再到一键工作流编排——让 AI 基于**真实电路证据**而非猜测来理解和开发嵌入式系统。

[![Skills](https://img.shields.io/badge/skills-6-2de2e6)](#技能总览)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776ab)](#环境要求)
[![Platform](https://img.shields.io/badge/platform-Windows-0a7bd6)](#环境要求)
[![License](https://img.shields.io/badge/license-AGPL--3.0-orange)](#许可与合规)

---

## 目录

- [这是什么](#这是什么)
- [核心理念](#核心理念)
- [技能总览](#技能总览)
- [整体架构](#整体架构)
- [环境要求](#环境要求)
- [安装](#安装)
- [快速开始](#快速开始)
- [技能详解](#技能详解)
- [典型工作流](#典型工作流)
- [配置](#配置)
- [许可与合规](#许可与合规)
- [贡献](#贡献)
- [Star 趋势](#star-趋势)
- [致谢](#致谢)

---

## 这是什么

`ADtoKeil` 是一组可被 AI 编码助手（Claude Code、Codex 等）调用的**技能包（Skills）**。每个技能由一份 `SKILL.md`（能力声明 + 调用约定）和一组 Python 脚本组成，覆盖嵌入式开发的关键环节：

```
原理图读取 → 电路分析 → 固件生成 → Keil 构建 → 串口调试 → 工作流编排
```

它解决的核心痛点是：**让 AI 停止"看文件名/截图猜电路"，转而基于结构化的网络表、引脚级连通性、PCB 焊盘和本地标注等可验证证据来推理。**

## 核心理念

- **证据优先（Evidence-led）**：网络名、元件值、符号形状只是线索，结论必须由网络表端点、符号全引脚覆盖、PCB 焊盘、本地标注或数据手册证明。
- **明确不确定性**：结论分级为 `Confirmed` / `Likely` / `Hypothesis` / `Unknown`，绝不把假设当事实输出。
- **硬件是事实之源**：原理图/PCB 决定引脚与网络；厂商库被视为有"初始化/服务/重启/IO 偏置"契约的状态机。
- **分层可观测的固件**：先验证时钟与安全 GPIO 默认值，再逐层点亮输出/输入路径，最后才让应用层依赖它们。
- **不猜，宁可列候选**：存在多个工程/Target/串口/后端时，列出候选交由用户选择，而非随意决定。

---

## 技能总览

| # | 技能 | 作用 | 触发场景 |
|---|------|------|----------|
| 1 | **altium-schematic-reader** | 解析 `.PrjPcb` / `.SchDoc` → 紧凑 JSON 切片 | 理解、解释、审查、查询 Altium 电路（元件/网络/引脚/BOM/电源） |
| 2 | **altium-circuit-investigator** | 证据驱动的网络追踪 + 全引脚覆盖 + PCB 对照 | 在出报告/设计文档前，证明电路功能、绘制 MCU 引脚图、定义外部端口 |
| 3 | **embedded-firmware-from-hardware** | 由硬件证据构建/审查可维护 MCU 固件 | 把硬件知识转为 BSP/HAL 代码、引脚配置、外设驱动、板级诊断 |
| 4 | **keil** | 驱动 Keil MDK/uVision 扫描·构建·产出 HEX | 涉及 Keil/MDK/UV4/C51/8051、编译、build/rebuild/clean、产物路径 |
| 5 | **serial** | UART/COM 端口扫描·监控·收发·日志 | 串口调试、波特率、AT 指令、Hex 流、抓取 UART 证据 |
| 6 | **workflow** | 薄编排层：build → flash → debug → observe | 显式要求"一键构建/烧录/自动诊断" |

---

## 整体架构

```
表现层 / 协调层
  └─ workflow            （选择后端、串联各技能、聚合结果）
        │
        ├─ keil          （构建后端：扫描工程 / 枚举 Target / build·rebuild·clean / 解析日志 → HEX）
        ├─ serial        （观测后端：扫描 / 监控 / 收发 / 日志）
        └─ flash·debug   （占位：J-Link / OpenOCD / probe-rs，需额外后端技能）

理解 / 设计层
  ├─ altium-schematic-reader      （结构化事实：netlist / components / nets / connections / BOM）
  ├─ altium-circuit-investigator  （证据推理：trace / coverage / port inventory / 区域渲染）
  └─ embedded-firmware-from-hardware（硬件→固件：分层架构 BSP / Drivers / App + 板级诊断）

状态枢纽
  └─ .embeddedskills/state.json   （在工作区内串联各阶段的产物与上下文）
```

**依赖方向**：`workflow` 调用下层技能；理解层为固件层提供事实；各技能通过 `.embeddedskills/` 下的工作区配置与状态文件协作。

---

## 环境要求

- **操作系统**：Windows（脚本示例为 PowerShell；Keil 调用依赖 `UV4.exe`）
- **Python**：3.12+（部分缓存显示 3.12 / 3.14 均可运行）
- **可选依赖**：
  - `altium-monkey`（技能 1、2 解析 Altium 文件所需）
  - `pyserial`（技能 5 串口收发）
  - Keil MDK / C51（技能 4 的 `UV4.exe`）

> Windows 上若默认 `python` 版本过新或缺少依赖，先尝试其它启动器，如 `py -3.12`，再判断依赖是否缺失。

---

## 安装

```powershell
# 1) 获取技能集（放入 AI 助手的 skills 目录，或克隆到本地）
git clone https://github.com/Tansuo2021/ADtoKeil.git

# 2) 解析 Altium 文件所需（技能 1 / 2）
pip install altium-monkey
# 在 altium_monkey 源码检出中使用时：
$env:PYTHONPATH="path\to\altium_monkey\src\py"

# 3) 串口调试所需（技能 5）
pip install pyserial

# 4) Keil 构建（技能 4）：安装 Keil MDK，并在 keil/config.json 指向 UV4.exe
```

各技能的脚本均可独立运行，命令模式统一为：

```powershell
python <skill_dir>\scripts\<script>.py <command> [args] [--json]
```

> `<skill_dir>` 为该技能目录在你环境中的绝对或相对路径。

---

## 快速开始

```powershell
# 读懂一个 Altium 工程：永远先 summary
python <skill_dir>\scripts\read_schematic.py summary path\to\Project.PrjPcb

# 看某颗 MCU 的全部连接
python <skill_dir>\scripts\read_schematic.py connections path\to\Project.PrjPcb --designator U7

# 一键构建（已配置 Keil 后端时）
python <skill_dir>\scripts\workflow_run.py build --json

# 扫描串口并监控启动横幅
python <skill_dir>\scripts\serial_scan.py --json
python <skill_dir>\scripts\serial_monitor.py --port COM3 --baudrate 115200 --timestamp --timeout 10
```

---

## 技能详解

### 1. altium-schematic-reader （原理图读取）

通过 `altium-monkey` 读取 Altium 文件，输出**紧凑 JSON 切片**供 AI 推理，所有命令打印 JSON 到 stdout（错误打印到 stderr）。

| 命令 | 用途 |
|------|------|
| `summary <prj>` | 工程总览（首选入口，含电源/地网络） |
| `components <prj> [--brief\|--sheet\|--designator]` | 元件清单 |
| `nets <prj> [--contains\|--name]` | 网络列表 / 指定网络的全部端子 |
| `connections <prj> --designator U7 [--pin C9]` | 元件 / 单引脚连通性 |
| `bom <prj> [--variant]` | BOM 与变体 |
| `sheet <schdoc>` | 仅有单张 `.SchDoc` 时使用 |
| `raw <prj> design\|netlist` | 兜底逃生口（输出可能很大） |

**推理规则要点**：答案需引用位号、引脚号、网络名、图纸文件名；优先工程级命令而非单图；区分"网络表中不存在"与"符号上不存在"（未连接引脚须标 `NC/未连接`）。

### 2. altium-circuit-investigator （电路分析）

补充技能 1：先收集结构化网络/元件数据，再用**拓扑、本地标注、PCB 证据、覆盖率检查**证明电路含义。

**不可妥协的覆盖闸门（出报告前）**：端口清点 → 覆盖每个 MCU 符号引脚（缺失网络标 `NC`）→ 覆盖每个连接器引脚 → 原理图 vs PCB 焊盘比对 → 渲染每个"未知"信号的本地上下文 → 对每条固件相关控制/反馈信号深追至 MCU 之外至少一级有源器件 → 显式列出待确认问题。

| 脚本 | 用途 |
|------|------|
| `port_inventory.py` | 收集连接器、全符号引脚、MCU 引脚、可疑网络、本地标注、PCB 焊盘 |
| `coverage_report.py` | 汇总完整度，高亮 MCU 引脚 / PCB-only 端口 / 可疑网络 |
| `trace_net_deep.py` | 多跳追踪：穿过无源件、驱动、光耦、继电器、开关、连接器 |
| `render_region.py` | 渲染网络端点/坐标周边的原理图 SVG 区域 |
| `schdoc_probe.py` | 无工程级工具时的单图 `.SchDoc` 追踪与渲染 |
| `generate_firmware_design_report.py` | 生成中文固件设计文档骨架 |

### 3. embedded-firmware-from-hardware （固件生成）

把硬件设计知识转为**可维护的固件架构**。核心规则：原理图/PCB 是引脚与网络的事实之源；厂商库当作有初始化/服务/重启/IO 偏置契约的状态机，不凭直觉替换其流程。

**固件归属（分层）**：`App/`（产品逻辑）· `BSP/`（板级引脚与 MCU 寄存器）· `Drivers/`（外部芯片/协议）· 厂商库（如 `Firmware/TKDriver/`）放在目标工程内并用 BSP 适配器包装 · `Config/board_config.h` 作为板级契约。

**分层点亮**：先验证时钟/安全 GPIO/未用引脚 → 点亮一条输出路径（显示/蜂鸣）→ 点亮一条输入路径并用板载诊断显示 → 最后应用层才依赖它们。

### 4. keil （构建）

驱动 Keil/uVision（含 8051/C51 与 MDK），优先用脚本而非手敲 `UV4.exe`。

| 脚本 / 命令 | 用途 |
|------|------|
| `keil_project.py scan --root <ws> --json` | 扫描 `.uvproj/.uvprojx/.uvmpw` 工程 |
| `keil_project.py targets --project <p> --json` | 枚举 Target |
| `keil_build.py build\|rebuild\|clean --project <p> --target <t> --workspace <ws> --json` | 构建并解析日志，返回 HEX/AXF 路径与指标 |

成功后报告：工程、Target、日志文件、错误/警告、HEX/AXF 路径；并持久化到 `.embeddedskills/state.json` 供 workflow 复用。

> 参数优先级：CLI > 工作区配置 > 技能配置 > `state.json` > 扫描结果。
> 未经用户明确要求不编辑 `.uvproj/.uvprojx/.uvopt/.uvoptx`。

### 5. serial （串口调试）

用于嵌入式 bring-up 期间的 UART/COM 观测与命令交互。

| 脚本 | 用途 |
|------|------|
| `serial_scan.py --json` | 扫描可用串口 |
| `serial_monitor.py --port COM3 --baudrate 115200 --timestamp` | 文本监控（可过滤/时间戳） |
| `serial_send.py "AT" --crlf --wait-response --json` | 发送文本（可等待响应） |
| `serial_send.py "01 03 00 00 00 02" --hex --json` | 发送 Hex |
| `serial_hex.py` | 以 hex dump 查看二进制流 |
| `serial_log.py --duration 30 --timestamp --json` | 记录日志（text/CSV/JSON） |

**Bring-up 模式**：扫描确认适配器 → 监控复位横幅 → 无输出则核对波特率/TX-RX 方向/电平域/固件 UART 初始化/是否真的烧录了当前 HEX → 先记录证据再改固件 → 发命令时发一条最小请求等响应。

> 安全约束：非必要不主动发送数据；多端口时不猜端口；不猜波特率；优先被动监控。

### 6. workflow （工作流编排）

**薄协调层**，不重复实现下层逻辑，只选择后端、调用下层脚本、通过 `.embeddedskills/state.json` 串联结果。

```powershell
python <skill_dir>\scripts\workflow_run.py plan|build|build-flash|build-debug|observe|diagnose --json
```

后端选择器：`--build-backend auto|keil|gcc`、`--flash-backend`/`--debug-backend`/`--observe-backend auto|jlink|openocd|probe-rs`。

> 当前边界：Keil 构建在已配置时可用；flash/debug/observe 后端在未配置专用后端前为编排占位。任一阶段失败时优先报告该阶段并附下层日志路径。

---

## 典型工作流

```text
目标：拿到一块陌生板子，做出能跑的固件

1. 读懂电路   altium-schematic-reader        summary → connections / nets
                    ↓ 结构化事实
2. 证据分析   altium-circuit-investigator    port_inventory → coverage_report
                    ↓ 全引脚覆盖 + 网络深追 + PCB 对照（标注 Confirmed/Likely/Hypothesis）
3. 推导固件   embedded-firmware-from-hardware 生成分层 BSP/Drivers/App + board_config.h
                    ↓
4. 构建产物   keil                           scan → build → 解析日志 → out/firmware.hex
                    ↓ 写入 .embeddedskills/state.json
5. 烧录观测   serial                         scan → monitor 复位横幅 → log 证据
                    ↓
6. 一键编排   workflow                       build → flash → debug → observe（聚合各阶段结果）
```

---

## 配置

工作区级配置集中在 `.embeddedskills/config.json`：

```json
{
  "keil": {
    "uv4_exe": "C:/Keil_v5/UV4/UV4.exe",
    "project": "path/to/project.uvproj",
    "target": "Target 1",
    "log_dir": ".embeddedskills/build"
  },
  "serial": {
    "port": "COM3",
    "baudrate": 115200,
    "encoding": "utf-8",
    "log_dir": ".embeddedskills/logs/serial"
  },
  "workflow": {
    "preferred_build": "keil",
    "preferred_flash": "auto",
    "preferred_debug": "auto",
    "preferred_observe": "auto"
  }
}
```

- 各技能配置参考其目录下的 `config.example.json`。
- `keil` 还支持环境级 `keil/config.json`（指向 `UV4.exe`）。**该文件含真机路径、已被 git 忽略**——本地把 `config.example.json` 复制为 `config.json` 即可。
- 跨阶段状态由 `.embeddedskills/state.json` 维护（同样被 git 忽略）。

---

## 许可与合规

本项目以 **GNU Affero 通用公共许可证 v3.0（AGPL-3.0）** 发布——见 [`LICENSE`](LICENSE)。

> **为何选 AGPL-3.0**：技能 1/2 依赖的 **`altium-monkey`** 为 **AGPL-3.0-or-later**，本项目采用 AGPL-3.0 可与该依赖保持兼容。注意 AGPL 具有"传染性"：若你**分发**修改版，或**以网络服务形式对外提供其功能**，必须按 AGPL-3.0 公开相应源码。分发或托管前请先审阅许可证。

另外：仓库早前状态曾含硬编码本地路径与个人用户名，已为公开发布清理。请通过 [`.gitignore`](.gitignore) 将机器相关配置（`keil/config.json`、`.embeddedskills/`、`.env`）排除出版本控制。

---

## 贡献

欢迎提交 Issue / PR：

- **新增技能**：附 `SKILL.md`（含 `name` + `description` frontmatter）与可独立运行的脚本，命令统一支持 `--json`。
- **代码风格**：脚本输出结构化 JSON，错误打印到 stderr；存在多候选时列出而非猜测。
- **文档**：补充 `references/` 下的领域知识；保持"证据优先、明确不确定性"的一致风格。
- **测试**：覆盖正常路径与边界（空值、缺失 PCB、串口占用、构建失败等）。
- **合规**：切勿提交个人路径、用户名、密钥或机器相关配置。

---

## Star 趋势

[![Star History Chart](https://api.star-history.com/svg?repos=Tansuo2021/ADtoKeil&type=Date)](https://star-history.com/#Tansuo2021/ADtoKeil&Date)

如果这个项目对你有帮助，欢迎点一个 ⭐ —— 这对作者非常重要！

---

## 致谢

- 感谢 **[linux.do](https://linux.do)** 社区——正是这里的分享、讨论与启发，让这套技能集得以成型。🙏
- 本套件面向 Claude Code、Codex 等 AI 编码助手驱动而设计。
- Altium 解析由开源项目 [`altium-monkey`](https://pypi.org/project/altium-monkey/) 提供支持。
