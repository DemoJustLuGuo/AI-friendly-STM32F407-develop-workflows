# STM32F407 HAL Keil 最小模板

这是一个自包含的 STM32F407ZGT6 Keil MDK-ARM v5 最小 HAL 工程模板。它以 ST 官方 STM32CubeF4 的 HAL/CMSIS 文件为来源，但已经裁剪掉 Eval 板 BSP、无关外设模块和共享库路径，适合作为克隆后可直接复制的新项目起点。

默认固件只做一个可观察的心跳：使用板载 8MHz HSE 配置 168MHz SYSCLK，初始化 LED1 和 LED2，然后通过 `HAL_Delay()` 周期翻转两个 LED。

## 硬件事实

- 开发板：STM32F407 开发板 C V1.0
- MCU：STM32F407ZGT6
- LED1：PA5，高电平点亮
- LED2：PA4，高电平点亮
- HSE：PH0/PH1 上的 8MHz 晶振

这些信息来自 `../../docs/hardware/schematic-stm32f407-board-c-v1.0.md`。修改引脚、时钟或外设前，先回到硬件文档确认电气行为。

## 目录结构

```text
minimal_hal_keil/
├── AGENTS.md
├── README.md
├── minimal_hal_keil.uvprojx
├── Startup/
├── User/
└── Drivers/
    ├── CMSIS/
    └── STM32F4xx_HAL_Driver/
```

`Drivers/` 是故意复制进模板的。这个工程不要指向仓库根目录外的共享 HAL/CMSIS 路径，否则项目目录单独复制给别人时很容易失效。

## 构建方式

1. 用 Keil uVision 5 打开 `minimal_hal_keil.uvprojx`。
2. 选择 `Target 1`。
3. 按 F7 构建。
4. 通过 ST-Link/SWD 下载到开发板。

构建后通常会生成：

- `Output/minimal_hal_keil.hex`
- `Output/minimal_hal_keil.axf`

这些输出文件已经被 `.gitignore` 排除。

## 从模板创建新项目

推荐复制整个目录：

```powershell
Copy-Item -Recurse .\example\minimal_hal_keil .\practice\hal_led_blink
```

复制后按顺序处理：

1. 先打开并构建一次，确认本机 Keil 环境正常。
2. 根据需要重命名 `.uvprojx` 和 Keil 输出名。
3. 修改项目级 `AGENTS.md`，写清楚新项目目标、HAL 模块、使用外设、构建和验证方式。
4. 新增外设时，把对应 HAL `.c` 文件复制到 `Drivers/STM32F4xx_HAL_Driver/Src/`，并在 `User/stm32f4xx_hal_conf.h` 中打开对应模块宏。
5. 每增加一个外设先构建一次，再继续叠加功能。

## 板级验证

烧录后，LED1 和 LED2 应该一起闪烁。闪烁频率不是精确定时要求，只用于确认时钟、SysTick、GPIO、启动文件和下载流程基本可用。
