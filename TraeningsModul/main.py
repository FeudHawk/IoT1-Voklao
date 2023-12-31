import tm1637
import _thread
import umqtt_robust2 as mqtt #Dette biblotek henter credentials, som gør det muligt at forbinde ESP32 til internet og Adafruit.
from imu import MPU6050  # https://github.com/micropython-IMU/micropython-mpu9x50
from machine import UART, ADC, Pin, Timer, I2C
from neopixel import NeoPixel
from time import sleep #henter tids bibloteket, som gør det muligt at bruge sleep funktionen.
from gps_bare_minimum import GPS_Minimum #Dette biblotek henter tid og dat, derudover henter den kordinat system til jordkloden, som gør det muligt at indhente latitude, longtitude og speed værdier.

##########################################################

tm_tack = tm1637.TM1637(clk=Pin(32), dio=Pin(33))
tm_bat = tm1637.TM1637(clk=Pin(22), dio=Pin(23))

gps_port = 2 #Det er hardware UART som har tildelt rx 16 og tx 17 på esp32
gps_dataspeed = 9600 #Det er kommunikationshastighed i bits per sekund. 
uart = UART(gps_port, gps_dataspeed) #definere UART til at være GPS porten og dataspeed, det er også de steder UART bliver brugt.
gps = GPS_Minimum(uart)

bat_adc = ADC(Pin(34))
bat_adc.atten(ADC.ATTN_11DB) #Sætter attenuation til 11dB hvilket vil sige at den kan læse mellem 0v og 3,3v

led_amount = 10
current_np = 10
np = NeoPixel(Pin(26, Pin.OUT),led_amount)
yellow_card_timer = Timer(1)
deinit_yellow_card = Timer(2)

class States:
    timeout = False
    no_yellow = True

##########################################################

def get_adafruit_gps():
    speed, lat, lon = "", "", ""  # Initialiser variablerne
    
    if gps.receive_nmea_data():
        # hvis der er kommet end brugbar værdi på alle der skal anvendes
        if gps.get_speed() != 0 and gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0:
            # returnerer data med adafruit gps format
            speed =str(gps.get_speed())
            lat = str(gps.get_latitude())
            lon = str(gps.get_longitude())
            return speed + "," + lat + "," + lon + "," + "0.0" # Adafruit skal bruge altitude, derfor er den sat til 0.0
        else: # hvis ikke både hastighed, latitude og longtitude er korrekte 
            print("Waiting for GPS DATA - Move GPS to place with acces to the sky")
            return False
    else:
        return False
    
##########################################################
#NeoPixel colors

def set_color(r, g, b): # Vi definere set_color funktionen, så vi kan få neopixel til at lyse i forskellige farver
    for i in range(led_amount):
        np[i] = (r, g, b)
    np.write()
    
def clear(): #Vi definere clear funktionen, så vi kan slukke led'erne på neopixel efter de er tændt
    for i in range(led_amount):
        np[i] = (0, 0, 0)
        np.write()
        
def blink_purple():
    set_color(55, 0, 55) #Farve sat til lilla og blink med 1hz
    sleep(0.5)
    clear()
    sleep(0.5)

def timeout(yellow_card_timer): #Definere funktionen timeout ved brug af yellow_card_timer
    global current_np #Brug global variable af current_np
    global led_amount #Brug global variable af antal_led
    current_np -= 1 #Opdaterer current np til en mindre end før
    led_amount -= 1 #Opdaterer total antal led til en mindre end før. Dette gør vi for at sikre os den ikke tænder alle LEDer igen
    for i in range(led_amount): #Tænder alle tilgængelige np
        np[i] = (55, 55, 0) 
    np[current_np] = (0, 0, 0) #Slukker den nuværende np
    np.write() #Sender data til NeoPixel
    sleep(0.1) #Sørger for at den kun kører 1 gang pr. callback

def timeout_over(deinit_yellow_card): #Definere funktionen timeout_over ved brug af deinit_yellow_card
    yellow_card_timer.deinit() #Deinitializer den anden timer så den ikke kører mere
    global led_amount #Brug global variable af antal_led
    led_amount = 10 #Opdatere led_amount tilbage til 10
    set_color(0, 55, 0) #Lyser grønt i 5 sekunder før den går hent til stabil gul
    sleep(5)
    set_color(55, 55, 0)

##########################################################

#Tager et gennemsnit af adc værdien og omregner til procent
#Kode inspiration taget fra Bo Hansen, twoway_remote_data.py   
def get_battery_percent():
    adc_val = 0
    for i in range(64):
        adc_val += bat_adc.read() #lægger 64 adc læsninger sammen
    adc64_val = adc_val >> 6 #dividere med 64
    bat_percent = (adc64_val - 1590) / 7.3 # ADC1590 = 0% og 1% = ADC7.3
    return bat_percent

##########################################################

#Regner antal af tacklinger
def tacklinger():
    i2c = I2C(0) # Assigner i2c til I2C klassen og bruger slot 0 på esp32
    imu = MPU6050(i2c) #Assigner MPU6050 klassen fra imu.py til imu variablen
    current_tacklinger = 0
    while True:
        #Her tager vi to værdier på acceleration på yxz-aksen og sammenligner de absoulute numre. 
        accel_y1 = abs(imu.accel.y)
        accel_x1 = abs(imu.accel.x)
        accel_z1 = abs(imu.accel.z)
        sleep(0.1)
        accel_y2 = abs(imu.accel.y)
        accel_x2 = abs(imu.accel.x)
        accel_z2 = abs(imu.accel.z)
        
        if accel_y1 < 1 and accel_y2 > 1.5:
            current_tacklinger += 1
        elif accel_x1 < 1 and accel_x2 > 1.5:
            current_tacklinger += 1
        elif accel_z1 < 1 and accel_z2 > 1.5:
            current_tacklinger += 1
            
        #Sender vi antal af tacklinger til display
        tm_tack.number(current_tacklinger)     

#Her starter vi funktionen tacklinger i en thread, som gør at den kører selvom vi har sleep i while True løkken
_thread.start_new_thread(tacklinger, ())

##########################################################

while True:
    try:
        gps_data = get_adafruit_gps() #Sætter en variable til at call en funktion
        tm_bat.number(int(get_battery_percent())) #Sender batteridata til display

        if mqtt.besked == "gult kort": #Tjekker om mqtt besked indeholder gult kort
            States.timeout = True #Sætter timeout state til true
            States.no_yellow = False #Sætter no_yellow til false
            set_color(55, 55, 0) #Farve sat til gul
            #Initialzer yellow_card_timer og kører hver minut og kører forevigt. Herefter kører den funktionen timeout
            yellow_card_timer.init(period=60000, mode=Timer.PERIODIC, callback=timeout)
            #Ininitializer deinit_yellow_card timer og kører kun 1 gang efter 10 minutter. Den kalder timeout funktionen
            deinit_yellow_card.init(period=600100, mode=Timer.ONE_SHOT, callback=timeout_over)
         
        #Hvis udskifting er modtaget fra adafruit og vi ikke har fået gult kort, så kun blink lilla 
        if mqtt.besked ==  "udskiftning" and States.no_yellow == True:
            print("Udskiftning")
            for i in range(10):
                blink_purple()
        
        #Hvis udskifting er modtaget fra adafruit og vi har fået gult kort, så blink lilla og sæt den til gul bagefter 
        if mqtt.besked == "udskiftning" and States.timeout == True:
            for i in range(10):
                blink_purple()
                set_color(55, 55, 0)    

##########################################################

        # Hvis funktionen returnere en string er den True ellers returnere den False
        if gps_data: # hvis der er korrekt data så send til adafruit
            print('gps_data er:', gps_data)
            sleep(0.1)
            mqtt.web_print(get_adafruit_gps(), 'Shadow02Hunter/feeds/mapfeed/csv')               
        
        sleep(3) # vent mere end 3 sekunder mellem hver besked der sendes til adafruit  

        mqtt.web_print(get_battery_percent(), 'Shadow02Hunter/feeds/Batteri/csv') #Sender batteridata til adafruit
        
        sleep(3)

        if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
            mqtt.besked = ""            
        mqtt.sync_with_adafruitIO() # igangsæt at sende og modtage data med Adafruit IO             
               
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        mqtt.c.disconnect()
        mqtt.sys.exit()




