# STM32F407 SPL Keil 最小模板

这是一个自包含的 STM32F407ZGT6 Keil MDK-ARM v5 最小 SPL 工程模板。它只保留建立新项目最容易缺失的部分：Keil 工程文件、启动文件、系统时钟文件、SPL 配置文件、中断文件，以及能独立构建的最小 CMSIS/SPL 库子集。

默认固件只做一个可观察的心跳：使用板载 8MHz HSE 配置 168MHz SYSCLK，初始化 LED1 和 LED2，然后在主循环中翻转两个 LED。确认这个模板能编译、烧录、看到 LED 闪烁后，再添加按键、定时器、串口、SPI、LCD、传感器或应用逻辑。

## 硬件事实

- 开发板：STM32F407 开发板 C V1.0
- MCU：STM32F407ZGT6
- LED1：PA5，高电平点亮
- LED2：PA4，高电平点亮
- HSE：PH0/PH1 上的 8MHz 晶振

这些信息来自 `../../docs/hardware/schematic-stm32f407-board-c-v1.0.md`。修改引脚或外设前，先回到硬件文档确认电气行为，不要按其他 STM32 开发板经验猜测。

## 目录结构

```text
minimal_spl_keil/
├── AGENTS.md
├── README.md
├── minimal_spl_keil.uvprojx
├── Startup/
├── User/
└── Libraries/
    ├── CMSIS/inc/
    └── STM32F4xx_StdPeriph_Driver/
```

`Libraries/` 是故意复制进模板的。这个模板面向“克隆后能直接打开”和“复制项目目录给别人也不丢依赖”，因此 Keil 工程不要指向仓库根目录外的共享库路径。

## 构建方式

1. 用 Keil uVision 5 打开 `minimal_spl_keil.uvprojx`。
2. 选择 `Target 1`。
3. 按 F7 构建。
4. 通过 ST-Link/SWD 下载到开发板。

构建后通常会生成：

- `Output/minimal_spl_keil.hex`
- `Output/minimal_spl_keil.axf`

这些输出文件已经被 `.gitignore` 排除。

## 从模板创建新项目

推荐复制整个目录，而不是只复制 `main.c`：

```powershell
Copy-Item -Recurse .\example\minimal_spl_keil .\projects\led_blink
```

复制后按顺序处理：

1. 按项目级 `AGENTS.md` 的占位段完成环境初始化，确认本机 Keil/EIDE/GCC 能力。
2. 根据需要重命名 `.uvprojx` 和 Keil 输出名。
3. 修改项目级 `AGENTS.md`，写清楚新项目目标、环境探测结果、使用外设、构建和验证方式。
4. 在 `User/main.c` 或后续 `src/`、`bsp/` 中添加项目代码。
5. 新增外设时，把对应 SPL `.c` 文件复制到 `Libraries/STM32F4xx_StdPeriph_Driver/src/`，并在 `User/stm32f4xx_conf.h` 中打开对应头文件。
6. 每增加一个外设先构建一次，再继续叠加功能。

## 板级验证

烧录后，LED1 和 LED2 应该一起闪烁。闪烁频率不是精确定时要求，只用于确认时钟、GPIO、启动文件和下载流程基本可用。

如果没有闪烁，优先检查：

- 当前下载的 HEX 是否来自这个工程。
- Keil 预处理宏里是否包含 `HSE_VALUE=8000000`。
- PA5 和 PA4 是否仍配置为推挽输出。
- 硬件文档中 LED 有效电平是否被误改。
