/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
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
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
USARTX_HANDLE usart3_handle;
HANDLE handle;
uint16_t AUTORELOAD = 2000;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_TIM2_Init();
  MX_USART1_UART_Init();
  MX_USART3_UART_Init();
  /* USER CODE BEGIN 2 */
	HAL_TIM_PWM_Start(&htim2,TIM_CHANNEL_2);
	handle.flagstate=RUNL;
	handle.ledstate=0;
  ledshow(handle.ledstate);
	HAL_UART_Receive_DMA(&huart3,usart3_handle.rx_buf,RX_SIZE);
  __HAL_UART_ENABLE_IT(&huart3, UART_IT_IDLE);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
			switch(handle.flagstate)
		{

			//0
			case CAIJI:
      caiji();
			break;

			//3
			case STOP:
        ledshow(0);
				HAL_GPIO_WritePin(EN_GPIO_Port, EN_Pin, 0);
				__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 0);
			break;

			//1
			case RUNL://Dir_Pin拉高电机左转  EN_Pin拉低使能转动
				HAL_GPIO_WritePin(Dir_GPIO_Port, Dir_Pin, GPIO_PIN_SET);
				HAL_GPIO_WritePin(EN_GPIO_Port, EN_Pin, GPIO_PIN_RESET);
				__HAL_TIM_SetAutoreload(&htim2, AUTORELOAD-1);
				__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, __HAL_TIM_GET_AUTORELOAD(&htim2)/2);//脉冲输出72000000/（72*AUTORELOAD）=2KHZ
			break;

			//2
			case RUNR://Dir_Pin拉低电机右转  EN_Pin拉低使能转动
				HAL_GPIO_WritePin(Dir_GPIO_Port, Dir_Pin, GPIO_PIN_RESET);
				HAL_GPIO_WritePin(EN_GPIO_Port, EN_Pin, GPIO_PIN_RESET);
				__HAL_TIM_SetAutoreload(&htim2, AUTORELOAD-1);
				__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, __HAL_TIM_GET_AUTORELOAD(&htim2)/2);//脉冲输出72000000/（72*AUTORELOAD）=2KHZ
			break;
		}



//		/***串口测试***/
//		sprintf((char*)usart3_handle.tx_buf,"123456");
//		for(int i=0;i<strlen((char*)usart3_handle.tx_buf);i++)//循环发送数据
//		{
//			while((USART3->SR&0X40)==0){;}//循环发送,直到发送完毕
//			USART3->DR =usart3_handle.tx_buf[i];
//		}
//		/***串口测试***/

		HAL_Delay(10);
    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void ledshow(uint8_t ledstate)
{
/***
		LED_ROW1_Pin 0X01
		LED_ROW2_Pin 0X02
		LED_ROW3_Pin 0X04
		LED_ROW4_Pin 0X08
		LED_ROW5_Pin 0X10
		LED_ROW6_Pin 0X20
		GPIO_PIN_RESET低电平关 GPIO_PIN_SET高电平开
***/
		HAL_GPIO_WritePin(LED_ROW1_GPIO_Port, LED_ROW1_Pin, 0X01&ledstate);
		HAL_GPIO_WritePin(LED_ROW2_GPIO_Port, LED_ROW2_Pin, 0X02&ledstate);
		HAL_GPIO_WritePin(LED_ROW3_GPIO_Port, LED_ROW3_Pin, 0X04&ledstate);
		HAL_GPIO_WritePin(LED_ROW4_GPIO_Port, LED_ROW4_Pin, 0X08&ledstate);
		HAL_GPIO_WritePin(LED_ROW5_GPIO_Port, LED_ROW5_Pin, 0X10&ledstate);
		HAL_GPIO_WritePin(LED_ROW6_GPIO_Port, LED_ROW6_Pin, 0X20&ledstate);
}
void sendString(const char* str, size_t length)
{

  HAL_UART_Transmit_DMA(&huart3, (uint8_t*)str, length);

}


void caiji(void)
{
	char* state ="$1";
	size_t Lengthmian = strlen(state) + 1;

	char* mian ="660";
	size_t Lengthled = strlen(mian) + 1;

//暂停电机
	HAL_GPIO_WritePin(EN_GPIO_Port, EN_Pin, 0);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 0);

	//当前采集面1
  sendString("$1", Lengthmian);
	HAL_Delay(50);

  ledshow(0x01);
	HAL_Delay(handdelay);
  sendString("660", Lengthled);
	HAL_Delay(handdelay);

  ledshow(0x02);
	HAL_Delay(handdelay);
  sendString("730", Lengthled);
	HAL_Delay(handdelay);

  ledshow(0x04);
	HAL_Delay(handdelay);
  sendString("800", Lengthled);
	HAL_Delay(handdelay);

  ledshow(0x08);
	HAL_Delay(handdelay);
  sendString("850", Lengthled);
	HAL_Delay(handdelay);

  ledshow(0x10);
	HAL_Delay(handdelay);
  sendString("940", Lengthled);
	HAL_Delay(handdelay);

  ledshow(0x20);
	HAL_Delay(handdelay);
  sendString("100", Lengthled);
	HAL_Delay(handdelay);
	ledshow(0);
	
	HAL_GPIO_WritePin(Dir_GPIO_Port, Dir_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(EN_GPIO_Port, EN_Pin, GPIO_PIN_RESET);
	__HAL_TIM_SetAutoreload(&htim2, AUTORELOAD-1);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, __HAL_TIM_GET_AUTORELOAD(&htim2)/2);//脉冲输出72000000/（72*AUTORELOAD）=2KHZ

	HAL_Delay(6000);
	
	HAL_GPIO_WritePin(EN_GPIO_Port, EN_Pin, 0);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 0);
	handle.flagstate = STOP;
}


/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
