# STM32F407 Board Support Package (BSP) Design Guide

**Target Board**: STM32F407ZGT6 Development Board  
**Repository Role**: AI-friendly STM32F407 workflow base
**Library**: STM32F4xx Standard Peripheral Library V1.3.0

This document defines the Board Support Package (BSP) architecture and API specifications for the STM32F407 development board. The BSP provides unified, reusable driver interfaces for all onboard peripherals, enabling rapid firmware development across multiple projects.

---

## Table of Contents

1. [BSP Architecture Overview](#bsp-architecture-overview)
2. [Directory Structure](#directory-structure)
3. [LED Driver Interface](#led-driver-interface)
4. [Key Driver Interface](#key-driver-interface)
5. [Buzzer Driver Interface](#buzzer-driver-interface)
6. [DHT11 Driver Interface](#dht11-driver-interface)
7. [SPI Bus Arbiter](#spi-bus-arbiter)
8. [USART Driver Interface](#usart-driver-interface)
9. [System Tick Timer](#system-tick-timer)
10. [BSP Initialization Sequence](#bsp-initialization-sequence)
11. [Integration Guide](#integration-guide)

---

## BSP Architecture Overview

### Design Principles

1. **Hardware Abstraction**: Hide hardware details behind clean APIs
2. **Reusability**: One BSP codebase shared across all practice projects
3. **Modularity**: Each peripheral is an independent module with init/deinit functions
4. **Consistency**: Unified naming conventions and return types
5. **Safety**: Input validation and error handling
6. **Efficiency**: Minimal overhead, suitable for bare-metal and RTOS environments

### Layer Structure

```
┌─────────────────────────────────────────┐
│   Application Code (practice projects)  │
├─────────────────────────────────────────┤
│   BSP API Layer (bsp_*.h/c)            │
│   - bsp_led, bsp_key, bsp_beep         │
│   - bsp_dht11, bsp_spi, bsp_usart      │
├─────────────────────────────────────────┤
│   STM32F4xx Standard Peripheral Library │
│   - stm32f4xx_gpio, stm32f4xx_spi, etc.│
├─────────────────────────────────────────┤
│   STM32F407 Hardware                    │
└─────────────────────────────────────────┘
```

### Common Return Type

All BSP functions that can fail use a common status type:

```c
typedef enum
{
    BSP_OK       = 0x00,    // Success
    BSP_ERROR    = 0x01,    // Generic error
    BSP_BUSY     = 0x02,    // Resource busy
    BSP_TIMEOUT  = 0x03,    // Operation timeout
    BSP_INVALID  = 0x04     // Invalid parameter
} BSP_StatusTypeDef;
```

---

## Directory Structure

### Recommended BSP File Organization

```
bsp/
├── inc/
│   ├── bsp_common.h        // Common types, macros, includes
│   ├── bsp_led.h           // LED driver interface
│   ├── bsp_key.h           // Key driver interface
│   ├── bsp_beep.h          // Buzzer driver interface
│   ├── bsp_dht11.h         // DHT11 temperature/humidity sensor
│   ├── bsp_spi.h           // SPI bus arbiter (Flash + LCD)
│   ├── bsp_usart.h         // USART driver (CH340C bridge)
│   └── bsp_systick.h       // System tick and delay functions
├── src/
│   ├── bsp_led.c
│   ├── bsp_key.c
│   ├── bsp_beep.c
│   ├── bsp_dht11.c
│   ├── bsp_spi.c
│   ├── bsp_usart.c
│   └── bsp_systick.c
└── README.md               // BSP usage documentation
```

---

## LED Driver Interface

### Header: `bsp_led.h`

```c
#ifndef __BSP_LED_H
#define __BSP_LED_H

#include "bsp_common.h"

/* LED identifiers */
typedef enum
{
    LED1 = 0,   // PA5, active-high
    LED2 = 1    // PA4, active-high
} LED_TypeDef;

/* LED states */
typedef enum
{
    LED_OFF = 0,
    LED_ON  = 1
} LED_StateTypeDef;

/* Public functions */
void BSP_LED_Init(void);
void BSP_LED_On(LED_TypeDef led);
void BSP_LED_Off(LED_TypeDef led);
void BSP_LED_Toggle(LED_TypeDef led);
void BSP_LED_Set(LED_TypeDef led, LED_StateTypeDef state);
LED_StateTypeDef BSP_LED_GetState(LED_TypeDef led);

#endif /* __BSP_LED_H */
```

### Implementation: `bsp_led.c`

```c
#include "bsp_led.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_rcc.h"

/* LED GPIO configuration */
#define LED1_GPIO_PORT      GPIOA
#define LED1_GPIO_PIN       GPIO_Pin_5
#define LED2_GPIO_PORT      GPIOA
#define LED2_GPIO_PIN       GPIO_Pin_4
#define LED_GPIO_CLK        RCC_AHB1Periph_GPIOA

/**
 * @brief  Initialize all LEDs
 */
void BSP_LED_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    
    // Enable GPIO clock
    RCC_AHB1PeriphClockCmd(LED_GPIO_CLK, ENABLE);
    
    // Configure LED pins as output
    GPIO_InitStruct.GPIO_Pin = LED1_GPIO_PIN | LED2_GPIO_PIN;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(LED1_GPIO_PORT, &GPIO_InitStruct);
    
    // Turn off both LEDs initially
    BSP_LED_Off(LED1);
    BSP_LED_Off(LED2);
}

/**
 * @brief  Turn on LED
 * @param  led: LED identifier (LED1 or LED2)
 */
void BSP_LED_On(LED_TypeDef led)
{
    if (led == LED1) {
        GPIO_SetBits(LED1_GPIO_PORT, LED1_GPIO_PIN);
    } else if (led == LED2) {
        GPIO_SetBits(LED2_GPIO_PORT, LED2_GPIO_PIN);
    }
}

/**
 * @brief  Turn off LED
 * @param  led: LED identifier (LED1 or LED2)
 */
void BSP_LED_Off(LED_TypeDef led)
{
    if (led == LED1) {
        GPIO_ResetBits(LED1_GPIO_PORT, LED1_GPIO_PIN);
    } else if (led == LED2) {
        GPIO_ResetBits(LED2_GPIO_PORT, LED2_GPIO_PIN);
    }
}

/**
 * @brief  Toggle LED state
 * @param  led: LED identifier (LED1 or LED2)
 */
void BSP_LED_Toggle(LED_TypeDef led)
{
    if (led == LED1) {
        GPIO_ToggleBits(LED1_GPIO_PORT, LED1_GPIO_PIN);
    } else if (led == LED2) {
        GPIO_ToggleBits(LED2_GPIO_PORT, LED2_GPIO_PIN);
    }
}

/**
 * @brief  Set LED to specific state
 * @param  led: LED identifier
 * @param  state: LED_ON or LED_OFF
 */
void BSP_LED_Set(LED_TypeDef led, LED_StateTypeDef state)
{
    if (state == LED_ON) {
        BSP_LED_On(led);
    } else {
        BSP_LED_Off(led);
    }
}

/**
 * @brief  Get current LED state
 * @param  led: LED identifier
 * @retval LED_ON or LED_OFF
 */
LED_StateTypeDef BSP_LED_GetState(LED_TypeDef led)
{
    uint8_t bit_val;
    
    if (led == LED1) {
        bit_val = GPIO_ReadOutputDataBit(LED1_GPIO_PORT, LED1_GPIO_PIN);
    } else {
        bit_val = GPIO_ReadOutputDataBit(LED2_GPIO_PORT, LED2_GPIO_PIN);
    }
    
    return (bit_val == Bit_SET) ? LED_ON : LED_OFF;
}
```

---

## Key Driver Interface

### Header: `bsp_key.h`

```c
#ifndef __BSP_KEY_H
#define __BSP_KEY_H

#include "bsp_common.h"

/* Key identifiers */
typedef enum
{
    KEY1 = 0,   // PA0, active-low
    KEY2 = 1    // PA1, active-low
} KEY_TypeDef;

/* Key states */
typedef enum
{
    KEY_RELEASED = 0,
    KEY_PRESSED  = 1
} KEY_StateTypeDef;

/* Public functions */
void BSP_KEY_Init(void);
KEY_StateTypeDef BSP_KEY_GetState(KEY_TypeDef key);
KEY_StateTypeDef BSP_KEY_WaitPress(KEY_TypeDef key, uint32_t timeout_ms);
uint8_t BSP_KEY_Scan(uint32_t debounce_ms);

#endif /* __BSP_KEY_H */
```

### Implementation: `bsp_key.c`

```c
#include "bsp_key.h"
#include "bsp_systick.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_rcc.h"

/* Key GPIO configuration */
#define KEY1_GPIO_PORT      GPIOA
#define KEY1_GPIO_PIN       GPIO_Pin_0
#define KEY2_GPIO_PORT      GPIOA
#define KEY2_GPIO_PIN       GPIO_Pin_1
#define KEY_GPIO_CLK        RCC_AHB1Periph_GPIOA

/**
 * @brief  Initialize all keys
 * @note   Keys are active-low with 10kΩ pull-down on board
 *         Requires internal pull-up: pressed = LOW, released = HIGH
 */
void BSP_KEY_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    
    // Enable GPIO clock
    RCC_AHB1PeriphClockCmd(KEY_GPIO_CLK, ENABLE);
    
    // Configure key pins as input with internal pull-up
    GPIO_InitStruct.GPIO_Pin = KEY1_GPIO_PIN | KEY2_GPIO_PIN;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
    GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;  // Don't care for input
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(KEY1_GPIO_PORT, &GPIO_InitStruct);
}

/**
 * @brief  Get current key state (no debounce)
 * @param  key: Key identifier (KEY1 or KEY2)
 * @retval KEY_PRESSED or KEY_RELEASED
 */
KEY_StateTypeDef BSP_KEY_GetState(KEY_TypeDef key)
{
    uint8_t bit_val;
    
    if (key == KEY1) {
        bit_val = GPIO_ReadInputDataBit(KEY1_GPIO_PORT, KEY1_GPIO_PIN);
    } else {
        bit_val = GPIO_ReadInputDataBit(KEY2_GPIO_PORT, KEY2_GPIO_PIN);
    }
    
    // Active-low: pressed = LOW (Bit_RESET)
    return (bit_val == Bit_RESET) ? KEY_PRESSED : KEY_RELEASED;
}

/**
 * @brief  Wait for key press with timeout
 * @param  key: Key identifier
 * @param  timeout_ms: Timeout in milliseconds (0 = wait forever)
 * @retval KEY_PRESSED if key was pressed, KEY_RELEASED if timeout
 */
KEY_StateTypeDef BSP_KEY_WaitPress(KEY_TypeDef key, uint32_t timeout_ms)
{
    uint32_t start_tick = BSP_GetTick();
    
    // Wait for key press (LOW)
    while (BSP_KEY_GetState(key) == KEY_RELEASED)
    {
        if (timeout_ms > 0 && (BSP_GetTick() - start_tick) > timeout_ms) {
            return KEY_RELEASED;  // Timeout
        }
    }
    
    // Debounce delay
    BSP_Delay(20);
    
    // Wait for key release (HIGH)
    while (BSP_KEY_GetState(key) == KEY_PRESSED)
    {
        if (timeout_ms > 0 && (BSP_GetTick() - start_tick) > timeout_ms) {
            return KEY_PRESSED;  // Still pressed at timeout
        }
    }
    
    // Debounce delay
    BSP_Delay(20);
    
    return KEY_PRESSED;
}

/**
 * @brief  Scan all keys with debounce
 * @param  debounce_ms: Debounce time in milliseconds
 * @retval Bitmask: bit 0 = KEY1, bit 1 = KEY2 (1 = pressed)
 */
uint8_t BSP_KEY_Scan(uint32_t debounce_ms)
{
    static uint8_t key_state = 0x00;
    static uint32_t last_change_tick = 0;
    uint8_t current_state = 0;
    
    // Read current key states
    if (BSP_KEY_GetState(KEY1) == KEY_PRESSED) {
        current_state |= 0x01;
    }
    if (BSP_KEY_GetState(KEY2) == KEY_PRESSED) {
        current_state |= 0x02;
    }
    
    // Debounce logic
    if (current_state != key_state)
    {
        if ((BSP_GetTick() - last_change_tick) > debounce_ms)
        {
            key_state = current_state;
            last_change_tick = BSP_GetTick();
            return key_state;  // Return new state
        }
    }
    
    return 0x00;  // No change or debouncing
}
```

---

## Buzzer Driver Interface

### Header: `bsp_beep.h`

```c
#ifndef __BSP_BEEP_H
#define __BSP_BEEP_H

#include "bsp_common.h"

/* Public functions */
void BSP_BEEP_Init(void);
void BSP_BEEP_On(void);
void BSP_BEEP_Off(void);
void BSP_BEEP_Beep(uint16_t duration_ms);

#endif /* __BSP_BEEP_H */
```

### Implementation: `bsp_beep.c`

```c
#include "bsp_beep.h"
#include "bsp_systick.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_rcc.h"

/* Buzzer GPIO configuration */
#define BEEP_GPIO_PORT      GPIOA
#define BEEP_GPIO_PIN       GPIO_Pin_6
#define BEEP_GPIO_CLK       RCC_AHB1Periph_GPIOA

/**
 * @brief  Initialize buzzer
 * @note   BEEP (PA6) is active-low: pull LOW to sound
 */
void BSP_BEEP_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    
    // Enable GPIO clock
    RCC_AHB1PeriphClockCmd(BEEP_GPIO_CLK, ENABLE);
    
    // Configure buzzer pin as output
    GPIO_InitStruct.GPIO_Pin = BEEP_GPIO_PIN;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Low_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(BEEP_GPIO_PORT, &GPIO_InitStruct);
    
    // Turn off buzzer initially (HIGH = silent)
    BSP_BEEP_Off();
}

/**
 * @brief  Turn on buzzer
 */
void BSP_BEEP_On(void)
{
    GPIO_ResetBits(BEEP_GPIO_PORT, BEEP_GPIO_PIN);  // Active-low
}

/**
 * @brief  Turn off buzzer
 */
void BSP_BEEP_Off(void)
{
    GPIO_SetBits(BEEP_GPIO_PORT, BEEP_GPIO_PIN);
}

/**
 * @brief  Beep for a duration
 * @param  duration_ms: Duration in milliseconds
 */
void BSP_BEEP_Beep(uint16_t duration_ms)
{
    BSP_BEEP_On();
    BSP_Delay(duration_ms);
    BSP_BEEP_Off();
}
```

---

## DHT11 Driver Interface

### Header: `bsp_dht11.h`

```c
#ifndef __BSP_DHT11_H
#define __BSP_DHT11_H

#include "bsp_common.h"

/* DHT11 data structure */
typedef struct
{
    uint8_t  humidity_int;      // Humidity integer part
    uint8_t  humidity_dec;      // Humidity decimal part
    uint8_t  temperature_int;   // Temperature integer part
    uint8_t  temperature_dec;   // Temperature decimal part
    uint8_t  checksum;          // Checksum
    uint8_t  valid;             // 1 if data is valid
} DHT11_DataTypeDef;

/* Public functions */
BSP_StatusTypeDef BSP_DHT11_Init(void);
BSP_StatusTypeDef BSP_DHT11_Read(DHT11_DataTypeDef *data);

#endif /* __BSP_DHT11_H */
```

### Implementation: `bsp_dht11.c`

```c
#include "bsp_dht11.h"
#include "bsp_systick.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_rcc.h"

/* DHT11 GPIO configuration */
#define DHT11_GPIO_PORT     GPIOC
#define DHT11_GPIO_PIN      GPIO_Pin_13
#define DHT11_GPIO_CLK      RCC_AHB1Periph_GPIOC

/* Pin control macros */
#define DHT11_PIN_OUT()     do { \
    GPIO_InitTypeDef GPIO_InitStruct; \
    GPIO_InitStruct.GPIO_Pin = DHT11_GPIO_PIN; \
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT; \
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed; \
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP; \
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL; \
    GPIO_Init(DHT11_GPIO_PORT, &GPIO_InitStruct); \
} while(0)

#define DHT11_PIN_IN()      do { \
    GPIO_InitTypeDef GPIO_InitStruct; \
    GPIO_InitStruct.GPIO_Pin = DHT11_GPIO_PIN; \
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN; \
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed; \
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP; \
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL; \
    GPIO_Init(DHT11_GPIO_PORT, &GPIO_InitStruct); \
} while(0)

#define DHT11_PIN_SET()     GPIO_SetBits(DHT11_GPIO_PORT, DHT11_GPIO_PIN)
#define DHT11_PIN_CLR()     GPIO_ResetBits(DHT11_GPIO_PORT, DHT11_GPIO_PIN)
#define DHT11_PIN_READ()    GPIO_ReadInputDataBit(DHT11_GPIO_PORT, DHT11_GPIO_PIN)

/**
 * @brief  Initialize DHT11
 * @note   Board has 4.7kΩ pull-up resistor on PC13
 * @retval BSP_OK or BSP_ERROR
 */
BSP_StatusTypeDef BSP_DHT11_Init(void)
{
    // Enable GPIO clock
    RCC_AHB1PeriphClockCmd(DHT11_GPIO_CLK, ENABLE);
    
    // Configure as output initially
    DHT11_PIN_OUT();
    DHT11_PIN_SET();
    
    BSP_Delay(100);  // Wait for DHT11 to stabilize
    
    return BSP_OK;
}

/**
 * @brief  Read byte from DHT11
 * @retval Received byte
 */
static uint8_t DHT11_ReadByte(void)
{
    uint8_t byte = 0;
    
    for (uint8_t i = 0; i < 8; i++)
    {
        // Wait for start of bit (LOW to HIGH)
        while (DHT11_PIN_READ() == Bit_RESET);
        
        // Wait 40us to sample bit
        BSP_DelayUs(40);
        
        byte <<= 1;
        if (DHT11_PIN_READ() == Bit_SET) {
            byte |= 0x01;
        }
        
        // Wait for end of bit (HIGH to LOW)
        while (DHT11_PIN_READ() == Bit_SET);
    }
    
    return byte;
}

/**
 * @brief  Read data from DHT11
 * @param  data: Pointer to data structure
 * @retval BSP_OK, BSP_ERROR, or BSP_TIMEOUT
 */
BSP_StatusTypeDef BSP_DHT11_Read(DHT11_DataTypeDef *data)
{
    uint8_t buf[5];
    uint32_t timeout;
    
    if (data == NULL) {
        return BSP_INVALID;
    }
    
    data->valid = 0;
    
    // Send start signal
    DHT11_PIN_OUT();
    DHT11_PIN_CLR();
    BSP_Delay(20);     // At least 18ms LOW
    DHT11_PIN_SET();
    BSP_DelayUs(30);   // 20-40us HIGH
    DHT11_PIN_IN();
    
    // Wait for DHT11 response (LOW)
    timeout = 1000;
    while (DHT11_PIN_READ() == Bit_SET && timeout--);
    if (timeout == 0) return BSP_TIMEOUT;
    
    // Wait for response HIGH
    timeout = 1000;
    while (DHT11_PIN_READ() == Bit_RESET && timeout--);
    if (timeout == 0) return BSP_TIMEOUT;
    
    // Wait for data start (LOW)
    timeout = 1000;
    while (DHT11_PIN_READ() == Bit_SET && timeout--);
    if (timeout == 0) return BSP_TIMEOUT;
    
    // Read 5 bytes
    for (uint8_t i = 0; i < 5; i++) {
        buf[i] = DHT11_ReadByte();
    }
    
    // Release bus
    DHT11_PIN_OUT();
    DHT11_PIN_SET();
    
    // Verify checksum
    if (buf[4] != (buf[0] + buf[1] + buf[2] + buf[3])) {
        return BSP_ERROR;
    }
    
    // Fill data structure
    data->humidity_int = buf[0];
    data->humidity_dec = buf[1];
    data->temperature_int = buf[2];
    data->temperature_dec = buf[3];
    data->checksum = buf[4];
    data->valid = 1;
    
    return BSP_OK;
}
```

---

## SPI Bus Arbiter

### Header: `bsp_spi.h`
```c
#ifndef __BSP_SPI_H
#define __BSP_SPI_H

#include "bsp_common.h"

/* SPI device identifiers */
typedef enum
{
    SPI_DEVICE_FLASH = 0,   // W25Q64 Flash on PA7
    SPI_DEVICE_LCD   = 1    // LCD module on PA15
} SPI_DeviceTypeDef;

/* Public functions */
BSP_StatusTypeDef BSP_SPI_Init(void);
BSP_StatusTypeDef BSP_SPI_SelectDevice(SPI_DeviceTypeDef device);
void BSP_SPI_DeselectAll(void);
uint8_t BSP_SPI_TransferByte(uint8_t data);
BSP_StatusTypeDef BSP_SPI_TransferBuffer(uint8_t *tx_buf, uint8_t *rx_buf, uint16_t len);

#endif /* __BSP_SPI_H */
```

### Implementation: `bsp_spi.c`

```c
#include "bsp_spi.h"
#include "bsp_systick.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_spi.h"
#include "stm32f4xx_rcc.h"

/* SPI3 GPIO configuration */
#define SPIx                    SPI3
#define SPIx_CLK                RCC_APB1Periph_SPI3
#define SPIx_GPIO_CLK           RCC_AHB1Periph_GPIOA | RCC_AHB1Periph_GPIOC

#define SPIx_SCK_GPIO_PORT      GPIOC
#define SPIx_SCK_GPIO_PIN       GPIO_Pin_10
#define SPIx_SCK_PIN_SOURCE     GPIO_PinSource10

#define SPIx_MISO_GPIO_PORT     GPIOC
#define SPIx_MISO_GPIO_PIN      GPIO_Pin_11
#define SPIx_MISO_PIN_SOURCE    GPIO_PinSource11

#define SPIx_MOSI_GPIO_PORT     GPIOC
#define SPIx_MOSI_GPIO_PIN      GPIO_Pin_12
#define SPIx_MOSI_PIN_SOURCE    GPIO_PinSource12

#define FLASH_CS_GPIO_PORT      GPIOA
#define FLASH_CS_GPIO_PIN       GPIO_Pin_7

#define LCD_CS_GPIO_PORT        GPIOA
#define LCD_CS_GPIO_PIN         GPIO_Pin_15

/* Current selected device */
static SPI_DeviceTypeDef current_device = (SPI_DeviceTypeDef)0xFF;

/**
 * @brief  Initialize SPI3 bus and CS pins
 * @note   Configures SPI3 as master, mode 0, 10.5MHz
 *         Flash CS = PA7, LCD CS = PA15
 * @retval BSP_OK
 */
BSP_StatusTypeDef BSP_SPI_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    SPI_InitTypeDef SPI_InitStruct;
    
    // Enable clocks
    RCC_AHB1PeriphClockCmd(SPIx_GPIO_CLK, ENABLE);
    RCC_APB1PeriphClockCmd(SPIx_CLK, ENABLE);
    
    // Configure SPI pins as alternate function
    GPIO_InitStruct.GPIO_Pin = SPIx_SCK_GPIO_PIN | SPIx_MISO_GPIO_PIN | SPIx_MOSI_GPIO_PIN;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // Connect pins to SPI3 alternate function
    GPIO_PinAFConfig(SPIx_SCK_GPIO_PORT, SPIx_SCK_PIN_SOURCE, GPIO_AF_SPI3);
    GPIO_PinAFConfig(SPIx_MISO_GPIO_PORT, SPIx_MISO_PIN_SOURCE, GPIO_AF_SPI3);
    GPIO_PinAFConfig(SPIx_MOSI_GPIO_PORT, SPIx_MOSI_PIN_SOURCE, GPIO_AF_SPI3);
    
    // Configure CS pins as GPIO output
    GPIO_InitStruct.GPIO_Pin = FLASH_CS_GPIO_PIN | LCD_CS_GPIO_PIN;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // Deselect all devices
    BSP_SPI_DeselectAll();
    
    // Configure SPI3
    SPI_InitStruct.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
    SPI_InitStruct.SPI_Mode = SPI_Mode_Master;
    SPI_InitStruct.SPI_DataSize = SPI_DataSize_8b;
    SPI_InitStruct.SPI_CPOL = SPI_CPOL_Low;      // Mode 0
    SPI_InitStruct.SPI_CPHA = SPI_CPHA_1Edge;    // Mode 0
    SPI_InitStruct.SPI_NSS = SPI_NSS_Soft;
    SPI_InitStruct.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_4;  // 10.5MHz
    SPI_InitStruct.SPI_FirstBit = SPI_FirstBit_MSB;
    SPI_InitStruct.SPI_CRCPolynomial = 7;
    SPI_Init(SPIx, &SPI_InitStruct);
    
    // Configure NSS internally
    SPI_NSSInternalSoftwareConfig(SPIx, SPI_NSSInternalSoft_Set);
    
    // Enable SPI3
    SPI_Cmd(SPIx, ENABLE);
    
    current_device = (SPI_DeviceTypeDef)0xFF;
    
    return BSP_OK;
}

/**
 * @brief  Select SPI device
 * @param  device: SPI_DEVICE_FLASH or SPI_DEVICE_LCD
 * @retval BSP_OK or BSP_BUSY
 */
BSP_StatusTypeDef BSP_SPI_SelectDevice(SPI_DeviceTypeDef device)
{
    // If same device already selected, do nothing
    if (device == current_device) {
        return BSP_OK;
    }
    
    // Deselect all devices first
    GPIO_SetBits(FLASH_CS_GPIO_PORT, FLASH_CS_GPIO_PIN);
    GPIO_SetBits(LCD_CS_GPIO_PORT, LCD_CS_GPIO_PIN);
    
    // Settling delay
    BSP_DelayUs(1);
    
    // Select requested device
    if (device == SPI_DEVICE_FLASH) {
        GPIO_ResetBits(FLASH_CS_GPIO_PORT, FLASH_CS_GPIO_PIN);
    } else if (device == SPI_DEVICE_LCD) {
        GPIO_ResetBits(LCD_CS_GPIO_PORT, LCD_CS_GPIO_PIN);
    } else {
        return BSP_INVALID;
    }
    
    current_device = device;
    
    return BSP_OK;
}

/**
 * @brief  Deselect all SPI devices
 */
void BSP_SPI_DeselectAll(void)
{
    GPIO_SetBits(FLASH_CS_GPIO_PORT, FLASH_CS_GPIO_PIN);
    GPIO_SetBits(LCD_CS_GPIO_PORT, LCD_CS_GPIO_PIN);
    current_device = (SPI_DeviceTypeDef)0xFF;
}

/**
 * @brief  Transfer one byte via SPI (blocking)
 * @param  data: Byte to send
 * @retval Received byte
 */
uint8_t BSP_SPI_TransferByte(uint8_t data)
{
    // Wait until transmit buffer is empty
    while (SPI_I2S_GetFlagStatus(SPIx, SPI_I2S_FLAG_TXE) == RESET);
    
    // Send data
    SPI_I2S_SendData(SPIx, data);
    
    // Wait until receive buffer is not empty
    while (SPI_I2S_GetFlagStatus(SPIx, SPI_I2S_FLAG_RXNE) == RESET);
    
    // Return received data
    return (uint8_t)SPI_I2S_ReceiveData(SPIx);
}

/**
 * @brief  Transfer buffer via SPI (blocking)
 * @param  tx_buf: Transmit buffer (can be NULL to send 0xFF)
 * @param  rx_buf: Receive buffer (can be NULL to discard)
 * @param  len: Number of bytes to transfer
 * @retval BSP_OK
 */
BSP_StatusTypeDef BSP_SPI_TransferBuffer(uint8_t *tx_buf, uint8_t *rx_buf, uint16_t len)
{
    for (uint16_t i = 0; i < len; i++)
    {
        uint8_t tx_data = (tx_buf != NULL) ? tx_buf[i] : 0xFF;
        uint8_t rx_data = BSP_SPI_TransferByte(tx_data);
        
        if (rx_buf != NULL) {
            rx_buf[i] = rx_data;
        }
    }
    
    return BSP_OK;
}
```

---

## USART Driver Interface

### Header: `bsp_usart.h`

```c
#ifndef __BSP_USART_H
#define __BSP_USART_H

#include "bsp_common.h"

/* USART identifiers */
typedef enum
{
    USART_CH340C = 0    // USART2 connected to CH340C USB-serial bridge
} USART_TypeDef_BSP;

/* Public functions */
BSP_StatusTypeDef BSP_USART_Init(USART_TypeDef_BSP usart, uint32_t baudrate);
void BSP_USART_SendByte(USART_TypeDef_BSP usart, uint8_t data);
uint8_t BSP_USART_ReceiveByte(USART_TypeDef_BSP usart);
void BSP_USART_SendString(USART_TypeDef_BSP usart, const char *str);
void BSP_USART_SendBuffer(USART_TypeDef_BSP usart, const uint8_t *buf, uint16_t len);
uint16_t BSP_USART_ReceiveBuffer(USART_TypeDef_BSP usart, uint8_t *buf, uint16_t max_len, uint32_t timeout_ms);

#endif /* __BSP_USART_H */
```

### Implementation: `bsp_usart.c`

```c
#include "bsp_usart.h"
#include "bsp_systick.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_usart.h"
#include "stm32f4xx_rcc.h"

/* USART2 GPIO configuration (CH340C bridge) */
#define USART2_GPIO_PORT    GPIOA
#define USART2_GPIO_CLK     RCC_AHB1Periph_GPIOA
#define USART2_CLK          RCC_APB1Periph_USART2
#define USART2_TX_PIN       GPIO_Pin_2
#define USART2_RX_PIN       GPIO_Pin_3
#define USART2_TX_SOURCE    GPIO_PinSource2
#define USART2_RX_SOURCE    GPIO_PinSource3

/**
 * @brief  Initialize USART
 * @param  usart: USART identifier (USART_CH340C)
 * @param  baudrate: Baud rate (e.g., 115200, 9600)
 * @retval BSP_OK
 */
BSP_StatusTypeDef BSP_USART_Init(USART_TypeDef_BSP usart, uint32_t baudrate)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    USART_InitTypeDef USART_InitStruct;
    
    if (usart == USART_CH340C)
    {
        // Enable clocks
        RCC_AHB1PeriphClockCmd(USART2_GPIO_CLK, ENABLE);
        RCC_APB1PeriphClockCmd(USART2_CLK, ENABLE);
        
        // Configure GPIO pins
        GPIO_InitStruct.GPIO_Pin = USART2_TX_PIN | USART2_RX_PIN;
        GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
        GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
        GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
        GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
        GPIO_Init(USART2_GPIO_PORT, &GPIO_InitStruct);
        
        // Connect to alternate function
        GPIO_PinAFConfig(USART2_GPIO_PORT, USART2_TX_SOURCE, GPIO_AF_USART2);
        GPIO_PinAFConfig(USART2_GPIO_PORT, USART2_RX_SOURCE, GPIO_AF_USART2);
        
        // Configure USART
        USART_InitStruct.USART_BaudRate = baudrate;
        USART_InitStruct.USART_WordLength = USART_WordLength_8b;
        USART_InitStruct.USART_StopBits = USART_StopBits_1;
        USART_InitStruct.USART_Parity = USART_Parity_No;
        USART_InitStruct.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
        USART_InitStruct.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
        USART_Init(USART2, &USART_InitStruct);
        
        // Enable USART
        USART_Cmd(USART2, ENABLE);
    }
    
    return BSP_OK;
}

/**
 * @brief  Send one byte
 * @param  usart: USART identifier
 * @param  data: Byte to send
 */
void BSP_USART_SendByte(USART_TypeDef_BSP usart, uint8_t data)
{
    if (usart == USART_CH340C)
    {
        while (USART_GetFlagStatus(USART2, USART_FLAG_TXE) == RESET);
        USART_SendData(USART2, data);
    }
}

/**
 * @brief  Receive one byte (blocking)
 * @param  usart: USART identifier
 * @retval Received byte
 */
uint8_t BSP_USART_ReceiveByte(USART_TypeDef_BSP usart)
{
    if (usart == USART_CH340C)
    {
        while (USART_GetFlagStatus(USART2, USART_FLAG_RXNE) == RESET);
        return (uint8_t)USART_ReceiveData(USART2);
    }
    
    return 0;
}

/**
 * @brief  Send string
 * @param  usart: USART identifier
 * @param  str: Null-terminated string
 */
void BSP_USART_SendString(USART_TypeDef_BSP usart, const char *str)
{
    while (*str) {
        BSP_USART_SendByte(usart, *str++);
    }
}

/**
 * @brief  Send buffer
 * @param  usart: USART identifier
 * @param  buf: Buffer to send
 * @param  len: Number of bytes
 */
void BSP_USART_SendBuffer(USART_TypeDef_BSP usart, const uint8_t *buf, uint16_t len)
{
    for (uint16_t i = 0; i < len; i++) {
        BSP_USART_SendByte(usart, buf[i]);
    }
}

/**
 * @brief  Receive buffer with timeout
 * @param  usart: USART identifier
 * @param  buf: Receive buffer
 * @param  max_len: Maximum bytes to receive
 * @param  timeout_ms: Timeout in milliseconds
 * @retval Number of bytes actually received
 */
uint16_t BSP_USART_ReceiveBuffer(USART_TypeDef_BSP usart, uint8_t *buf, uint16_t max_len, uint32_t timeout_ms)
{
    uint16_t count = 0;
    uint32_t start_tick = BSP_GetTick();
    
    if (usart == USART_CH340C)
    {
        while (count < max_len)
        {
            if (USART_GetFlagStatus(USART2, USART_FLAG_RXNE) != RESET)
            {
                buf[count++] = (uint8_t)USART_ReceiveData(USART2);
                start_tick = BSP_GetTick();  // Reset timeout on each byte
            }
            else if ((BSP_GetTick() - start_tick) > timeout_ms)
            {
                break;  // Timeout
            }
        }
    }
    
    return count;
}
```

---

## System Tick Timer

### Header: `bsp_systick.h`

```c
#ifndef __BSP_SYSTICK_H
#define __BSP_SYSTICK_H

#include "bsp_common.h"

/* Public functions */
void BSP_SysTick_Init(void);
uint32_t BSP_GetTick(void);
void BSP_Delay(uint32_t ms);
void BSP_DelayUs(uint32_t us);

#endif /* __BSP_SYSTICK_H */
```

### Implementation: `bsp_systick.c`

```c
#include "bsp_systick.h"
#include "stm32f4xx.h"

static volatile uint32_t systick_counter = 0;

/**
 * @brief  Initialize SysTick timer for 1ms tick
 * @note   Assumes 168MHz system clock
 */
void BSP_SysTick_Init(void)
{
    // Configure SysTick for 1ms interrupt
    // 168MHz / 1000 = 168000 ticks per millisecond
    if (SysTick_Config(SystemCoreClock / 1000))
    {
        // Capture error
        while (1);
    }
}

/**
 * @brief  SysTick interrupt handler
 * @note   This function must be called from SysTick_Handler in stm32f4xx_it.c
 */
void BSP_SysTick_Handler(void)
{
    systick_counter++;
}

/**
 * @brief  Get current tick count
 * @retval Tick count in milliseconds
 */
uint32_t BSP_GetTick(void)
{
    return systick_counter;
}

/**
 * @brief  Delay in milliseconds
 * @param  ms: Delay time in milliseconds
 */
void BSP_Delay(uint32_t ms)
{
    uint32_t start_tick = BSP_GetTick();
    
    while ((BSP_GetTick() - start_tick) < ms);
}

/**
 * @brief  Delay in microseconds
 * @param  us: Delay time in microseconds
 * @note   Not accurate, for rough timing only
 */
void BSP_DelayUs(uint32_t us)
{
    // Approximate: 168MHz = 168 cycles per microsecond
    // Each loop iteration ~= 3-4 cycles
    volatile uint32_t count = us * 42;
    
    while (count--);
}
```

---

## BSP Initialization Sequence

### Common Header: `bsp_common.h`

```c
#ifndef __BSP_COMMON_H
#define __BSP_COMMON_H

#include <stdint.h>
#include <stddef.h>
#include "stm32f4xx.h"

/* BSP status type */
typedef enum
{
    BSP_OK       = 0x00,
    BSP_ERROR    = 0x01,
    BSP_BUSY     = 0x02,
    BSP_TIMEOUT  = 0x03,
    BSP_INVALID  = 0x04
} BSP_StatusTypeDef;

/* Include all BSP headers */
#include "bsp_systick.h"
#include "bsp_led.h"
#include "bsp_key.h"
#include "bsp_beep.h"
#include "bsp_dht11.h"
#include "bsp_spi.h"
#include "bsp_usart.h"

/* BSP initialization */
void BSP_Init(void);

#endif /* __BSP_COMMON_H */
```

### Master Initialization: `bsp_init.c`

```c
#include "bsp_common.h"

/**
 * @brief  Initialize all BSP modules
 * @note   Call this function once at startup before using any BSP functions
 */
void BSP_Init(void)
{
    // Initialize system tick timer (must be first for delay functions)
    BSP_SysTick_Init();
    
    // Initialize onboard peripherals
    BSP_LED_Init();
    BSP_KEY_Init();
    BSP_BEEP_Init();
    BSP_DHT11_Init();
    
    // Initialize communication interfaces
    BSP_SPI_Init();
    BSP_USART_Init(USART_CH340C, 115200);
    
    // Send startup message
    BSP_USART_SendString(USART_CH340C, "\r\nSTM32F407 BSP Initialized\r\n");
}
```

### Interrupt Handler: Add to `stm32f4xx_it.c`

```c
#include "bsp_systick.h"

void SysTick_Handler(void)
{
    BSP_SysTick_Handler();
}
```

---

## Integration Guide

### Step 1: Add BSP to Project

1. Copy `bsp/` directory to your project
2. Add BSP include path: `bsp/inc/`
3. Add all BSP source files to build: `bsp/src/*.c`

### Step 2: Include BSP in Main

```c
#include "bsp_common.h"

int main(void)
{
    // Initialize BSP
    BSP_Init();
    
    // Your application code here
    BSP_LED_On(LED1);
    BSP_USART_SendString(USART_CH340C, "Hello World!\r\n");
    
    while (1)
    {
        if (BSP_KEY_GetState(KEY1) == KEY_PRESSED)
        {
            BSP_LED_Toggle(LED1);
            BSP_BEEP_Beep(100);
            BSP_Delay(200);
        }
    }
}
```

### Step 3: Example - Flash Access

```c
#include "bsp_common.h"

uint16_t read_flash_id(void)
{
    uint16_t id;
    
    BSP_SPI_SelectDevice(SPI_DEVICE_FLASH);
    
    BSP_SPI_TransferByte(0x90);   // Read ID command
    BSP_SPI_TransferByte(0x00);
    BSP_SPI_TransferByte(0x00);
    BSP_SPI_TransferByte(0x00);
    
    id = BSP_SPI_TransferByte(0xFF) << 8;
    id |= BSP_SPI_TransferByte(0xFF);
    
    BSP_SPI_DeselectAll();
    
    return id;
}
```

### Step 4: Example - DHT11 Reading

```c
#include "bsp_common.h"
#include <stdio.h>

void read_temperature_humidity(void)
{
    DHT11_DataTypeDef dht11_data;
    char msg[64];
    
    if (BSP_DHT11_Read(&dht11_data) == BSP_OK)
    {
        sprintf(msg, "Temp: %d.%d C, Humidity: %d.%d %%\r\n",
                dht11_data.temperature_int,
                dht11_data.temperature_dec,
                dht11_data.humidity_int,
                dht11_data.humidity_dec);
        
        BSP_USART_SendString(USART_CH340C, msg);
    }
    else
    {
        BSP_USART_SendString(USART_CH340C, "DHT11 read error\r\n");
    }
}
```

---

## BSP Design Checklist

### Module Design

- [ ] Each module has separate `.h` and `.c` files
- [ ] All functions have `BSP_<Module>_` prefix
- [ ] Hardware details are hidden in `.c` file
- [ ] GPIO/peripheral macros use `#define` in `.c` (not exposed)
- [ ] Public API uses enums for device/state selection

### Error Handling

- [ ] Functions that can fail return `BSP_StatusTypeDef`
- [ ] Pointer parameters are validated (`!= NULL`)
- [ ] Timeout mechanisms for blocking operations
- [ ] Invalid enum values are checked

### Documentation

- [ ] Every function has Doxygen-style comment
- [ ] `@brief` describes what function does
- [ ] `@param` describes each parameter
- [ ] `@retval` describes return value
- [ ] `@note` highlights hardware-specific behavior

### Reusability

- [ ] No hardcoded magic numbers (use macros)
- [ ] Configurable parameters (baudrate, timeout, etc.)
- [ ] No global state where avoidable
- [ ] Thread-safe where applicable (RTOS environments)

---

## Additional Resources

- **Hardware Reference**: `docs/hardware/schematic-stm32f407-board-c-v1.0.md`
- **SPL Quick Reference**: `docs/software/spl-quick-reference.md`
- **Workspace Guide**: `AGENTS.md`, with `CLAUDE.md` compatibility when Claude Code is used
- **Example Projects**: `practice/` directory

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-01  
**Maintainer**: Workspace documentation system
