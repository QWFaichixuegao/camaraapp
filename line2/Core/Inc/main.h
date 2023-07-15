/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <string.h>
#include <stdio.h>
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define EN_Pin GPIO_PIN_0
#define EN_GPIO_Port GPIOA
#define STP_Pin GPIO_PIN_1
#define STP_GPIO_Port GPIOA
#define Dir_Pin GPIO_PIN_2
#define Dir_GPIO_Port GPIOA
#define LED_ROW1_Pin GPIO_PIN_3
#define LED_ROW1_GPIO_Port GPIOA
#define LED_ROW2_Pin GPIO_PIN_4
#define LED_ROW2_GPIO_Port GPIOA
#define LED_ROW3_Pin GPIO_PIN_5
#define LED_ROW3_GPIO_Port GPIOA
#define LED_ROW4_Pin GPIO_PIN_6
#define LED_ROW4_GPIO_Port GPIOA
#define LED_ROW5_Pin GPIO_PIN_7
#define LED_ROW5_GPIO_Port GPIOA
#define LED_ROW6_Pin GPIO_PIN_0
#define LED_ROW6_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */
#define SETBIT(x,y) x|=(1<<y)  			//将X的第Y位置1
#define CLRBIT(x,y) x&=~(1<<y) 			//将X的第Y位清0

typedef enum
{
	CAIJI			=0,
	RUNL			=1,
	RUNR			=2,
	STOP  		=3,
} HANDLE_STATE;

#define handdelay     3000
#define ledopendelay  2000
typedef struct {

	uint8_t flagstate ;
	uint8_t getdataflag ;
	uint8_t ledstate;
	uint16_t	savecount;

}HANDLE;
extern HANDLE handle;
#define tX_SIZE     8
#define RX_SIZE     8
#define SAVE_SIZE   8
typedef struct {
	uint16_t  rx_count;
	uint16_t  rx_len;
	uint8_t   save_buf[SAVE_SIZE];
	uint8_t   rx_buf[RX_SIZE];
	uint8_t   tx_buf[tX_SIZE];
}USARTX_HANDLE;
extern USARTX_HANDLE usart3_handle;

void ledshow(uint8_t ledstate);
void caiji(void);
void line_snap(size_t bochang_msg);
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
