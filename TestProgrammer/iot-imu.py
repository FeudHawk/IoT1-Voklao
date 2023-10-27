from imu import MPU6050  # https://github.com/micropython-IMU/micropython-mpu9x50
import time
from time import sleep,
from machine import Pin, I2C
i2c = I2C(0)
imu = MPU6050(i2c)
current_tacklinger = 1
acceleration = imu.accel


def tacklinger():
    global current_tacklinger
    accel1 = abs(acceleration.y)
    sleep(0.1)
    accel2 = abs(acceleration.y)
    
    if accel1 < 0.6 and accel2 > 1.5:
        current_tacklinger += 1
    
    return current_tacklinger

while True:
#    print(abs(acceleration.y))
    print("Antal tacklinger er:", tacklinger())

        

    