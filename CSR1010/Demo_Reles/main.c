/******************************************************************************
 *  Copyright Cambridge Silicon Radio Limited 2012-2014
 *  Part of CSR uEnergy SDK 2.3.0
 *  Application version 2.3.0.0
 *
 *  FILE
 *      main.c
 *
 *  DESCRIPTION
 *      Simple timers example to show Timers usage. This application also
 *      demonstrates how to produce multiple timeouts using a single timer
 *      resource by chaining timer requests.
 *
 ******************************************************************************/

/*============================================================================*
 *  SDK Header Files
 *============================================================================*/
 
#include <main.h>           /* Functions relating to powering up the device */
#include <ls_app_if.h>      /* Link Supervisor application interface */
#include <debug.h>          /* Simple host interface to the UART driver */
#include <timer.h>          /* Chip timer functions */
#include <panic.h>          /* Support for applications to panic */
#include <pio.h>

/*============================================================================*
 *  Private Definitions
 *============================================================================*/
/*Contador para cronometragem dos reles*/
static uint8 countTimer = 0;

/* Number of timers used in this application */
#define MAX_TIMERS 1

/* First timeout at which the timer has to fire a callback */
#define TIMER_TIMEOUT1 (1 * SECOND)

#define PIO_LED0        (10)        /* PIO connected to the LED0 on CSR1000 */
#define PIO_LED1        (4)         /* PIO connected to the LED1 on CSR1000 */

#define PIO_DIR_OUTPUT  ( TRUE )    /* PIO direction configured as output */
#define PIO_DIR_INPUT   ( FALSE )   /* PIO direction configured as input */

/*============================================================================*
 *  Private Data
 *============================================================================*/

/* Declare timer buffer to be managed by firmware library */
static uint16 app_timers[SIZEOF_APP_TIMER * MAX_TIMERS];

/*============================================================================*
 *  Private Function Prototypes
 *============================================================================*/

/* Start timer */
static void startTimer(uint32 timeout, timer_callback_arg handler);

/* Callback after first timeout */
static void timerCallback1(timer_id const id);

/* Callback after second timeout */
static void timerCallback2(timer_id const id);

/* Read the current system time and write to UART */
static void printCurrentTime(void);

/* Convert an integer value into an ASCII string and send to the UART */
static uint8 writeASCIICodedNumber(uint32 value);

/*Start Time café curto.*/
static void startCafeCurto(void);

/*Start Timer café longo*/
static void startCafeLongo(void);

static void ligaCafeteira(uint8 command);

/*============================================================================*
 *  Private Function Implementations
 *============================================================================*/

/*----------------------------------------------------------------------------*
 *  NAME
 *      startCafeCurto
 *
 *  DESCRIPTION
 *      Start a timer para cafe curto
 *
 * PARAMETERS
 *      Nothing
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void ligaCafeteira(uint8 command)
{
   
    if (command == 0) {    
        /* Liga cafeteira */
        PioSet( PIO_LED1, 0x1 );
    } else {
        /* Desliga cafeteira */
        PioSet( PIO_LED1, 0x0 );
    }
}


/*----------------------------------------------------------------------------*
 *  NAME
 *      startCafeCurto
 *
 *  DESCRIPTION
 *      Start a timer para cafe curto
 *
 * PARAMETERS
 *      Nothing
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void startCafeCurto(void)
{
    countTimer = 0;
    
     /* Set LED0 according to bit 0 of desired pattern */
    PioSet( PIO_LED0, 0x1 );
    
    /* Start the first timer */
    startTimer(TIMER_TIMEOUT1, timerCallback1);
    
    
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      startTimer
 *
 *  DESCRIPTION
 *      Start a timer para cafe longo
 *
 * PARAMETERS
 *      Nothing
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void startCafeLongo(void)
{
    countTimer = 0;    
    
    /* Set LED0 according to bit 1 of desired pattern */
    PioSet( PIO_LED0, 0x1 );
    
    /* Start the first timer */
    startTimer(TIMER_TIMEOUT1, timerCallback2);
}


/*----------------------------------------------------------------------------*
 *  NAME
 *      startTimer
 *
 *  DESCRIPTION
 *      Start a timer
 *
 * PARAMETERS
 *      timeout [in]    Timeout period in seconds
 *      handler [in]    Callback handler for when timer expires
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void startTimer(uint32 timeout, timer_callback_arg handler)
{
    /* Now starting a timer */
    const timer_id tId = TimerCreate(timeout, TRUE, handler);
    
    /* If a timer could not be created, panic to restart the app */
    if (tId == TIMER_INVALID)
    {
        DebugWriteString("\r\nFailed to start timer");
        
        /* Panic with panic code 0xfe */
        Panic(0xfe);
    }
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      timerCallback1
 *
 *  DESCRIPTION
 *      This function is called when the timer created by TimerCreate expires.
 *      It creates a new timer that will expire after the second timer interval.
 *
 * PARAMETERS
 *      id [in]     ID of timer that has expired
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void timerCallback1(timer_id const id)
{
    countTimer = countTimer + 1;
   
    /* Report current system time */
    printCurrentTime();
    
    if(countTimer < 5) {    
        /* Now restart the timer for second callback */
        startTimer( TIMER_TIMEOUT1, timerCallback1 );
    } else {
        /* Set LED0 according to bit 0 of desired pattern */
        PioSet( PIO_LED0, 0x0 );

        DebugWriteString( "\r\n" );
        DebugWriteString( " ************FIM*****************" );
    }
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      timerCallback2
 *
 *  DESCRIPTION
 *      This function is called when the timer created by TimerCreate expires.
 *      It creates a new timer that will expire after the first timer interval.
 *
 * PARAMETERS
 *      id [in]     ID of timer that has expired
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void timerCallback2(timer_id const id)
{
    countTimer = countTimer + 1;
    
    /* Report current system time */
    printCurrentTime();
    
    if(countTimer < 10) {    
        /* Now restart the timer for second callback */
        startTimer( TIMER_TIMEOUT1, timerCallback2 );
    } else {

        /* Set LED0 according to bit 1 of desired pattern */
        PioSet( PIO_LED0, 0x0 );
        DebugWriteString( "\r\n" );
        DebugWriteString( " ************FIM*****************" );
    }
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      printCurrentTime
 *
 *  DESCRIPTION
 *      Read the current system time and write to UART.
 *
 * PARAMETERS
 *      None
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
static void printCurrentTime(void)
{
    /* Read current system time */
    const uint32 now = TimeGet32();
    
    /* Report current system time */
    DebugWriteString("\n\nCurrent system time: ");
    writeASCIICodedNumber(now / MINUTE);
    DebugWriteString("m ");
    writeASCIICodedNumber((now % MINUTE)/SECOND);
    DebugWriteString("s\r\n");
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      writeASCIICodedNumber
 *
 *  DESCRIPTION
 *      Convert an integer value into an ASCII encoded string and send to the
 *      UART
 *
 * PARAMETERS
 *      value [in]     Integer to convert to ASCII and send over UART
 *
 * RETURNS
 *      Number of characters sent to the UART.
 *----------------------------------------------------------------------------*/
static uint8 writeASCIICodedNumber(uint32 value)
{
#define BUFFER_SIZE 11          /* Buffer size required to hold maximum value */
    
    uint8  i = BUFFER_SIZE;     /* Loop counter */
    uint32 remainder = value;   /* Remaining value to send */
    char   buffer[BUFFER_SIZE]; /* Buffer for ASCII string */

    /* Ensure the string is correctly terminated */    
    buffer[--i] = '\0';
    
    /* Loop at least once and until the whole value has been converted */
    do
    {
        /* Convert the unit value into ASCII and store in the buffer */
        buffer[--i] = (remainder % 10) + '0';
        
        /* Shift the value right one decimal */
        remainder /= 10;
    } while (remainder > 0);

    /* Send the string to the UART */
    DebugWriteString(buffer + i);
    
    /* Return length of ASCII string sent to UART */
    return (BUFFER_SIZE - 1) - i;
}

/*============================================================================*
 *  Public Function Implementations
 *============================================================================*/

/*----------------------------------------------------------------------------*
 *  NAME
 *      AppPowerOnReset
 *
 *  DESCRIPTION
 *      This user application function is called just after a power-on reset
 *      (including after a firmware panic), or after a wakeup from Hibernate or
 *      Dormant sleep states.
 *
 *      At the time this function is called, the last sleep state is not yet
 *      known.
 *
 *      NOTE: this function should only contain code to be executed after a
 *      power-on reset or panic. Code that should also be executed after an
 *      HCI_RESET should instead be placed in the AppInit() function.
 *
 * PARAMETERS
 *      None
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
void AppPowerOnReset(void)
{
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      AppInit
 *
 *  DESCRIPTION
 *      This user application function is called after a power-on reset
 *      (including after a firmware panic), after a wakeup from Hibernate or
 *      Dormant sleep states, or after an HCI Reset has been requested.
 *
 *      NOTE: In the case of a power-on reset, this function is called
 *      after app_power_on_reset().
 *
 * PARAMETERS
 *      last_sleep_state [in]   Last sleep state
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
void AppInit(sleep_state last_sleep_state)
{
    /* Initialise communications */
    DebugInit(1, NULL, NULL);
    
     /* Set LED0 and LED1 to be controlled directly via PioSet */
    PioSetModes( ( 1UL << PIO_LED0 ) | ( 1UL << PIO_LED1 ), pio_mode_user );
    /* Configure LED0 and LED1 to be outputs */
    PioSetDir( PIO_LED0, PIO_DIR_OUTPUT );
    PioSetDir( PIO_LED1, PIO_DIR_OUTPUT );

    /* Set the LED0 and LED1 to have strong internal pull ups */
    PioSetPullModes( ( 1UL << PIO_LED0 ) | ( 1UL << PIO_LED1 ),
            pio_mode_strong_pull_up );

    DebugWriteString("\r\nInitialising timers");
    TimerInit(MAX_TIMERS, (void *)app_timers);

    /* Report current time */
    printCurrentTime();
    
    uint8 i = 0;
    
    if (i == 0)
        startCafeCurto();
    else
        startCafeLongo();
    
    ligaCafeteira(0);
    
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      AppProcesSystemEvent
 *
 *  DESCRIPTION
 *      This user application function is called whenever a system event, such
 *      as a battery low notification, is received by the system.
 *
 * PARAMETERS
 *      id   [in]   System event ID
 *      data [in]   Event data
 *
 * RETURNS
 *      Nothing
 *----------------------------------------------------------------------------*/
void AppProcessSystemEvent(sys_event_id id, void *data)
{
}

/*----------------------------------------------------------------------------*
 *  NAME
 *      AppProcessLmEvent
 *
 *  DESCRIPTION
 *      This user application function is called whenever a LM-specific event
 *      is received by the system.
 *
 * PARAMETERS
 *      event_code [in]   LM event ID
 *      event_data [in]   LM event data
 *
 * RETURNS
 *      TRUE if the app has finished with the event data; the control layer
 *      will free the buffer.
 *----------------------------------------------------------------------------*/
bool AppProcessLmEvent(lm_event_code event_code, LM_EVENT_T *event_data)
{
    return TRUE;
}
