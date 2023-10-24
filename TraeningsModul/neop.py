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
    if mqtt.besked == "gult kort":
        set_color(0, 255, 255)
            
            