# Krav: Løsningen bør kunne fremvise batteriniveau på løsningens hardwaredel.
import tm1637
from time import sleep
from machine import Pin, ADC

tm_bat = tm1637.TM1637(clk=Pin(32), dio=Pin(33))

bat_adc = ADC(Pin(34))
bat_adc.atten(ADC.ATTN_11DB)

#Kode tager et gennemsnit af adc værdien og omregner til procent
#Kode inspiration taget fra Bo Hansen, twoway_remote_data.py
def get_battery_percent():
    adc_val = 0
    for i in range(64):
        adc_val += bat_adc.read()
    adc64_val = adc_val >> 6
    bat_percent = (adc64_val - 1590) / 7.3
    return bat_percent

while True:
    tm_bat.number(int(get_battery_percent()))
    print(get_battery_percent())
    sleep(1)

    
    

