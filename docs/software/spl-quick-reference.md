# STM32F4xx Standard Peripheral Library Quick Reference

**Library Version**: STM32F4xx_StdPeriph_Driver V1.3.0  
**Target Board**: STM32F407ZGT6 Development Board  
**Repository Role**: STM32F407-AI-develop-workflows base

This document provides quick access to commonly used STM32F4xx Standard Peripheral Library (SPL) APIs, initialization templates, and board-specific code examples. It is designed to accelerate firmware development by reducing the need to repeatedly consult the full SPL manual.

---

## Table of Contents

1. [Common Include Files](#common-include-files)
2. [RCC - Clock Configuration](#rcc---clock-configuration)
3. [GPIO - General Purpose I/O](#gpio---general-purpose-io)
4. [USART - Serial Communication](#usart---serial-communication)
5. [SPI - Serial Peripheral Interface](#spi---serial-peripheral-interface)
6. [TIM - Timers](#tim---timers)
7. [NVIC - Interrupt Controller](#nvic---interrupt-controller)
8. [Board-Specific Examples](#board-specific-examples)

---

## Common Include Files

For SPL projects targeting STM32F407ZGT6, include these headers:

```c
#include "stm32f4xx.h"                  // Main device header
#include "stm32f4xx_rcc.h"              // Clock control
#include "stm32f4xx_gpio.h"             // GPIO control
#include "stm32f4xx_usart.h"            // USART control
#include "stm32f4xx_spi.h"              // SPI control
#include "stm32f4xx_tim.h"              // Timer control
#include "stm32f4xx_misc.h"             // NVIC and SysTick functions in this workspace
```

**Device macro**: Define `STM32F40_41xxx` in project settings or before including headers:

```c
#define STM32F40_41xxx
```

**Board clock macro**: For Keil projects in this workspace, also define the 8MHz board crystal explicitly:

```c
#define HSE_VALUE 8000000
```

In Keil C/C++ preprocessor settings, use:

```text
STM32F40_41xxx
USE_STDPERIPH_DRIVER
HSE_VALUE=8000000
```

If `HSE_VALUE` is missing, the local device headers may stop compilation with `#error "OSC value not defined!"`.

**Local SPL naming note**: The shared SPL tree uses `stm32f4xx_misc.h` and `stm32f4xx_misc.c`. Do not assume older examples using `misc.h` or `misc.c` match this workspace.

---

## RCC - Clock Configuration

### Key API Functions

```c
// HSE and PLL configuration
void RCC_HSEConfig(uint8_t RCC_HSE);
ErrorStatus RCC_WaitForHSEStartUp(void);
void RCC_PLLConfig(uint32_t RCC_PLLSource, uint32_t PLLM, uint32_t PLLN, 
                   uint32_t PLLP, uint32_t PLLQ);
void RCC_PLLCmd(FunctionalState NewState);

// System clock selection
void RCC_SYSCLKConfig(uint32_t RCC_SYSCLKSource);
uint8_t RCC_GetSYSCLKSource(void);

// Bus clock dividers
void RCC_HCLKConfig(uint32_t RCC_SYSCLK);      // AHB prescaler
void RCC_PCLK1Config(uint32_t RCC_HCLK);       // APB1 prescaler
void RCC_PCLK2Config(uint32_t RCC_HCLK);       // APB2 prescaler

// Peripheral clock enable
void RCC_AHB1PeriphClockCmd(uint32_t RCC_AHB1Periph, FunctionalState NewState);
void RCC_APB1PeriphClockCmd(uint32_t RCC_APB1Periph, FunctionalState NewState);
void RCC_APB2PeriphClockCmd(uint32_t RCC_APB2Periph, FunctionalState NewState);
```

### Peripheral Clock Macros

```c
// AHB1 peripherals (RCC_AHB1PeriphClockCmd)
RCC_AHB1Periph_GPIOA
RCC_AHB1Periph_GPIOB
RCC_AHB1Periph_GPIOC
RCC_AHB1Periph_GPIOD
RCC_AHB1Periph_GPIOE
RCC_AHB1Periph_GPIOF
RCC_AHB1Periph_GPIOG
RCC_AHB1Periph_GPIOH

// APB1 peripherals (RCC_APB1PeriphClockCmd)
RCC_APB1Periph_TIM2
RCC_APB1Periph_TIM3
RCC_APB1Periph_TIM4
RCC_APB1Periph_TIM5
RCC_APB1Periph_USART2
RCC_APB1Periph_USART3
RCC_APB1Periph_SPI2
RCC_APB1Periph_SPI3
RCC_APB1Periph_I2C1
RCC_APB1Periph_I2C2

// APB2 peripherals (RCC_APB2PeriphClockCmd)
RCC_APB2Periph_TIM1
RCC_APB2Periph_USART1
RCC_APB2Periph_USART6
RCC_APB2Periph_ADC1
RCC_APB2Periph_SPI1
RCC_APB2Periph_SYSCFG
```

### System Clock Configuration Template (168MHz from 8MHz HSE)

```c
/**
 * @brief  Configure system clock to 168MHz using 8MHz HSE
 * @note   Board has 8MHz HSE crystal on PH0/PH1
 * @retval None
 */
void SystemClock_Config(void)
{
    ErrorStatus HSEStartUpStatus;
    
    // Enable HSE
    RCC_HSEConfig(RCC_HSE_ON);
    
    // Wait for HSE ready
    HSEStartUpStatus = RCC_WaitForHSEStartUp();
    
    if (HSEStartUpStatus == SUCCESS)
    {
        // Enable prefetch buffer
        FLASH_PrefetchBufferCmd(ENABLE);
        
        // Flash latency: 5 wait states for 168MHz at 3.3V
        FLASH_SetLatency(FLASH_Latency_5);
        
        // AHB = SYSCLK (168MHz)
        RCC_HCLKConfig(RCC_SYSCLK_Div1);
        
        // APB2 = AHB/2 (84MHz, max 100MHz)
        RCC_PCLK2Config(RCC_HCLK_Div2);
        
        // APB1 = AHB/4 (42MHz, max 50MHz)
        RCC_PCLK1Config(RCC_HCLK_Div4);
        
        // Configure PLL: 8MHz / 8 * 336 / 2 = 168MHz
        // PLLM=8, PLLN=336, PLLP=2, PLLQ=7 (for USB 48MHz)
        RCC_PLLConfig(RCC_PLLSource_HSE, 8, 336, 2, 7);
        
        // Enable PLL
        RCC_PLLCmd(ENABLE);
        
        // Wait for PLL ready
        while (RCC_GetFlagStatus(RCC_FLAG_PLLRDY) == RESET);
        
        // Select PLL as system clock
        RCC_SYSCLKConfig(RCC_SYSCLKSource_PLLCLK);
        
        // Wait until PLL is system clock
        while (RCC_GetSYSCLKSource() != 0x08);
    }
    else
    {
        // HSE startup failed - handle error
        while(1);
    }
}
```

---

## GPIO - General Purpose I/O

### Key API Functions

```c
// Initialization
void GPIO_Init(GPIO_TypeDef* GPIOx, GPIO_InitTypeDef* GPIO_InitStruct);
void GPIO_StructInit(GPIO_InitTypeDef* GPIO_InitStruct);

// Read operations
uint8_t GPIO_ReadInputDataBit(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);
uint16_t GPIO_ReadInputData(GPIO_TypeDef* GPIOx);
uint8_t GPIO_ReadOutputDataBit(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);

// Write operations
void GPIO_SetBits(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);      // Set pin HIGH
void GPIO_ResetBits(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);    // Set pin LOW
void GPIO_WriteBit(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin, BitAction BitVal);
void GPIO_ToggleBits(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);

// Alternate function configuration
void GPIO_PinAFConfig(GPIO_TypeDef* GPIOx, uint16_t GPIO_PinSource, uint8_t GPIO_AF);
```

### GPIO Configuration Structure

```c
typedef struct
{
    uint32_t GPIO_Pin;              // GPIO_Pin_0 to GPIO_Pin_15, or GPIO_Pin_All
    GPIOMode_TypeDef GPIO_Mode;     // GPIO_Mode_IN, OUT, AF, AN
    GPIOSpeed_TypeDef GPIO_Speed;   // GPIO_Low_Speed, Medium, Fast, High_Speed
    GPIOOType_TypeDef GPIO_OType;   // GPIO_OType_PP (push-pull), OD (open-drain)
    GPIOPuPd_TypeDef GPIO_PuPd;     // GPIO_PuPd_NOPULL, UP, DOWN
} GPIO_InitTypeDef;
```

### GPIO Modes and Types

```c
// GPIO Mode
GPIO_Mode_IN       // Input mode
GPIO_Mode_OUT      // Output mode
GPIO_Mode_AF       // Alternate function mode
GPIO_Mode_AN       // Analog mode

// Output Type
GPIO_OType_PP      // Push-pull (standard output)
GPIO_OType_OD      // Open-drain (for I2C, requires external pull-up)

// Speed
GPIO_Low_Speed     // 2MHz
GPIO_Medium_Speed  // 25MHz
GPIO_Fast_Speed    // 50MHz
GPIO_High_Speed    // 100MHz

// Pull-up/Pull-down
GPIO_PuPd_NOPULL   // No pull resistor
GPIO_PuPd_UP       // Internal pull-up (~40kΩ)
GPIO_PuPd_DOWN     // Internal pull-down (~40kΩ)
```

### GPIO Pin Macros

```c
GPIO_Pin_0   to   GPIO_Pin_15    // Individual pins
GPIO_Pin_All                      // All 16 pins
```

### GPIO Initialization Templates

#### Output Pin (Push-Pull)

```c
// Enable GPIO clock
RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);

// Configure PA5 as output
GPIO_InitTypeDef GPIO_InitStruct;
GPIO_InitStruct.GPIO_Pin = GPIO_Pin_5;
GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
GPIO_Init(GPIOA, &GPIO_InitStruct);

// Set pin high
GPIO_SetBits(GPIOA, GPIO_Pin_5);

// Set pin low
GPIO_ResetBits(GPIOA, GPIO_Pin_5);

// Toggle pin
GPIO_ToggleBits(GPIOA, GPIO_Pin_5);
```

#### Input Pin (with Pull-Up)

```c
// Enable GPIO clock
RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);

// Configure PA0 as input with pull-up
GPIO_InitTypeDef GPIO_InitStruct;
GPIO_InitStruct.GPIO_Pin = GPIO_Pin_0;
GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;     // Don't care for input
GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
GPIO_Init(GPIOA, &GPIO_InitStruct);

// Read pin state
if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_0) == Bit_SET) {
    // Pin is HIGH
} else {
    // Pin is LOW
}
```

#### Alternate Function (e.g., USART TX)

```c
// Enable GPIO and USART clocks
RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);

// Configure PA2 as USART2_TX (AF7)
GPIO_InitTypeDef GPIO_InitStruct;
GPIO_InitStruct.GPIO_Pin = GPIO_Pin_2;
GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
GPIO_Init(GPIOA, &GPIO_InitStruct);

// Connect PA2 to USART2_TX (AF7)
GPIO_PinAFConfig(GPIOA, GPIO_PinSource2, GPIO_AF_USART2);
```

#### Open-Drain Output (e.g., for DHT11)

```c
// Enable GPIO clock
RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOC, ENABLE);

// Configure PC13 as open-drain output (no internal pull-up, board has 4.7kΩ)
GPIO_InitTypeDef GPIO_InitStruct;
GPIO_InitStruct.GPIO_Pin = GPIO_Pin_13;
GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
GPIO_InitStruct.GPIO_OType = GPIO_OType_OD;
GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;   // Board has external 4.7kΩ pull-up
GPIO_Init(GPIOC, &GPIO_InitStruct);
```

---

## USART - Serial Communication

### Key API Functions

```c
// Initialization
void USART_Init(USART_TypeDef* USARTx, USART_InitTypeDef* USART_InitStruct);
void USART_StructInit(USART_InitTypeDef* USART_InitStruct);
void USART_Cmd(USART_TypeDef* USARTx, FunctionalState NewState);

// Data transfer
void USART_SendData(USART_TypeDef* USARTx, uint16_t Data);
uint16_t USART_ReceiveData(USART_TypeDef* USARTx);

// Status flags
FlagStatus USART_GetFlagStatus(USART_TypeDef* USARTx, uint16_t USART_FLAG);
void USART_ClearFlag(USART_TypeDef* USARTx, uint16_t USART_FLAG);

// Interrupt configuration
void USART_ITConfig(USART_TypeDef* USARTx, uint16_t USART_IT, FunctionalState NewState);
ITStatus USART_GetITStatus(USART_TypeDef* USARTx, uint16_t USART_IT);
```

### USART Configuration Structure

```c
typedef struct
{
    uint32_t USART_BaudRate;            // Baud rate (e.g., 9600, 115200)
    uint16_t USART_WordLength;          // USART_WordLength_8b or 9b
    uint16_t USART_StopBits;            // USART_StopBits_1, 0_5, 2, 1_5
    uint16_t USART_Parity;              // USART_Parity_No, Even, Odd
    uint16_t USART_Mode;                // USART_Mode_Rx, Tx, or Rx | Tx
    uint16_t USART_HardwareFlowControl; // USART_HardwareFlowControl_None, RTS, CTS, RTS_CTS
} USART_InitTypeDef;
```

### Common USART Flags

```c
USART_FLAG_TXE      // Transmit data register empty
USART_FLAG_RXNE     // Receive data register not empty
USART_FLAG_TC       // Transmission complete
USART_FLAG_ORE      // Overrun error
USART_FLAG_NE       // Noise error
USART_FLAG_FE       // Framing error
USART_FLAG_PE       // Parity error
```

### USART Initialization Template (115200 baud, 8N1)

```c
/**
 * @brief  Initialize USART2 on PA2(TX)/PA3(RX) for 115200 baud
 * @note   Board connects PA2/PA3 to CH340C USB-serial bridge
 * @retval None
 */
void USART2_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    USART_InitTypeDef USART_InitStruct;
    
    // Enable clocks
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
    
    // Configure PA2 (TX) and PA3 (RX) as alternate function
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_2 | GPIO_Pin_3;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // Connect pins to USART2 alternate function (AF7)
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource2, GPIO_AF_USART2);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource3, GPIO_AF_USART2);
    
    // Configure USART2: 115200 baud, 8 data bits, 1 stop bit, no parity
    USART_InitStruct.USART_BaudRate = 115200;
    USART_InitStruct.USART_WordLength = USART_WordLength_8b;
    USART_InitStruct.USART_StopBits = USART_StopBits_1;
    USART_InitStruct.USART_Parity = USART_Parity_No;
    USART_InitStruct.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    USART_InitStruct.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_Init(USART2, &USART_InitStruct);
    
    // Enable USART2
    USART_Cmd(USART2, ENABLE);
}

/**
 * @brief  Send a byte via USART2
 * @param  data: Byte to send
 * @retval None
 */
void USART2_SendByte(uint8_t data)
{
    // Wait until transmit data register is empty
    while (USART_GetFlagStatus(USART2, USART_FLAG_TXE) == RESET);
    
    // Send data
    USART_SendData(USART2, data);
}

/**
 * @brief  Receive a byte via USART2 (blocking)
 * @retval Received byte
 */
uint8_t USART2_ReceiveByte(void)
{
    // Wait until data is received
    while (USART_GetFlagStatus(USART2, USART_FLAG_RXNE) == RESET);
    
    // Read and return received data
    return (uint8_t)USART_ReceiveData(USART2);
}

/**
 * @brief  Send a string via USART2
 * @param  str: Null-terminated string
 * @retval None
 */
void USART2_SendString(const char *str)
{
    while (*str) {
        USART2_SendByte(*str++);
    }
}
```

---

## SPI - Serial Peripheral Interface

### Key API Functions

```c
// Initialization
void SPI_Init(SPI_TypeDef* SPIx, SPI_InitTypeDef* SPI_InitStruct);
void SPI_StructInit(SPI_InitTypeDef* SPI_InitStruct);
void SPI_Cmd(SPI_TypeDef* SPIx, FunctionalState NewState);

// Data transfer
void SPI_I2S_SendData(SPI_TypeDef* SPIx, uint16_t Data);
uint16_t SPI_I2S_ReceiveData(SPI_TypeDef* SPIx);

// Status flags
FlagStatus SPI_I2S_GetFlagStatus(SPI_TypeDef* SPIx, uint16_t SPI_I2S_FLAG);

// Configuration
void SPI_NSSInternalSoftwareConfig(SPI_TypeDef* SPIx, uint16_t SPI_NSSInternalSoft);
void SPI_SSOutputCmd(SPI_TypeDef* SPIx, FunctionalState NewState);
```

### SPI Configuration Structure

```c
typedef struct
{
    uint16_t SPI_Direction;         // SPI_Direction_2Lines_FullDuplex, 2Lines_RxOnly, 1Line_Rx, 1Line_Tx
    uint16_t SPI_Mode;              // SPI_Mode_Master or SPI_Mode_Slave
    uint16_t SPI_DataSize;          // SPI_DataSize_8b or 16b
    uint16_t SPI_CPOL;              // SPI_CPOL_Low or High (clock polarity)
    uint16_t SPI_CPHA;              // SPI_CPHA_1Edge or 2Edge (clock phase)
    uint16_t SPI_NSS;               // SPI_NSS_Soft or Hard
    uint16_t SPI_BaudRatePrescaler; // SPI_BaudRatePrescaler_2, 4, 8, 16, 32, 64, 128, 256
    uint16_t SPI_FirstBit;          // SPI_FirstBit_MSB or LSB
    uint16_t SPI_CRCPolynomial;     // CRC polynomial (if CRC enabled)
} SPI_InitTypeDef;
```

### SPI Modes (CPOL/CPHA)

```c
// Mode 0: CPOL=0, CPHA=0 (most common, used by W25Q64)
SPI_CPOL_Low, SPI_CPHA_1Edge

// Mode 1: CPOL=0, CPHA=1
SPI_CPOL_Low, SPI_CPHA_2Edge

// Mode 2: CPOL=1, CPHA=0
SPI_CPOL_High, SPI_CPHA_1Edge

// Mode 3: CPOL=1, CPHA=1
SPI_CPOL_High, SPI_CPHA_2Edge
```

### SPI Baud Rate Prescalers

```c
SPI_BaudRatePrescaler_2      // APB clock / 2
SPI_BaudRatePrescaler_4      // APB clock / 4
SPI_BaudRatePrescaler_8      // APB clock / 8
SPI_BaudRatePrescaler_16     // APB clock / 16
SPI_BaudRatePrescaler_32     // APB clock / 32
SPI_BaudRatePrescaler_64     // APB clock / 64
SPI_BaudRatePrescaler_128    // APB clock / 128
SPI_BaudRatePrescaler_256    // APB clock / 256
```

**Note**: SPI3 is on APB1 (42MHz at 168MHz system clock), so:
- Prescaler_2 → 21MHz
- Prescaler_4 → 10.5MHz
- Prescaler_8 → 5.25MHz

### SPI Initialization Template (SPI3 Master, Mode 0)
```c
/**
 * @brief  Initialize SPI3 as master, mode 0, 10.5MHz
 * @note   Board shares SPI3 (PC10/PC11/PC12) between W25Q64 Flash and LCD
 *         CS pins: PA7 (Flash), PA15 (LCD) - manually controlled
 * @retval None
 */
void SPI3_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    SPI_InitTypeDef SPI_InitStruct;
    
    // Enable clocks
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA | RCC_AHB1Periph_GPIOC, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_SPI3, ENABLE);
    
    // Configure PC10 (SCK), PC11 (MISO), PC12 (MOSI) as alternate function
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_10 | GPIO_Pin_11 | GPIO_Pin_12;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // Connect pins to SPI3 alternate function (AF6)
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource10, GPIO_AF_SPI3);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource11, GPIO_AF_SPI3);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource12, GPIO_AF_SPI3);
    
    // Configure PA7 (Flash CS) and PA15 (LCD CS) as GPIO output
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_7 | GPIO_Pin_15;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // Deselect both devices (CS high)
    GPIO_SetBits(GPIOA, GPIO_Pin_7 | GPIO_Pin_15);
    
    // Configure SPI3: Master, Mode 0, 10.5MHz (APB1 42MHz / 4)
    SPI_InitStruct.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
    SPI_InitStruct.SPI_Mode = SPI_Mode_Master;
    SPI_InitStruct.SPI_DataSize = SPI_DataSize_8b;
    SPI_InitStruct.SPI_CPOL = SPI_CPOL_Low;     // Mode 0
    SPI_InitStruct.SPI_CPHA = SPI_CPHA_1Edge;   // Mode 0
    SPI_InitStruct.SPI_NSS = SPI_NSS_Soft;
    SPI_InitStruct.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_4;  // 10.5MHz
    SPI_InitStruct.SPI_FirstBit = SPI_FirstBit_MSB;
    SPI_InitStruct.SPI_CRCPolynomial = 7;
    SPI_Init(SPI3, &SPI_InitStruct);
    
    // Configure NSS pin internally
    SPI_NSSInternalSoftwareConfig(SPI3, SPI_NSSInternalSoft_Set);
    
    // Enable SPI3
    SPI_Cmd(SPI3, ENABLE);
}

/**
 * @brief  Transfer a byte via SPI3 (blocking)
 * @param  data: Byte to send
 * @retval Received byte
 */
uint8_t SPI3_TransferByte(uint8_t data)
{
    // Wait until transmit buffer is empty
    while (SPI_I2S_GetFlagStatus(SPI3, SPI_I2S_FLAG_TXE) == RESET);
    
    // Send data
    SPI_I2S_SendData(SPI3, data);
    
    // Wait until receive buffer is not empty
    while (SPI_I2S_GetFlagStatus(SPI3, SPI_I2S_FLAG_RXNE) == RESET);
    
    // Return received data
    return (uint8_t)SPI_I2S_ReceiveData(SPI3);
}
```

---

## Board-Specific Examples

### Example 1: LED Control (LED1 on PA5, LED2 on PA4)

```c
/**
 * @brief  Initialize board LEDs
 * @note   LED1 (PA5) and LED2 (PA4) are active-high
 */
void LED_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    
    // Enable GPIOA clock
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    
    // Configure PA4 (LED2) and PA5 (LED1) as output
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_4 | GPIO_Pin_5;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // Turn off both LEDs initially
    GPIO_ResetBits(GPIOA, GPIO_Pin_4 | GPIO_Pin_5);
}

// LED control macros
#define LED1_ON()     GPIO_SetBits(GPIOA, GPIO_Pin_5)
#define LED1_OFF()    GPIO_ResetBits(GPIOA, GPIO_Pin_5)
#define LED1_TOGGLE() GPIO_ToggleBits(GPIOA, GPIO_Pin_5)

#define LED2_ON()     GPIO_SetBits(GPIOA, GPIO_Pin_4)
#define LED2_OFF()    GPIO_ResetBits(GPIOA, GPIO_Pin_4)
#define LED2_TOGGLE() GPIO_ToggleBits(GPIOA, GPIO_Pin_4)
```

### Example 2: Key Input (KEY1 on PA0, KEY2 on PA1)

```c
/**
 * @brief  Initialize board keys
 * @note   KEY1 (PA0) and KEY2 (PA1) are active-low with 10kΩ pull-down
 *         Requires internal pull-up; pressed = LOW, released = HIGH
 */
void KEY_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    
    // Enable GPIOA clock
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    
    // Configure PA0 (KEY1) and PA1 (KEY2) as input with pull-up
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
    GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;  // Don't care for input
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
}

/**
 * @brief  Read KEY1 state
 * @retval 1 if pressed, 0 if released
 */
uint8_t KEY1_Read(void)
{
    // Active-low: pressed = LOW (0), released = HIGH (1)
    return (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_0) == Bit_RESET) ? 1 : 0;
}

/**
 * @brief  Read KEY2 state
 * @retval 1 if pressed, 0 if released
 */
uint8_t KEY2_Read(void)
{
    return (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == Bit_RESET) ? 1 : 0;
}
```

### Example 3: Buzzer Control (BEEP on PA6)

```c
/**
 * @brief  Initialize buzzer
 * @note   BEEP (PA6) is active-low: pull LOW to sound
 */
void BEEP_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    
    // Enable GPIOA clock
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    
    // Configure PA6 as output
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_6;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // Turn off buzzer initially (HIGH = silent)
    GPIO_SetBits(GPIOA, GPIO_Pin_6);
}

#define BEEP_ON()   GPIO_ResetBits(GPIOA, GPIO_Pin_6)  // Active-low
#define BEEP_OFF()  GPIO_SetBits(GPIOA, GPIO_Pin_6)

/**
 * @brief  Beep for a duration
 * @param  ms: Duration in milliseconds
 */
void BEEP_Beep(uint16_t ms)
{
    BEEP_ON();
    delay_ms(ms);
    BEEP_OFF();
}
```

### Example 4: SPI3 Shared Bus Management (Flash + LCD)

```c
/**
 * @brief  Select Flash device on shared SPI3 bus
 * @note   Deselects LCD, waits for settling, selects Flash
 */
void SPI3_SelectFlash(void)
{
    GPIO_SetBits(GPIOA, GPIO_Pin_15);    // LCD CS = HIGH (deselect)
    delay_us(1);                          // Settling time
    GPIO_ResetBits(GPIOA, GPIO_Pin_7);   // Flash CS = LOW (select)
}

/**
 * @brief  Deselect Flash device on shared SPI3 bus
 */
void SPI3_DeselectFlash(void)
{
    GPIO_SetBits(GPIOA, GPIO_Pin_7);     // Flash CS = HIGH (deselect)
}

/**
 * @brief  Select LCD device on shared SPI3 bus
 * @note   Deselects Flash, waits for settling, selects LCD
 */
void SPI3_SelectLCD(void)
{
    GPIO_SetBits(GPIOA, GPIO_Pin_7);     // Flash CS = HIGH (deselect)
    delay_us(1);                          // Settling time
    GPIO_ResetBits(GPIOA, GPIO_Pin_15);  // LCD CS = LOW (select)
}

/**
 * @brief  Deselect LCD device on shared SPI3 bus
 */
void SPI3_DeselectLCD(void)
{
    GPIO_SetBits(GPIOA, GPIO_Pin_15);    // LCD CS = HIGH (deselect)
}

/**
 * @brief  Example: Read W25Q64 Flash ID
 * @retval 16-bit manufacturer and device ID
 */
uint16_t W25Q64_ReadID(void)
{
    uint16_t id;
    
    SPI3_SelectFlash();
    
    SPI3_TransferByte(0x90);   // Read ID command
    SPI3_TransferByte(0x00);   // Address byte 1
    SPI3_TransferByte(0x00);   // Address byte 2
    SPI3_TransferByte(0x00);   // Address byte 3
    
    id = SPI3_TransferByte(0xFF) << 8;   // Manufacturer ID
    id |= SPI3_TransferByte(0xFF);       // Device ID
    
    SPI3_DeselectFlash();
    
    return id;  // Should return 0xEF17 for W25Q64
}
```

---

## Quick Reference Tables

### Peripheral Clock Buses

| Peripheral | Bus | Clock Enable Function |
|------------|-----|----------------------|
| GPIOA-GPIOH | AHB1 | `RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOx, ENABLE)` |
| TIM2-TIM7 | APB1 | `RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIMx, ENABLE)` |
| USART2, USART3 | APB1 | `RCC_APB1PeriphClockCmd(RCC_APB1Periph_USARTx, ENABLE)` |
| USART1, USART6 | APB2 | `RCC_APB2PeriphClockCmd(RCC_APB2Periph_USARTx, ENABLE)` |
| SPI2, SPI3 | APB1 | `RCC_APB1PeriphClockCmd(RCC_APB1Periph_SPIx, ENABLE)` |
| SPI1 | APB2 | `RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE)` |

### GPIO Alternate Functions (Common)

| Function | AF Number | Connect Macro Example |
|----------|-----------|----------------------|
| USART2 TX/RX | AF7 | `GPIO_PinAFConfig(GPIOA, GPIO_PinSource2, GPIO_AF_USART2)` |
| SPI3 | AF6 | `GPIO_PinAFConfig(GPIOC, GPIO_PinSource10, GPIO_AF_SPI3)` |
| I2C1/2/3 | AF4 | `GPIO_PinAFConfig(GPIOB, GPIO_PinSource6, GPIO_AF_I2C1)` |
| TIM3/4/5 | AF2 | `GPIO_PinAFConfig(GPIOC, GPIO_PinSource6, GPIO_AF_TIM3)` |

### Board GPIO Quick Map

| Function | GPIO | Active Level | Notes |
|----------|------|--------------|-------|
| LED1 | PA5 | High | `GPIO_SetBits` to turn on |
| LED2 | PA4 | High | `GPIO_SetBits` to turn on |
| KEY1 | PA0 | Low (pressed) | Requires internal pull-up |
| KEY2 | PA1 | Low (pressed) | Requires internal pull-up |
| BEEP | PA6 | Low | `GPIO_ResetBits` to sound |
| USART2 TX | PA2 | AF7 | USB-serial bridge |
| USART2 RX | PA3 | AF7 | USB-serial bridge |
| SPI3 SCK | PC10 | AF6 | Shared: Flash + LCD |
| SPI3 MISO | PC11 | AF6 | Shared: Flash + LCD |
| SPI3 MOSI | PC12 | AF6 | Shared: Flash + LCD |
| Flash CS | PA7 | Low (active) | Manual GPIO control |
| LCD CS | PA15 | Low (active) | Manual GPIO control |
| DHT11 DATA | PC13 | Open-drain | 4.7kΩ pull-up on board |

---

## Additional Resources

- **Base Libraries**: `docs/software/base-libraries.md`
- **Full SPL Documentation**: `lib/stm32f4xx/README.md`
- **Hardware Reference**: `docs/hardware/schematic-stm32f407-board-c-v1.0.md`
- **Workspace Guide**: `AGENTS.md`
- **STM32F407 Reference Manual**: RM0090 (official ST documentation)
- **STM32F407 Datasheet**: DS8626 (official ST documentation)

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-30  
**Maintainer**: Workspace documentation system
