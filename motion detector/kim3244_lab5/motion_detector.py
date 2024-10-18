import esp32
import socket
import sys
import os
from machine import Timer, I2C, Pin
import network
from time import sleep
import ubinascii
import machine
import urequests

flag = 0
ACC_X1 = 0x32
ACC_X2 = 0x33
ACC_Y1 = 0x34
ACC_Y2 = 0x35
ACC_Z1 = 0x36
ACC_Z2 = 0x37

CTL   = 0x2D
FORMAT = 0x31
RATE  = 0x2C 

i2c = I2C(1, scl=Pin(23), sda=Pin(22), freq=400000)
addr0 = i2c.scan()[0]
addr1 = i2c.scan()[1]

def do_connect():
    ssid = '무'
    pw = '19980628'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting')
        wlan.connect(ssid, pw)
        while not wlan.isconnected():
            pass
    print('Connected to ', ssid)    
    print('IP Address:', wlan.ifconfig()[0]) 

def readdata():
    api = 'KCQHB4KS8FZHNFCP'
    url = 'https://api.thingspeak.com/channels/1602409/feeds/last.json?api_key=KCQHB4KS8FZHNFCP&results=1'
    get_data = urequests.get(url).json()
    field_1 = get_data['field1']
    global flag
    if  field_1 == 'activate':
        flag = 1
    else:
        flag = 0

def combine_reg(h, l):
    if not h[0] & 0x80:
        return h[0] << 8 | l[0]
    return -(((h[0] ^ 255) << 8) |  (l[0] ^ 255) + 1)

def get_accel(i2c):
    x_h = i2c.readfrom_mem(addr1, ACC_X1, 1)
    x_l = i2c.readfrom_mem(addr1, ACC_X2, 1)
    y_h = i2c.readfrom_mem(addr1, ACC_Y1, 1)
    y_l = i2c.readfrom_mem(addr1, ACC_Y2, 1)
    z_h = i2c.readfrom_mem(addr1, ACC_Z1, 1)
    z_l = i2c.readfrom_mem(addr1, ACC_Z2, 1)

    print("Calibration complete")

    return [(combine_reg(x_h, x_l) /256 * 0.006)*9.80665, (combine_reg(y_h, y_l) /256 *0.04)*9.80665, combine_reg(z_h, z_l) /256*9.80665*0.005]    

def detect(list):
    x = list[0]
    y = list[1]
    z = list[2]
    if x >= 3 or x <= -3 or y >= 3 or y <= -3 or z >= 3 or z <= -3:
        return True
    return False
    
do_connect()
led_green = Pin(14, Pin.OUT)
led_red = Pin(15, Pin.OUT)

tim = Timer(0)
tim.init(period=30000, mode=Timer.PERIODIC, callback = lambda t:readdata())

while True:
    if flag == 1:
        if i2c.readfrom_mem(addr1 , 0x00 , 1)  != b'\xe5':
            print("invalid device")
        i2c.writeto_mem(addr1, FORMAT, b'\x08') 
        i2c.writeto_mem(addr1, RATE, b'\x0d') 
        i2c.writeto_mem(addr1, CTL, b'\x08')
        print("Detector initialized")
        print(get_accel(i2c))
        detected = detect(get_accel(i2c))
        if detected == True:
            led_green.value(0)
            led_red.value(1)
            notifi = urequests.get('https://maker.ifttt.com/trigger/Motion/with/key/bxvcUJPxS8MtPhZeHYvSeP')
            notifi.close()
        else:
            led_green.value(1)
            led_red.value(0)
    else:
        led_green.value(0)
        led_red.value(0)