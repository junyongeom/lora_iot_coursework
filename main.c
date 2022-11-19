#define IS_ENDNODE

/* Includes ------------------------------------------------------------------*/
#include <string.h>
#include <cmath> //
#include <stdlib.h>
#include "hw.h"
#include "radio.h"
#include "timeServer.h"
#include "low_power_manager.h"
#include "vcom.h"
#include "HTS221_Driver.h"
#include <time.h>


#define TX_OUTPUT_POWER                             14        // dBm
#define LORA_BANDWIDTH                              0         // [0: 125 kHz,
#define LORA_SPREADING_FACTOR                       7         // [SF7..SF12]
#define LORA_CODINGRATE                             1         // [1: 4/5,
#define LORA_PREAMBLE_LENGTH                        8         // Same for Tx and Rx
#define LORA_SYMBOL_TIMEOUT                         5         // Symbols
#define LORA_FIX_LENGTH_PAYLOAD_ON                  false
#define LORA_IQ_INVERSION_ON                        false


#if defined( IS_ENDNODE )
#include "bsp.h"
#endif

typedef enum
{
  LOWPOWER,
  RX,
  RX_TIMEOUT,
  RX_ERROR,
  TX,
  TX_TIMEOUT,
} States_t;

#define RX_TIMEOUT_VALUE                            3000
#define BUFFER_SIZE                                 64 // Define the payload size here
#define LED_PERIOD_MS               200

#define LEDS_OFF   do{ \
                   LED_Off( LED_BLUE ) ;   \
                   LED_Off( LED_RED ) ;    \
                   LED_Off( LED_GREEN1 ) ; \
                   LED_Off( LED_GREEN2 ) ; \
                   } while(0) ;


uint16_t BufferSize = BUFFER_SIZE;
uint8_t Buffer[BUFFER_SIZE];

States_t State = LOWPOWER;

int8_t RssiValue = 0;
int8_t SnrValue = 0;
									 
/* Led Timers objects*/
static  TimerEvent_t timerLed;

/* Private function prototypes -----------------------------------------------*/
/*!
 * Radio events function pointer
 */
static RadioEvents_t RadioEvents;

/*!
 * \brief Function to be executed on Radio Tx Done event
 */
void OnTxDone(void);

/*!
 * \brief Function to be executed on Radio Rx Done event
 */
void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr);

/*!
 * \brief Function executed on Radio Tx Timeout event
 */
void OnTxTimeout(void);

/*!
 * \brief Function executed on Radio Rx Timeout event
 */
void OnRxTimeout(void);

/*!
 * \brief Function executed on Radio Rx Error event
 */
void OnRxError(void);

/*!
 * \brief Function executed on when led timer elapses
 */
static void OnledEvent(void *context);
/**
 * Main application entry point.
 */
 
/*
* Function executed for movement detection
*/
int main(void)
{
	HAL_Init();

  SystemClock_Config();

  DBG_Init();

  HW_Init();
	
	#if defined( IS_ENDNODE )
	uint16_t pressure = 0;
  int16_t temperature = 0;
  uint16_t humidity = 0;
  uint8_t batteryLevel;
  sensor_t sensor_data;
	int32_t accel_scalar = 1083; // 
	uint16_t accel_except_num = 0;
	uint16_t sequence_num = 0;
	//uint16_t lora_ID = rand() % 999; // its actually pseudo random
	uint16_t lora_ID = 597;
	#endif
	
  
	
	uint8_t i;

  /*Disbale Stand-by mode*/
  LPM_SetOffMode(LPM_APPLI_Id, LPM_Disable);

  RadioEvents.TxDone = OnTxDone;
  RadioEvents.RxDone = OnRxDone;
  RadioEvents.TxTimeout = OnTxTimeout;
  RadioEvents.RxTimeout = OnRxTimeout;
  RadioEvents.RxError = OnRxError;

  Radio.Init(&RadioEvents);

  Radio.SetChannel(RF_FREQUENCY);

#if defined( USE_MODEM_LORA )

  Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                    LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                    LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                    true, 0, 0, LORA_IQ_INVERSION_ON, 3000);

  Radio.SetRxConfig(MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
                    LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH,
                    LORA_SYMBOL_TIMEOUT, LORA_FIX_LENGTH_PAYLOAD_ON,
                    0, true, 0, 0, LORA_IQ_INVERSION_ON, true);


#else
#error "Please define a frequency band in the compiler options."
#endif

  
	#if defined( IS_ENDNODE )
	State = TX; // only sending 
	#else
	State = RX; // only listening
	#endif
	DelayMs(1000);
	
  while (1)
  {
    switch (State)
    {
      case TX:
				if(BufferSize > 0)
				{
					int len = 0;
					char temp[100];
					
					TimerStop(&timerLed);
          LED_Off(LED_BLUE);
          LED_Off(LED_GREEN) ;
          LED_Off(LED_RED1) ;
          LED_Toggle(LED_RED2) ;
					
					#if defined( IS_ENDNODE )
					BSP_sensor_Read(&sensor_data); // sensor_enabled in hw_conf.h must be set
					temperature = (int16_t)(sensor_data.temperature * 100);         /* in t * 100 */
					pressure    = (uint16_t)(sensor_data.pressure * 100 / 10);      /* in hPa / 10 */
					
					accel_temp = accel_scalar; //
					accel_scalar = sqrt(pow(sensor_data.accel_x,2) + pow(sensor_data.accel_y,2) + pow(sensor_data.accel_z,2)); //
					PRINTF("ACCEL %d\n\r", accel_scalar);
					
					uint16_t movement = 0;
					if(accel_scalar < 500 || accel_scalar > 1500) movement = 1;
					
					
					humidity    = (uint16_t)(sensor_data.humidity * 10);            /* in %*10     */
					sprintf(temp, "ID%d N%d M%d T%d P%d H%d ax%d ay%d az%d", lora_ID, ++sequence_num, movement, temperature, pressure, humidity, \
					sensor_data.accel_x, sensor_data.accel_y, sensor_data.accel_z);
					PRINTF("%s\n\r", temp);
					len = strlen(temp);
					#endif

					for(int i=0; i<len; i++)
					{
						Buffer[i] = temp[i];
					}
					
          // We fill the buffer with numbers for the payload
          for (i = len; i < BufferSize; i++)
          {
						Buffer[i] = i - len;
          }
					DelayMs(3000);
					Radio.Send(Buffer, BufferSize);
				}
        
        State = LOWPOWER;
        break;
      case RX:
        Radio.Rx(RX_TIMEOUT_VALUE);
        State = LOWPOWER;
        break;
      case RX_TIMEOUT:
				State = RX;
				break;
      case RX_ERROR:
				State = RX; // return to listening
				break;
 
      case TX_TIMEOUT:
        Radio.Rx(RX_TIMEOUT_VALUE);
        State = LOWPOWER;
        break;
      case LOWPOWER:
      default:
        // Set low power
        break;
    }

    DISABLE_IRQ();
    /* if an interupt has occured after __disable_irq, it is kept pending
     * and cortex will not enter low power anyway  */
    if (State == LOWPOWER)
    {
#ifndef LOW_POWER_DISABLE
      LPM_EnterLowPower();
#endif
    }
    ENABLE_IRQ();
  }
}

void OnTxDone(void)
{
  Radio.Sleep();
  State = TX; // Only for sending
  PRINTF("OnTxDone\n\r");
}

void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr)
{
  Radio.Sleep();
  BufferSize = size;
  memcpy(Buffer, payload, BufferSize);
  RssiValue = rssi;
  SnrValue = snr;
  State = RX; // Only for listening

	PRINTF("%s\n\r", Buffer);
  PRINTF("OnRxDone\n\r");
  //PRINTF("RssiValue=%d dBm, SnrValue=%d\n\r", rssi, snr);
}

void OnTxTimeout(void)
{
  Radio.Sleep();
  State = TX_TIMEOUT;

  PRINTF("OnTxTimeout\n\r");
}

void OnRxTimeout(void)
{
  Radio.Sleep();
  State = RX_TIMEOUT;
  //PRINTF("OnRxTimeout\n\r");
}

void OnRxError(void)
{
  Radio.Sleep();
  State = RX_ERROR;
  PRINTF("OnRxError\n\r");
}

static void OnledEvent(void *context)
{
  LED_Toggle(LED_BLUE) ;
  LED_Toggle(LED_RED1) ;
  LED_Toggle(LED_RED2) ;
  LED_Toggle(LED_GREEN) ;

  TimerStart(&timerLed);
}


