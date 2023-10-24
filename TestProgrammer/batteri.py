from machine import ADC, Pin
from time import sleep

bat_adc = ADC(Pin(34))
bat_adc.atten(ADC.ATTN_11DB)

#Kode tager et gennemsnit af adc værdien og omregner til procent
#Kode inspiration taget fra Bo Hansen, twoway_remote_data.py
def get_battery_percent():
    adc_val = 0
    for i in range(64):
        adc_val += bat_adc.read()
    adc64_val = adc_val >> 6
    bat_percent = (adc64_val - 1500) / 7.3
    return bat_percent

while True:
    print(get_battery_percent())
    sleep(0.3)
    
