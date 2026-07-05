/**
  ******************************************************************************
  * @file    main.c
  * @brief   Minimal SPL heartbeat template for the STM32F407ZGT6 board.
  ******************************************************************************
  */

#include "stm32f4xx.h"

#define LED_GPIO_PORT      GPIOA
#define LED_GPIO_CLK       RCC_AHB1Periph_GPIOA
#define LED1_GPIO_PIN      GPIO_Pin_5
#define LED2_GPIO_PIN      GPIO_Pin_4

static void SystemClock_Config(void);
static void LED_GPIO_Init(void);
static void Delay(volatile uint32_t count);

int main(void)
{
    SystemClock_Config();
    LED_GPIO_Init();

    while (1)
    {
        GPIO_ToggleBits(LED_GPIO_PORT, LED1_GPIO_PIN);
        GPIO_ToggleBits(LED_GPIO_PORT, LED2_GPIO_PIN);
        Delay(4000000);
    }
}

static void SystemClock_Config(void)
{
    RCC_DeInit();
    RCC_HSEConfig(RCC_HSE_ON);

    if (RCC_WaitForHSEStartUp() == SUCCESS)
    {
        FLASH_PrefetchBufferCmd(ENABLE);
        FLASH_SetLatency(FLASH_Latency_5);

        RCC_HCLKConfig(RCC_SYSCLK_Div1);
        RCC_PCLK2Config(RCC_HCLK_Div2);
        RCC_PCLK1Config(RCC_HCLK_Div4);

        RCC_PLLConfig(RCC_PLLSource_HSE, 8, 336, 2, 7);
        RCC_PLLCmd(ENABLE);
        while (RCC_GetFlagStatus(RCC_FLAG_PLLRDY) == RESET)
        {
        }

        RCC_SYSCLKConfig(RCC_SYSCLKSource_PLLCLK);
        while (RCC_GetSYSCLKSource() != 0x08)
        {
        }

        SystemCoreClockUpdate();
    }
    else
    {
        while (1)
        {
        }
    }
}

static void LED_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;

    RCC_AHB1PeriphClockCmd(LED_GPIO_CLK, ENABLE);

    GPIO_InitStructure.GPIO_Pin = LED1_GPIO_PIN | LED2_GPIO_PIN;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(LED_GPIO_PORT, &GPIO_InitStructure);

    GPIO_ResetBits(LED_GPIO_PORT, LED1_GPIO_PIN | LED2_GPIO_PIN);
}

static void Delay(volatile uint32_t count)
{
    while (count--)
    {
    }
}
