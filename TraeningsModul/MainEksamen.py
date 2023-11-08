import tm1637
import _thread
import umqtt_robust2 as mqtt 
from imu import MPU6050  
from machine import UART, ADC, Pin, Timer, I2C
from neopixel import NeoPixel
from time import sleep 
from gps_bare_minimum import GPS_Minimum 

##########################################################

tm_tack = tm1637.TM1637(clk=Pin(32), dio=Pin(33))
tm_bat = tm1637.TM1637(clk=Pin(22), dio=Pin(23))

gps_port = 2 
gps_dataspeed = 9600 
uart = UART(gps_port, gps_dataspeed) 
gps = GPS_Minimum(uart)

bat_adc = ADC(Pin(34))
bat_adc.atten(ADC.ATTN_11DB) 

led_amount = 10
current_np = 10
np = NeoPixel(Pin(26, Pin.OUT),led_amount)
yellow_card_timer = Timer(1)
deinit_yellow_card = Timer(2)

class States:
    timeout = False
    no_yellow = True

##########################################################
#GPS Funktion
def get_adafruit_gps():
    speed, lat, lon = "", "", ""  
    
    if gps.receive_nmea_data():
       
        if gps.get_speed() != 0 and gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0:
            
            speed =str(gps.get_speed())
            lat = str(gps.get_latitude())
            lon = str(gps.get_longitude())
            return speed + "," + lat + "," + lon + "," + "0.0" 
        else: 
            print("Waiting for GPS DATA - Move GPS to place with acces to the sky")
            return False
    else:
        return False
    
##########################################################
#NeoPixel Funktioner

def set_color(r, g, b): 
    for i in range(led_amount):
        np[i] = (r, g, b)
    np.write()
    
def clear(): 
    for i in range(led_amount):
        np[i] = (0, 0, 0)
        np.write()
        
def blink_purple():
    set_color(55, 0, 55) 
    sleep(0.5)
    clear()
    sleep(0.5)

def timeout(yellow_card_timer): 
    global current_np 
    global led_amount 
    current_np -= 1 
    led_amount -= 1 
    for i in range(led_amount): 
        np[i] = (55, 55, 0) 
    np[current_np] = (0, 0, 0) 
    np.write() 
    sleep(0.1) 

def timeout_over(deinit_yellow_card): 
    yellow_card_timer.deinit() 
    global led_amount 
    led_amount = 10 
    set_color(0, 55, 0) 
    sleep(5)
    set_color(55, 55, 0)

##########################################################
#Battri Dunktion


def get_battery_percent():
    adc_val = 0
    for i in range(64):
        adc_val += bat_adc.read() 
    adc64_val = adc_val >> 6 
    bat_percent = (adc64_val - 1590) / 7.3 
    return bat_percent

##########################################################

#Regner antal af tacklinger
def tacklinger():
    i2c = I2C(0) 
    imu = MPU6050(i2c) 
    current_tacklinger = 0
    while True:
        
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
            
        
        tm_tack.number(current_tacklinger)     


_thread.start_new_thread(tacklinger, ())

##########################################################

while True:
    try:
        gps_data = get_adafruit_gps() 
        tm_bat.number(int(get_battery_percent())) 

        if mqtt.besked == "gult kort": 
            States.timeout = True 
            States.no_yellow = False 
            set_color(55, 55, 0) 
            
            yellow_card_timer.init(period=60000, mode=Timer.PERIODIC, callback=timeout)
            
            deinit_yellow_card.init(period=600100, mode=Timer.ONE_SHOT, callback=timeout_over)
         
        
        if mqtt.besked ==  "udskiftning" and States.no_yellow == True:
            print("Udskiftning")
            for i in range(10):
                blink_purple()
        
        
        if mqtt.besked == "udskiftning" and States.timeout == True:
            for i in range(10):
                blink_purple()
                set_color(55, 55, 0)    

##########################################################

        
        if gps_data: 
            print('gps_data er:', gps_data)
            sleep(0.1)
            mqtt.web_print(get_adafruit_gps(), 'Shadow02Hunter/feeds/mapfeed/csv')               
        
        sleep(3)   

        mqtt.web_print(get_battery_percent(), 'Shadow02Hunter/feeds/Batteri/csv') 
        
        sleep(3)

        if len(mqtt.besked) != 0: 
            mqtt.besked = ""            
        mqtt.sync_with_adafruitIO()       
               
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        mqtt.c.disconnect()
        mqtt.sys.exit()




