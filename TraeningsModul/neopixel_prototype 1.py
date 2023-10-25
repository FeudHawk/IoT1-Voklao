import umqtt_robust2 as mqtt
from neopixel import NeoPixel
from machine import Pin, Timer
from time import sleep

antal_led = 10
np = NeoPixel(Pin(26, Pin.OUT),antal_led)
pb1 = Pin(4, Pin.IN)
myTimer1 = Timer(1)
myTimer2 = Timer(2)
current_np = 10
    

def set_color(r, g, b): # Vi definere set_color funktionen, så vi kan få neopixel til at lyse i forskellige farver
    for i in range(antal_led):
        np[i] = (r, g, b)
    np.write()
    
def clear(): #Vi definere clear funktionen, så vi kan slukke led'erne på neopixel efter de er tændt
    for i in range(antal_led):
        np[i] = (0, 0, 0)
        np.write()
        
def blink_purple():
    set_color(255, 0, 255) #Farve sat til lilla
    sleep(0.5)
    clear()
    sleep(0.5)
 

def timeout(myTimer2):
    global current_np
    global antal_led
    current_np -= 1
    sleep(0.1)
    antal_led -= 1
    for i in range(antal_led):
        np[i] = (255, 255, 0)
    np[current_np] = (0, 0, 0)
    np.write()

def jhg(myTimer1):
    global antal_led
    antal_led = 10
    set_color(0, 255, 0)
    myTimer2.deinit()
    
while True:
    try:
        if mqtt.besked == "gult kort":
#             sleep(0.5)
#             print("Gult kort")
            set_color(255, 255, 0) #Farve sat til gul
            myTimer2.init(period=6000, mode=Timer.PERIODIC, callback=timeout)
            myTimer1.init(period=60000, mode=Timer.ONE_SHOT, callback=jhg)
        elif mqtt.besked ==  "udskiftning":
            print("Udskiftning")
            for i in range(20):
                blink_purple()
        
        if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
            mqtt.besked = ""
            
        mqtt.sync_with_adafruitIO() # igangsæt at sende og modtage data med Adafruit IO             
        #sleep(1) # Udkommentér denne og næste linje for at se visuelt output
        #print(".", end = '') # printer et punktum til shell, uden et enter        
    
    except KeyboardInterrupt: # Stopper programmet når der trykkes Ctrl + c
        print('Ctrl-C pressed...exiting')
        mqtt.c.disconnect()
        mqtt.sys.exit()