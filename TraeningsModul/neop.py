import umqtt_robust2 as mqtt
from neopixel import NeoPixel
from machine import Pin
from time import sleep

n = 12
np = NeoPixel(Pin(26, Pin.OUT),n)

def set_color(r, g, b):
    for i in range(n):
        np[i] = (r, g, b)
    np.write()

while True:
    try:
    
        if mqtt.besked == "gult kort":
            set_color(255, 255, 0)
        
        if len(mqtt.besked) != 0: # Her nulstilles indkommende beskeder
            mqtt.besked = ""
            
        mqtt.sync_with_adafruitIO() # igangsæt at sende og modtage data med Adafruit IO             
        #sleep(1) # Udkommentér denne og næste linje for at se visuelt output
        #print(".", end = '') # printer et punktum til shell, uden et enter        
    
    except KeyboardInterrupt: # Stopper programmet når der trykkes Ctrl + c
        print('Ctrl-C pressed...exiting')
        mqtt.c.disconnect()
        mqtt.sys.exit()
            