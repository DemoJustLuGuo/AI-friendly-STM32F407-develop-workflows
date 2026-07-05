# AI 友好的 STM32F407 开发工作流

这个仓库整理了一套面向 STM32F407 开发板的、适合人与 AI 协作使用的基础工作流。它不是某一个练习工程，也不是本地工作区的完整备份，而是把后续做固件项目时最容易反复查找、反复配置的内容先放在一起：

- 板级硬件资料和引脚、电气特性说明。
- SPL、STM32CubeF4、HAL/LL 等基础库。
- 固件项目的目录、BSP、外设初始化和构建约定。
- 一个可直接打开的 Keil SPL 最小工程模板。
- 给 Codex、Claude Code 等 AI 编程助手读取的工作规则。
- 一组可复用的嵌入式开发辅助 skill 和脚本。

适合的使用方式是：先克隆这个仓库作为 STM32F407 项目的“工作底座”，再在本地创建自己的练习工程或产品工程。AI 助手进入仓库后，可以通过 `AGENTS.md` / `CLAUDE.md` 和 `docs/` 中的文档，理解硬件约束、库路径和项目组织方式。

## 仓库内容

```text
.
├── AGENTS.md
├── CLAUDE.md
├── docs/
│   ├── hardware/
│   └── software/
├── example/
│   └── minimal_spl_keil/
├── lib/
│   ├── STM32CubeF4/
│   ├── stm32f4xx/
│   └── stm32f4xx-hal-driver/
└── .agents/
    └── skills/
        └── ADtoKeil/
```

### 工作流说明文件

- `AGENTS.md`：Codex 等工具优先读取的工作规则，说明这个工作区的目录职责、硬件参考规则、默认固件库选择、项目级 `AGENTS.md` 的要求等。
- `CLAUDE.md`：面向 Claude Code 的兼容说明，内容应与 `AGENTS.md` 保持一致。

这两个文件只记录工作区级规则。具体项目的功能、外设使用、构建方式和验证步骤，应写到项目自己的 `AGENTS.md` 中。

### 硬件资料

- `docs/hardware/schematic-stm32f407-board-c-v1.0.md` 是日常开发优先查阅的硬件索引，包含 GPIO 映射、LED/按键/蜂鸣器等电气行为、供电、时钟、BOOT 设置、SPI3 共总线规则和固件初始化检查项。
- `docs/hardware/Schematic_STM32F407开发板-C-V1.0-2606_2026-06-22.pdf` 是原理图 PDF，用于 Markdown 文档缺少细节、实际板子行为与文档冲突，或需要看连接方向和器件位置时再确认。

### 软件参考

`docs/software/` 记录可复用的软件约定：

- `project-template.md`：标准项目目录、Keil / GCC 构建文件、启动文件和 include path 的放置方式。
- `board-bsp-guide.md`：板级 BSP 的组织方式，以及 LED、按键、蜂鸣器、DHT11、SPI3、USART2、SysTick 等模块的接口风格。
- `spl-quick-reference.md`：基于 STM32F4 Standard Peripheral Library 的 RCC、GPIO、USART、SPI、定时器、NVIC 等初始化模板。
- `base-libraries.md`：本仓库内基础库的来源和用途说明。

### 最小工程模板

`example/minimal_spl_keil/` 是一个可直接打开的 Keil MDK-ARM v5 最小 SPL 工程模板。它不是只写了目录结构的空壳，而是从本地已经验证能构建的 LED 闪烁练习工程中抽取出来，再删掉练习逻辑后整理成的最小模板。

这个模板默认只做一件事：使用 8MHz HSE 配置系统时钟，初始化 PA5/PA4 上的 LED1/LED2，并在主循环中翻转两个 LED。它包含项目自己的 `Startup/`、`User/` 和必要 SPL/CMSIS 子集，Keil 工程文件也指向模板内部的 `Libraries/`，不会依赖你电脑上的某个固定工作区路径或仓库根目录外的共享库路径。

建议新项目优先从它开始：

```powershell
Copy-Item -Recurse .\example\minimal_spl_keil .\practice\my_first_project
```

复制后再改项目名、应用逻辑和项目级 `AGENTS.md`。添加新外设时，把需要的 SPL `.c` 文件复制进项目自己的 `Libraries/STM32F4xx_StdPeriph_Driver/src/`，同时在 `User/stm32f4xx_conf.h` 里打开对应头文件。这样项目目录被单独复制给别人时仍然能打开和构建。

### 基础库

- `lib/stm32f4xx/`：当前推荐的默认 SPL / CMSIS 基础库。
- `lib/STM32CubeF4/`：STM32CubeF4 中的 CMSIS、Device、示例和相关模板。
- `lib/stm32f4xx-hal-driver/`：单独放置的 STM32F4 HAL/LL Driver 组件，可视为本地版 `Drivers/STM32F4xx_HAL_Driver`。

第三方库保留其原有 README、license 和版权声明。本仓库自有文档只说明如何使用这些库，不替代 ST、CMSIS、SPL、Cube、HAL/LL 等上游许可。

## 克隆到本地后的初始化

下面以 Windows PowerShell 为例。Linux/macOS 也可以使用同样的 Git 流程，只是 Keil 相关工具通常仍依赖 Windows 环境。

### 1. 克隆仓库

```powershell
cd D:\Projects
git clone https://github.com/DemoJustLuGuo/AI-friendly-STM32F407-develop-workflows.git
cd AI-friendly-STM32F407-develop-workflows
```

如果你希望放到别的目录，把 `D:\Projects` 换成自己的工作目录即可。这个仓库体积主要来自 `lib/STM32CubeF4/`，克隆时间取决于网络环境。

### 2. 做一次完整性检查

```powershell
git status --short
Test-Path .\AGENTS.md
Test-Path .\docs\hardware\schematic-stm32f407-board-c-v1.0.md
Test-Path .\lib\stm32f4xx
Test-Path .\lib\STM32CubeF4
Test-Path .\lib\stm32f4xx-hal-driver
```

正常情况下，`git status --short` 没有输出，后面的 `Test-Path` 都返回 `True`。如果基础库目录缺失，先重新克隆，不建议在缺库状态下开始建工程。

### 3. 准备本机工具

这个仓库本身不需要 `npm install` 或类似初始化命令。真正需要准备的是嵌入式开发工具链：

- 推荐安装 Keil MDK-ARM v5，用于打开和构建 Keil 工程。
- 如果你准备用 GCC 构建，安装 `arm-none-eabi-gcc` 并确认它在 `PATH` 中。
- 如果要运行 `.agents/skills/ADtoKeil/` 下的 Python 辅助脚本，安装 Python 3。
- 如果要用串口脚本调试硬件，通常还需要安装 `pyserial`。

可以用这些命令做快速检查：

```powershell
git --version
python --version
arm-none-eabi-gcc --version
```

没有使用 GCC 时，`arm-none-eabi-gcc` 检查失败并不影响 Keil 工作流。

### 4. 先读工作规则和硬件索引

开始写固件前，建议按这个顺序读：

```text
AGENTS.md
docs/hardware/schematic-stm32f407-board-c-v1.0.md
docs/software/project-template.md
docs/software/board-bsp-guide.md
docs/software/spl-quick-reference.md
```

如果你使用 Codex、Claude Code 或其他 AI 编程助手，请让它先读取 `AGENTS.md`。这样它会知道：日常固件开发优先使用 SPL，项目代码应有自己的项目级 `AGENTS.md`，BSP 代码不要和练习业务逻辑混在一起，SPI3 上 Flash 和 LCD 的片选必须集中管理。

### 5. 从最小模板创建自己的项目

本仓库没有把本地 `practice/` 练习工程完整发布，但提供了一个自包含的最小 Keil SPL 模板。克隆后建议先从模板复制出自己的项目，而不是从零拼 Keil 工程和库路径：

```powershell
mkdir practice
Copy-Item -Recurse .\example\minimal_spl_keil .\practice\led_blink
```

复制后，先打开 `practice\led_blink\minimal_spl_keil.uvprojx` 构建一次，确认模板在你的 Keil 环境里可用。然后再根据项目需要改名和扩展。最小模板已经包含：

```text
practice/led_blink/
├── AGENTS.md
├── README.md
├── minimal_spl_keil.uvprojx
├── Startup/
├── User/
└── Libraries/
    ├── CMSIS/inc/
    └── STM32F4xx_StdPeriph_Driver/
```

如果你希望项目名更整洁，可以在复制后把 `.uvprojx` 文件名和 Keil 的输出名一起改掉。不要只改文件夹名后就假定工程内部路径也自动更新。

扩展项目时建议保持这个原则：

```text
项目能独立构建所需的启动文件、配置文件、SPL 源文件和第三方驱动，应该放在项目目录内。
```

仓库根目录的 `lib/` 适合作为“取材来源”和参考，不建议让一个准备发给别人或单独复制的 Keil 工程长期依赖 `..\..\lib` 这类共享相对路径。项目级 `AGENTS.md` 应说明这个项目的目标、芯片和开发板、使用 SPL 还是 HAL/LL、构建方式、使用到的板载外设、电气特性、验证方法，以及哪些 IDE 生成文件或输出目录不应随意修改。

### 6. 选择固件库路线

一般练习项目建议先走 SPL。新增项目可以从 `example/minimal_spl_keil/` 复制起步；如果要手动取库，来源是：

```text
lib/stm32f4xx/CMSIS/inc/
lib/stm32f4xx/StdPeriph/inc/
lib/stm32f4xx/StdPeriph/src/
```

如果项目明确选择 HAL/LL，则使用：

```text
lib/STM32CubeF4/Drivers/CMSIS/Include/
lib/STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/Include/
lib/stm32f4xx-hal-driver/Inc/
lib/stm32f4xx-hal-driver/Src/
```

无论选择哪条路线，项目都应该自己提供 `stm32f4xx_conf.h` 或 `stm32f4xx_hal_conf.h`、中断文件、启动文件引用、链接脚本或 Keil scatter 配置，以及清晰的构建说明。

### 7. 建工程前的最小检查清单

开始写代码前，确认这些问题已经有答案：

- 当前项目用 SPL 还是 HAL/LL？
- 目标芯片宏是 `STM32F40_41xxx` 还是 `STM32F407xx`？
- HSE 频率和系统时钟配置是否与硬件文档一致？
- LED、按键、蜂鸣器等外设的有效电平是否确认过？
- 如果使用 SPI3，Flash 和 LCD 的片选是否互斥？
- 项目级 `AGENTS.md` 是否写明了构建、烧录和硬件验证方式？

完成这些检查后，再让 AI 助手生成或修改代码，成功率会高很多，也更容易定位问题。

## 不包含的内容

本次公开发布刻意排除了这些本地内容：

- `practice/` 练习工程。
- `example/` 工程输出和构建产物。
- `.embeddedskills/` 本地运行状态。
- `tmp/` 临时文件。
- AD9959 外部资料，包括 `lib/AD9959模块驱动+PDF-V2.6/` 和 `AD9959模块驱动+PDF-V2.6.rar`。
- Keil 用户态文件、调试器本地配置、对象文件、HEX/AXF、map/listing、构建日志等生成物。

后续如果要公开示例工程，建议按项目逐个清理，只保留源码、项目配置、项目级 `AGENTS.md`、README 和可复现的构建说明。

## 建议的协作方式

这个仓库最有价值的地方不是“文件很多”，而是把硬件事实、软件约定和 AI 工作规则放在同一个上下文里。实际开发时建议保持三个习惯：

1. 新建项目先写项目级 `AGENTS.md`，不要只靠聊天记录保存决策。
2. 改外设代码前先查 `docs/hardware/`，不要凭常见开发板经验猜有效电平和引脚。
3. 生成代码后一定做编译、烧录和板级现象验证，再把验证结果写回项目文档。

这样这个仓库就不只是资料合集，而是可以长期复用的 STM32F407 开发工作底座。
