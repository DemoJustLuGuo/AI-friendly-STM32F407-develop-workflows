# STM32F407-AI-develop-workflows

本仓库是一套面向 STM32F407ZGT6 开发板的 AI 协作固件开发工作流基座。它提供硬件事实索引、SPL/HAL 最小 Keil 工程模板、共享库来源说明和面向编码智能体的操作规则，用于快速初始化可迁移、可审查、上下文清晰的固件项目。

本仓库不是某个具体业务工程。下游项目应在独立的本地工作区中创建，并在项目级 `AGENTS.md` 中记录目标、所选固件栈、硬件约束和验证方式。

## 核心内容

| 目录/文件 | 作用 |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | AI 工作空间规则，说明项目路由、硬件查阅顺序、库选择和交付边界 |
| `docs/hardware/` | STM32F407 开发板硬件索引和原理图 PDF |
| `docs/software/` | 项目模板、BSP 设计、SPL 快速参考、SPL/HAL 依赖说明 |
| `docs/drivers/` | 可选的共享驱动说明、外设模块接线说明、驱动 API 约定和移植记录 |
| `drivers/` | 可选的工作流级共享驱动源码，适合多个项目复用的板级或模块级驱动 |
| `example/minimal_spl_keil/` | 可复制的 Keil MDK-ARM v5 SPL 最小工程 |
| `example/minimal_hal_keil/` | 可复制的 Keil MDK-ARM v5 HAL 最小工程 |
| `lib/stm32f4xx/` | STM32F4 SPL/CMSIS 依赖来源 |
| `lib/STM32CubeF4/` | CubeF4 CMSIS、启动文件、系统文件和有限包资料 |
| `lib/stm32f4xx-hal-driver/` | 独立 STM32F4 HAL/LL 驱动来源 |
| `.agents/skills/` | 可选的嵌入式辅助技能与脚本 |

## 初始化一个新项目

推荐使用 `projects/` 作为本地工程工作区名称。该目录不属于工作流基座本身；你可以在自己的下游仓库或本地环境中创建它。

```powershell
git clone https://github.com/DemoJustLuGuo/STM32F407-AI-develop-workflows.git
cd STM32F407-AI-develop-workflows

mkdir projects

# SPL 项目
Copy-Item -Recurse .\example\minimal_spl_keil .\projects\my-spl-project

# HAL/LL 项目
Copy-Item -Recurse .\example\minimal_hal_keil .\projects\my-hal-project
```

创建项目后，先进入项目目录，再修改项目级 `AGENTS.md`、README、Keil 工程名、输出名、源文件列表和配置头文件。不要直接在 `example/` 模板或 `lib/` 共享库来源上写业务逻辑。

## 补充资料与共享驱动

如果某些资料或驱动会被多个项目复用，推荐放在工作流根目录的共享位置，让编码智能体在项目初始化和开发前优先发现：

| 内容 | 推荐位置 | 说明 |
|---|---|---|
| 开发板补充硬件说明、模块接线、传感器电气参数 | `docs/hardware/` | 用于补充主硬件索引；涉及引脚、电平、供电、总线冲突时应优先放这里 |
| 通用软件约定、BSP 设计、移植说明、驱动 API 文档 | `docs/software/` 或 `docs/drivers/` | 面向多个项目的规则、接口和移植记录放这里 |
| 多项目共享的驱动源码 | `drivers/<driver-name>/` | 只放已经明确可复用的源码；每个驱动目录应带 README 或 AGENTS 说明支持 SPL/HAL、依赖和验证方式 |
| 第三方库或厂商基础库 | `lib/` | 作为上游依赖来源，不直接写业务逻辑 |

当补充文档或共享驱动放在这些根级位置时，编码智能体应在处理目标项目之前先读取相关说明，再决定是否复制、引用或适配到项目目录。

补充资料也可以作为单个工程的私有依赖放在目标项目目录中，例如：

```text
projects/<project-name>/docs/
projects/<project-name>/drivers/
projects/<project-name>/bsp/
```

这两种方式不冲突：根级位置适合沉淀可复用知识和共享驱动；项目级位置适合记录只服务于当前项目的模块资料、改动过的驱动、副本依赖和验证结果。若项目从根级 `drivers/` 复制驱动到项目内，应在项目级 `AGENTS.md` 中记录来源、修改点和当前验证状态。

## 全局环境初始化

本仓库故意不假设接手者的编译环境已经固定。首次在一台机器上使用本工作流时，编码智能体应先按根目录 `AGENTS.md` / `CLAUDE.md` 的规则完成环境探测，再开始具体项目开发。根级文档负责规定探测方法和必查项；探测结果应固化到目标项目的项目级 `AGENTS.md`，并在需要 Claude Code 兼容时同步到项目级 `CLAUDE.md`。

必须确认的内容包括：

| 项目 | 需要确认的问题 |
|---|---|
| Keil uVision | 是否安装 Keil MDK-ARM v5；`UV4.exe`/`UV5.exe` 是否可从命令行调用；实际安装路径是什么 |
| Keil 编译器 | 工程使用 ARMCC5 还是 ARMClang6；模板 `.uvprojx` 是否需要切换编译器；是否安装 STM32F4 Device Family Pack |
| VS Code + EIDE | 如果没有 Keil，是否可用 EIDE；EIDE 使用的 ARMCC、ARMClang 或 `arm-none-eabi-gcc` 路径是什么 |
| GCC 工具链 | 是否安装 `arm-none-eabi-gcc`、`make`、`cmake`；是否需要为项目生成 Makefile、CMake 或脚本化构建命令 |
| 烧录/调试 | 是否有 ST-Link、J-Link、OpenOCD、pyOCD 或厂商 CLI；当前机器可执行的下载命令是什么 |
| 项目模板 | SPL/HAL 模板是否能在当前工具链下构建；若不能，必须记录差异和下一步修正方式 |

Keil 工程有两类常见差异：旧工程可能固定为 ARMCC5，新机器可能只有 ARMClang6；有些环境只能通过 Keil IDE 手动构建，有些环境可以用 `UV4.exe -b <project.uvprojx> -t "<target>"` 做命令行构建。接手的编码智能体必须先确认这些差异，再决定是保留 Keil 工程、切换编译器、补 EIDE 配置，还是生成 GCC 构建文件。

## AI 初始化提示词

在新的 AI 会话中，可以直接使用下面这段提示词初始化上下文：

```text
你正在协助我开发 STM32F407ZGT6 开发板固件。请先读取仓库根目录 AGENTS.md，再读取 docs/hardware/schematic-stm32f407-board-c-v1.0.md，以及 docs/software/project-template.md、docs/software/base-libraries.md 和 docs/software/board-bsp-guide.md。

开始具体项目开发前，请先按根目录规则完成环境初始化：探测当前机器是否有 Keil、Keil 命令行路径、ARMCC/ARMClang 版本、STM32F4 pack、EIDE、arm-none-eabi-gcc、make/cmake 和可用烧录工具。然后把与目标项目相关的探测结果写入该项目的 AGENTS.md；如果项目同时维护 CLAUDE.md，也要保持两者一致。

接下来请在目标项目目录内工作。如果项目目录没有 AGENTS.md，请先根据根目录规则创建项目级 AGENTS.md。创建或修改代码前，先确认本项目选择的固件栈是 SPL 还是 HAL/LL，并把项目目标、所选栈、项目本地库路径、宏定义、启动文件、配置头文件、硬件引脚和验证步骤写入项目级 AGENTS.md。

生成外设代码时必须依据硬件 Markdown 索引确认电平、引脚、时钟、SPI3 共享总线和电源限制；只有 Markdown 缺少细节或行为矛盾时才查原理图 PDF。完成修改后请说明编译、烧录和板级验证步骤。
```

## 固件栈选择

本工作流同时支持 SPL 和 HAL/LL。新项目初始化时必须显式选择其中之一，并在项目级 `AGENTS.md` 中记录。

| 选择 | 推荐起点 | 主要依赖 | 常用宏 |
|---|---|---|---|
| SPL | `example/minimal_spl_keil/` | `lib/stm32f4xx/` | `STM32F40_41xxx`, `USE_STDPERIPH_DRIVER`, `HSE_VALUE=8000000` |
| HAL/LL | `example/minimal_hal_keil/` | `lib/STM32CubeF4/Drivers/CMSIS/` + `lib/stm32f4xx-hal-driver/` | `STM32F407xx`, `USE_HAL_DRIVER`, `HSE_VALUE=8000000` |

可迁移项目应把所需库子集复制到项目目录，并使用项目本地路径构建。只有临时实验才建议直接引用根目录 `lib/`。

## 推荐工作流

1. 克隆本仓库并创建本地 `projects/` 工作区。
2. 首次使用时按根目录规则完成环境初始化，并把结果写入目标项目的项目级 `AGENTS.md`。
3. 根据目标选择 SPL 或 HAL/LL 最小模板。
4. 进入项目目录，更新项目级 `AGENTS.md`，明确固件栈、项目本地依赖、硬件资源和验证步骤。
5. 根据 `docs/hardware/schematic-stm32f407-board-c-v1.0.md` 确认外设电气行为。
6. 按 `docs/software/project-template.md` 和 `docs/software/base-libraries.md` 补齐项目本地依赖。
7. 如果项目需要补充资料或共享驱动，先检查根级 `docs/hardware/`、`docs/software/`、`docs/drivers/` 和 `drivers/`，再决定复制到项目内还是直接作为共享参考。
8. 将板级代码放入 `bsp/`，将应用逻辑放入 `src/` 或项目自有模块。
9. 通过 `编译 -> 烧录 -> 板级现象验证` 闭环，并把项目结果记录到项目文档或交互上下文中。

## 复用边界

根目录文档记录工作流级规则、硬件事实、共享软件约定和环境初始化方法。具体项目的工具链探测结果、业务逻辑、引脚取舍、外设组合、调试现象和验收标准应写入项目级文档。

发布下游项目时，保留源码、项目级 AI 规则、构建说明和必要的库子集；构建产物、IDE 本地状态、个人绝对路径和临时调试缓存应由项目自己的 `.gitignore` 管理。
