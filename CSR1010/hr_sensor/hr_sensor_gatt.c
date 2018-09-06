/******************************************************************************
 *  Copyright (C) Cambridge Silicon Radio Limited 2012
 *  Part of uEnergy SDK 2.0.0
 *  2.0.0.0
 *
 *  FILE
 *      hr_sensor_gatt.c
 *
 *  DESCRIPTION
 *      Implementation of the Heart Rate sensor GATT-related routines
 *
 *****************************************************************************/

/*============================================================================*
 *  SDK Header Files
 *============================================================================*/

#include <ls_app_if.h>
#include <gap_app_if.h>
#include <gap_types.h>
#include <ls_err.h>
#include <ls_types.h>
#include <panic.h>
#include <gatt.h>
#include <gatt_uuid.h>
#include <debug.h>


/*============================================================================*
 *  Local Header Files
 *============================================================================*/

#include "hr_sensor.h"
#include "hr_sensor_gatt.h"
#include "app_gatt_db.h"
#include "app_gatt.h"
#include "appearance.h"
#include "gap_service.h"
#include "heart_rate_service.h"
#include "battery_service.h"
#include "heart_rate_service_uuids.h"
#include "battery_uuids.h"

/*============================================================================*
 *  Private Definitions
 *============================================================================*/

/* This constant is used in the main server app to define array that is 
   large enough to hold the advertisement data.
 */
#define MAX_ADV_DATA_LEN                                  (31)

/* Acceptable shortened device name length that can be sent in advertisement 
 * data 
 */
#define SHORTENED_DEV_NAME_LEN                            (8)

 /* Lenght of Tx Power prefixed with 'Tx Power' AD Type */
#define TX_POWER_VALUE_LENGTH                             (2)

/*============================================================================*
 *  Private Function Prototypes
 *============================================================================*/

static void addDeviceNameToAdvData(uint16 adv_data_len, uint16 scan_data_len);
static void gattSetAdvertParams(bool fast_connection);
static void gattAdvertTimerHandler(timer_id tid);

/*============================================================================*
 *  Private Function Implementations
 *============================================================================*/

/*----------------------------------------------------------------------------*
 *  NAME
 *      addDeviceNameToAdvData
 *
 *  DESCRIPTION
 *      This function is used to add device name to advertisement or scan 
 *      response data. It follows below steps:
 *      a. Try to add complete device name to the advertisment packet
 *      b. Try to add complete device name to the scan response packet
 *      c. Try to add shortened device name to the advertisement packet
 *      d. Try to add shortened (max possible) device name to the scan 
 *         response packet
 *
 *  RETURNS
 *      Nothing.
 *
 *---------------------------------------------------------------------------*/

static void addDeviceNameToAdvData(uint16 adv_data_len, uint16 scan_data_len)
{

    uint8 *p_device_name = NULL;
    uint16 device_name_adtype_len;

    /* Read device name along with AD Type and its length */
    p_device_name = GapGetNameAndLength(&device_name_adtype_len);

    /* Add complete device name to Advertisement data */
    p_device_name[0] = AD_TYPE_LOCAL_NAME_COMPLETE;

    /* Increment device_name_length by one to account for length field
     * which will be added by the GAP layer. 
     */

    /* Check if Complete Device Name can fit in remaining advertisement 
     * data space 
     */
    if((device_name_adtype_len + 1) <= (MAX_ADV_DATA_LEN - adv_data_len))
    {
        /* Add Complete Device Name to Advertisement Data */
        if (LsStoreAdvScanData(device_name_adtype_len , p_device_name, 
                      ad_src_advertise) != ls_err_none)
        {
            ReportPanic(app_panic_set_advert_data);
        }

    }
    /* Check if Complete Device Name can fit in Scan response message */
    else if((device_name_adtype_len + 1) <= (MAX_ADV_DATA_LEN - scan_data_len)) 
    {
        /* Add Complete Device Name to Scan Response Data */
        if (LsStoreAdvScanData(device_name_adtype_len , p_device_name, 
                      ad_src_scan_rsp) != ls_err_none)
        {
            ReportPanic(app_panic_set_scan_rsp_data);
        }

    }
    /* Check if Shortened Device Name can fit in remaining advertisement 
     * data space 
     */
    else if((MAX_ADV_DATA_LEN - adv_data_len) >=
            (SHORTENED_DEV_NAME_LEN + 2)) /* Added 2 for Length and AD type 
                                           * added by GAP layer
                                           */
    {
        /* Add shortened device name to Advertisement data */
        p_device_name[0] = AD_TYPE_LOCAL_NAME_SHORT;

       if (LsStoreAdvScanData(SHORTENED_DEV_NAME_LEN , p_device_name, 
                      ad_src_advertise) != ls_err_none)
        {
            ReportPanic(app_panic_set_advert_data);
        }

    }
    else /* Add device name to remaining Scan reponse data space */
    {
        /* Add as much as can be stored in Scan Response data */
        p_device_name[0] = AD_TYPE_LOCAL_NAME_SHORT;

       if (LsStoreAdvScanData(MAX_ADV_DATA_LEN - scan_data_len, 
                                    p_device_name, 
                                    ad_src_scan_rsp) != ls_err_none)
        {
            ReportPanic(app_panic_set_scan_rsp_data);
        }

    }

}


/*----------------------------------------------------------------------------*
 *  NAME
 *      gattSetAdvertParams
 *
 *  DESCRIPTION
 *      This function is used to set advertisement parameters 
 *
 *  RETURNS
 *      Nothing.
 *
 *---------------------------------------------------------------------------*/

static void gattSetAdvertParams(bool fast_connection)
{
    uint8 advert_data[MAX_ADV_DATA_LEN];
    uint16 length;
    uint32 adv_interval_min = RP_ADVERTISING_INTERVAL_MIN;
    uint32 adv_interval_max = RP_ADVERTISING_INTERVAL_MAX;

    int8 tx_power_level = 0xff; /* Signed value */

    /* Tx power level value prefixed with 'Tx Power' AD Type */
    uint8 device_tx_power[TX_POWER_VALUE_LENGTH] = {
                AD_TYPE_TX_POWER
                };

    uint8 device_appearance[ATTR_LEN_DEVICE_APPEARANCE + 1] = {
                AD_TYPE_APPEARANCE,
                LE8_L(APPEARANCE_HR_SENSOR_VALUE),
                LE8_H(APPEARANCE_HR_SENSOR_VALUE)
                };

    /* A variable to keep track of the data added to AdvData. The limit is 
     * MAX_ADV_DATA_LEN. GAP layer will add AD Flags to AdvData which 
     * is 3 bytes. Refer BT Spec 4.0, Vol 3, Part C, Sec 11.1.3.
     */
    uint16 length_added_to_adv = 3;

    if(fast_connection)
    {
        adv_interval_min = FC_ADVERTISING_INTERVAL_MIN;
        adv_interval_max = FC_ADVERTISING_INTERVAL_MAX;
    }

    /* In a Public Environment like Gym, there is a requirement for HR Sensor 
     * to communicate with fitness machines even without having a bond. So, 
     * for HR Sensor application we will not enforce bonding by calling SM 
     * Slave Security Request. Though, we will set HR Sensor's security 
     * capabilities to 'gap_mode_bond_yes' so that we accept bonding if the 
     * collector (like Watch or Cell Phone) would like to bond.
     */

    if((GapSetMode(gap_role_peripheral, gap_mode_discover_general,
                        gap_mode_connect_undirected, 
                        gap_mode_bond_yes,
                        gap_mode_security_unauthenticate) != ls_err_none) ||
       (GapSetAdvInterval(adv_interval_min, adv_interval_max) 
                        != ls_err_none))
    {
        ReportPanic(app_panic_set_advert_params);
    }

    /* Add bonded device to white list.*/
    if((g_hr_data.enable_white_list == TRUE))
    {
        /* Initial case when advertisements are started for Bonded host for 
         * 10 seconds. White list is configured with the Bonded host address
         */
        if(LsAddWhiteListDevice(&g_hr_data.bonded_bd_addr)!=
            ls_err_none)
        {
            ReportPanic(app_panic_add_whitelist);
        }
    }

    /* Reset existing advertising data */
    if(LsStoreAdvScanData(0, NULL, ad_src_advertise) != ls_err_none)
    {
        ReportPanic(app_panic_set_advert_data);
    }

    /* Reset existing scan response data */
    if(LsStoreAdvScanData(0, NULL, ad_src_scan_rsp) != ls_err_none)
    {
        ReportPanic(app_panic_set_scan_rsp_data);
    }

    /* Setup ADVERTISEMENT DATA */

    /* Add UUID list of the services supported by the device */
    length = GetSupported16BitUUIDServiceList(advert_data);

    /* One added for Length field, which will be added to Adv Data by GAP 
     * layer 
     */
    length_added_to_adv += (length + 1);

    if (LsStoreAdvScanData(length, advert_data, 
                        ad_src_advertise) != ls_err_none)
    {
        ReportPanic(app_panic_set_advert_data);
    }

    /* One added for Length field, which will be added to Adv Data by GAP 
     * layer 
     */
    length_added_to_adv += (sizeof(device_appearance) + 1);

    /* Add device appearance to the advertisements */
    if (LsStoreAdvScanData(ATTR_LEN_DEVICE_APPEARANCE + 1, 
        device_appearance, ad_src_advertise) != ls_err_none)
    {
        ReportPanic(app_panic_set_advert_data);
    }

    /* Read tx power of the chip */
    if(LsReadTransmitPowerLevel(&tx_power_level) != ls_err_none)
    {
        /* Reading tx power failed */
        ReportPanic(app_panic_read_tx_pwr_level);
    }

    /* Add the read tx power level to device_tx_power 
      * Tx power level value is of 1 byte 
      */
    device_tx_power[TX_POWER_VALUE_LENGTH - 1] = (uint8 )tx_power_level;

    /* One added for Length field, which will be added to Adv Data by GAP 
     * layer 
     */
    length_added_to_adv += (TX_POWER_VALUE_LENGTH + 1);

    /* Add tx power value of device to the advertising data */
    if (LsStoreAdvScanData(TX_POWER_VALUE_LENGTH, device_tx_power, 
                          ad_src_advertise) != ls_err_none)
    {
        ReportPanic(app_panic_set_advert_data);
    }

    addDeviceNameToAdvData(length_added_to_adv, 0);

}


/*----------------------------------------------------------------------------*
 *  NAME
 *      gattAdvertTimerHandler
 *
 *  DESCRIPTION
 *      This function is used to handle Advertisement timer.expiry.
 *
 *  RETURNS
 *      Nothing.
 *
 *---------------------------------------------------------------------------*/

static void gattAdvertTimerHandler(timer_id tid)
{
    /* Based upon the timer id, stop on-going advertisements */
    if(g_hr_data.app_tid == tid)
    {
        g_hr_data.app_tid = TIMER_INVALID;

        switch(g_hr_data.state)
        {
            case app_state_fast_advertising:
            {
                if((g_hr_data.enable_white_list == TRUE))
                {
                    /* Set advertisement timer for remaining 20 seconds for 
                     * fast connections with out any device in the white 
                     * list.
                     */
                    g_hr_data.advert_timer_value = 
                                    FAST_CONNECTION_ADVERT_TIMEOUT_VALUE - 
                                    BONDED_DEVICE_ADVERT_TIMEOUT_VALUE;
                }
                else
                {
                    /* No advertisement timer for reduced power 
                     * connections 
                     */
                    g_hr_data.advert_timer_value = 
                                SLOW_CONNECTION_ADVERT_TIMEOUT_VALUE;
                }
            }
            /* FALLTHROUGH */

            case app_state_slow_advertising:
                /* Stop on-going advertisements */
                GattStopAdverts();
            break;

            default:
                /* Ignore timer in remaining states */
            break;
        }

    }/* Else ignore timer expiry, could be because of 
      * some race condition */

}


/*============================================================================*
 *  Public Function Implementations
 *============================================================================*/

/*----------------------------------------------------------------------------*
 *  NAME
 *      HandleAccessRead
 *
 *  DESCRIPTION
 *      This function handles read operation on attributes (as received in 
 *      GATT_ACCESS_IND message) maintained by the application and respond 
 *      with the GATT_ACCESS_RSP message.
 *
 *  RETURNS
 *      Nothing
 *
 *---------------------------------------------------------------------------*/

extern void HandleAccessRead(GATT_ACCESS_IND_T *p_ind)
{

    /* For the received attribute handle, check all the services that support 
     * attribute 'Read' operation handled by application.
     */
    DebugWriteString("Call to read\n");

    if(GapCheckHandleRange(p_ind->handle))
    {
        /* Attribute handle belongs to GAP service */
        GapHandleAccessRead(p_ind);
    }
    else if(HeartRateCheckHandleRange(p_ind->handle))
    {
        /* Attribute handle belongs to Heart Rate service */
        HeartRateHandleAccessRead(p_ind);
    }
    else if(BatteryCheckHandleRange(p_ind->handle))
    {
        /* Attribute handle belongs to Battery service */
        BatteryHandleAccessRead(p_ind);
    }
    else
    {
        /* Application doesn't support 'Read' operation on received 
         * attribute handle, hence return 'gatt_status_read_not_permitted'
         * status
         */
        GattAccessRsp(p_ind->cid, p_ind->handle, 
                      gatt_status_read_not_permitted,
                      0, NULL);
    }

}


/*----------------------------------------------------------------------------*
 *  NAME
 *      HandleAccessWrite
 *
 *  DESCRIPTION
 *      This function handles Write operation on attributes (as received in 
 *      GATT_ACCESS_IND message) maintained by the application.
 *
 *  RETURNS
 *      Nothing
 *
 *---------------------------------------------------------------------------*/

extern void HandleAccessWrite(GATT_ACCESS_IND_T *p_ind)
{

    /* For the received attribute handle, check all the services that support 
     * attribute 'Write' operation handled by application.
     */
    DebugWriteString("Call to write\n");
    if(GapCheckHandleRange(p_ind->handle))
    {   
        DebugWriteString("Write Gap\n");
        /* Attribute handle belongs to GAP service */
        GapHandleAccessWrite(p_ind);
    }
    else if(HeartRateCheckHandleRange(p_ind->handle))
    {
        /* Attribute handle belongs to Heart Rate service */
        /*DebugWriteUint8(*p_ind->value);*/
        DebugWriteString("Write HeartRateHandle\n");
        HeartRateHandleAccessWrite(p_ind);

    }
    else if(BatteryCheckHandleRange(p_ind->handle))
    {
        /* Attribute handle belongs to Battery service */
        DebugWriteString("write BatteryHandleRange\n");
        BatteryHandleAccessWrite(p_ind);
    }
    else
    {
        /* Application doesn't support 'Write' operation on received 
         * attribute handle, hence return 'gatt_status_write_not_permitted'
         * status
         */
        DebugWriteString("Write not permitted\n");
        GattAccessRsp(p_ind->cid, p_ind->handle, 
                      gatt_status_write_not_permitted,
                      0, NULL);
    }

}


/*----------------------------------------------------------------------------*
 *  NAME
 *      GattStartAdverts
 *
 *  DESCRIPTION
 *      This function is used to start undirected advertisements and moves to 
 *      ADVERTISING state.
 *
 *  RETURNS
 *      Nothing.
 *
 *---------------------------------------------------------------------------*/

extern void GattStartAdverts(bool fast_connection)
{
    /* Variable 'connect_flags' needs to be updated to have peer address type 
     * if Directed advertisements are supported as peer address type will 
     * only be used in that case. We don't support directed advertisements for 
     * this application.
     */
    uint16 connect_flags = L2CAP_CONNECTION_SLAVE_UNDIRECTED | 
                          L2CAP_OWN_ADDR_TYPE_PUBLIC;

    /* Set UCID to INVALID_UCID */
    g_hr_data.st_ucid = GATT_INVALID_UCID;

    /* Set advertisement parameters */
    gattSetAdvertParams(fast_connection);

    /* If white list is enabled, set the controller's advertising filter policy 
     * to "process scan and connection requests only from devices in the White 
     * List"
     */
    if((g_hr_data.enable_white_list == TRUE) &&
        (!GattIsAddressResolvableRandom(&(g_hr_data.bonded_bd_addr))))
    {
        connect_flags = L2CAP_CONNECTION_SLAVE_WHITELIST |
                       L2CAP_OWN_ADDR_TYPE_PUBLIC;
    }

    /* Start GATT connection in Slave role */
    GattConnectReq(NULL, connect_flags);

    /* Start advertisement timer */
    if(g_hr_data.advert_timer_value)
    {
        TimerDelete(g_hr_data.app_tid);

        /* Start advertisement timer  */
        g_hr_data.app_tid = TimerCreate(g_hr_data.advert_timer_value, TRUE, 
                                        gattAdvertTimerHandler);
    }

}


/*----------------------------------------------------------------------------*
 *  NAME
 *      GattStopAdverts
 *
 *  DESCRIPTION
 *      This function is used to stop on-going advertisements.
 *
 *  RETURNS
 *      Nothing.
 *
 *---------------------------------------------------------------------------*/

extern void GattStopAdverts(void)
{
    GattCancelConnectReq();
}


/*----------------------------------------------------------------------------*
 *  NAME
 *      GetSupported16BitUUIDServiceList
 *
 *  DESCRIPTION
 *      This function prepares the list of supported 16-bit service UUIDs to be 
 *      added to Advertisement data. It also adds the relevant AD Type to the 
 *      starting of AD array.
 *
 *  RETURNS
 *      Return the size AD Service UUID data.
 *
 *---------------------------------------------------------------------------*/

extern uint16 GetSupported16BitUUIDServiceList(uint8 *p_service_uuid_ad)
{
    uint8 i = 0;

    /* Add 16-bit UUID for supported main service  */
    p_service_uuid_ad[i++] = AD_TYPE_SERVICE_UUID_16BIT_LIST;

    p_service_uuid_ad[i++] = LE8_L(UUID_HEART_RATE_SERVICE);
    p_service_uuid_ad[i++] = LE8_H(UUID_HEART_RATE_SERVICE);

    return ((uint16)i);

}


/*------------------------------------------------------------*
 *  NAME
 *      GattIsAddressResolvableRandom
 *
 *  DESCRIPTION
 *      This function checks if the address is resolvable random or not.
 *
 *  RETURNS
 *      Boolean - True (Resolvable Random Address) /
 *                     False (Not a Resolvable Random Address)
 *
 *----------------------------------------------------------*/

extern bool GattIsAddressResolvableRandom(TYPED_BD_ADDR_T *p_addr)
{
    if(p_addr->type != L2CA_RANDOM_ADDR_TYPE || 
       (p_addr->addr.nap & BD_ADDR_NAP_RANDOM_TYPE_MASK)
                                      != BD_ADDR_NAP_RANDOM_TYPE_RESOLVABLE)
    {
        /* This isn't a resolvable private address */
        return FALSE;
    }
    return TRUE;
} 


/*----------------------------------------------------------------------------*
 *  NAME
 *      GattTriggerFastAdverts
 *
 *  DESCRIPTION
 *      This function is used to trigger fast advertisements 
 *
 *  RETURNS
 *      Nothing
 *
 *---------------------------------------------------------------------------*/

extern void GattTriggerFastAdverts(void)
{

    if(g_hr_data.bonded)
    {
        if(!GattIsAddressResolvableRandom(&g_hr_data.bonded_bd_addr))
        {
            /* Enable white list if the device is bonded and the bonded host 
             * doesn't support resolvable random addresses
             */
            g_hr_data.enable_white_list = TRUE;
        }

        g_hr_data.advert_timer_value = BONDED_DEVICE_ADVERT_TIMEOUT_VALUE;
    }
    else
    {
        g_hr_data.advert_timer_value = FAST_CONNECTION_ADVERT_TIMEOUT_VALUE;
    }

    /* Trigger fast conections */
    GattStartAdverts(TRUE);

}


