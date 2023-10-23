#Krav: Løsningen skal som minimum kunne fremvise lokation og batteridata 
#via et online dashboard, med en opdateringsrate på minimum 2 opdateringer i minuttet.

from machine import Pin, ADC, UART
from time import sleep
import umqtt_robust2 as mqtt
from gps_bare_minimum import GPS_Minimum

gps_port = 2
gps_dataspeed = 9600

uart = UART(gps_port, gps_dataspeed)
gps = GPS_Minimum(uart)

bat_adc = ADC(Pin(34))
bat_adc.atten(ADC.ATTN_11DB)
bat_scaling = 4.2 / 2245 # Volt/ADC Værdi

def get_gpsdata():
    speed = lat = lon = None
    if gps.recieve_nmea_data():
        if gps.get_speed() != -999 and gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            speed = str(gps.get_speed())
            lat = str(gps.get_latitude())
            lon = str(gps.get_longitude())
            return speed + "," + lat + "," + lon + "," + "0.0"
        else:
            print(f"GPS data to adafruit not valid:\nspeed: {speed}\nlatitude: {lat}\nlongtitude: {lon}")
            return False
    else:
        return False

#Kode tager et gennemsnit af adc værdien, Kode taget fra Bo Hansen, twoway_remote_data.py
def read_battery_voltage_avg64():      
    adc_val = 0
    for i in range(64):
        adc_val += bat_adc.read()      
    voltage = bat_scaling * (adc_val >> 6) # >> fast divide by 64
    adc2 = adc_val >> 6
    return adc2
    return voltage

def get_battery_percent():
    adc64_val = read_battery_voltage_avg64()
    bat_percent = (adc64_val - 1500) / 7.3
    return bat_percent