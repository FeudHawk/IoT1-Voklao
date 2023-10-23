#Krav: Løsningen skal som minimum kunne fremvise lokation og batteridata 
#via et online dashboard, med en opdateringsrate på minimum 2 opdateringer i minuttet.

import umqtt_robust2 as mqtt
from machine import UART, ADC, Pin
from time import sleep
from gps_bare_minimum import GPS_Minimum

gps_port = 2 #Det er hardware UART som har tildelt rx 16 og tx 17 på esp32
gps_dataspeed = 9600 #Det er kommunikationshastighed i bits per sekund. 

uart = UART(gps_port, gps_dataspeed) #definere UART til at være GPS porten og dataspeed, det er også de steder UART bliver brugt.
gps = GPS_Minimum(uart)

bat_adc = ADC(Pin(34))
bat_adc.atten(ADC.ATTN_11DB)

def get_adafruit_gps():
    speed, lat, lon = "", "", ""
    
    if gps.recieve_nmea_data(): #nmea dataen er speed, latitude og longitude
        if gps.get_speed() != -999 and gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            speed = str(gps.get_speed()) #definere speed
            lat = str(gps.get_latitude()) #definere latitude
            lon = str(gps.get_longitude()) #definere longtitude
            return speed + "," + lat + "," + lon + "," + "0.0" #0.0 er altitude, adafruit skal bruge værdien selvom vi ikke har den
        else:
            print(f"Venter på GPS DATA - Gå hen til et sted med bedre signal:\nspeed: {speed}\nlatitude: {lat}\nlongtitude: {lon}") #Hvis gps ikke modtager andet data end -999.0 printer den find bedre lokation
            return False
    else:
        return False

#Kode tager et gennemsnit af adc værdien og omregner til procent
#Kode inspiration taget fra Bo Hansen, twoway_remote_data.py   
def get_battery_percent():
    adc_val = 0
    for i in range(64):
        adc_val += bat_adc.read() #lægger 64 adc læsninger sammen
    adc64_val = adc_val >> 6 #dividere med 64
    bat_percent = (adc64_val - 1500) / 7.3 # ADC1500 = 0% og 1% = ADC7.3
    return bat_percent

while True:
    try:
        # Hvis funktionen returnere en string er den True ellers returnere den False
        gps_data = get_adafruit_gps()
        if gps_data: # hvis der er korrekt data så send til adafruit
            print(f'\ngps_data er: {gps_data}')
            sleep(0.1)
            mqtt.web_print(get_adafruit_gps(), 'Shadow02Hunter/feeds/mapfeed/csv')
                
        #For at sende beskeder til andre feeds kan det gøres sådan:
        # mqtt.web_print("Besked til anden feed", DIT_ADAFRUIT_USERNAME/feeds/DIT_ANDET_FEED_NAVN/ )
        #Indsæt eget username og feednavn til så det svarer til dit eget username og feed du har oprettet

        #For at vise lokationsdata på adafruit dashboard skal det sendes til feed med /csv til sidst
        #For at sende til GPS lokationsdata til et feed kaldet mapfeed kan det gøres således:
        #mqtt.web_print(gps_data, 'DIT_ADAFRUIT_USERNAME/feeds/mapfeed/csv')        
        sleep(4) # vent mere end 3 sekunder mellem hver besked der sendes til adafruit
        
        #mqtt.web_print("test1") # Hvis der ikke angives et 2. argument vil default feed være det fra credentials filen      
        #sleep(4)  # vent mere end 3 sekunder mellem hver besked der sendes til adafruit
        if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
            mqtt.besked = ""            
        mqtt.sync_with_adafruitIO() # igangsæt at sende og modtage data med Adafruit IO             
        print(".", end = '') # printer et punktum til shell, uden et enter        
    # Stopper programmet når der trykkes Ctrl + c
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        mqtt.c.disconnect()
        mqtt.sys.exit()
