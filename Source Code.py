from PIL import Image
import base64
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
import math
import cv2
import time
import shutil
import sys
from glob import glob
from subprocess import check_output, CalledProcessError
from servosix import ServoSix
import time
import requests

from urllib.request import urlopen
import spidev # To communicate with SPI devices
from numpy import interp	# To scale values
from servosix import ServoSix

ss = ServoSix()
servo1 = 4 #for gpio 22

url = 'http://iotgecko.com/IOTHit.aspx?id=ali.shahid1@jgc.com&pass=8560&data='

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

red = 14
green = 15
button = 18
buzzer = 5
reset = 2

GPIO.setup(reset,GPIO.IN)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)

GPIO.output(green, True)
GPIO.output(red, True)  

spi = spidev.SpiDev() # Created an object
spi.open(0,0)

def analogInput(channel):
  spi.max_speed_hz = 1350000
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

def check_connectivity_internet():
    try:
        urlopen(url,timeout = 2)
        return True
    except:
        return False

def check_connectivity():
    camera=cv2.VideoCapture(0)
    time.sleep(3)
    request_site = url + '1'
    ret, frame = camera.read()
    time.sleep(1)
    print ('sending sample image')
    cv2.imwrite("pic2.jpeg", frame)
    with open('pic2.jpeg', 'rb') as f:
        en = base64.b64encode(f.read())
    data = {'img':en} 
    r = requests.post(request_site, data= data)
    data = r.text
    time.sleep(0.5)
    print(data)
    if data.find("Label1") > 0:
        index1 = data.find("Label1") + 8
        index2 = data.find("</span>")
        resp = data[index1:index2]
        print(resp)
    time.sleep(1)
    camera.release()

def response():
    req_site = url + '2' #+ '*' + '5' + '*' + '5'
    response = urlopen(req_site,timeout = 10)
    html = str(response.read())
    print (html)
    if html.find ("Label1") > 0:
        
        index1 = html.find("Label1") + 8
        index2 = html.find("</span>")
        resp1 = html[index1:index2]
        print(resp1)
    return resp1

while True:
    GPIO.output(green, True)
    main = 1
    time.sleep(2)
    print("Connecting to\nInternet ...")
    time.sleep(1)
    main = 1
    t1 = datetime.now()
    
    while not check_connectivity_internet():
        t2 = datetime.now()
        delta = t2 - t1
        time_elapse = delta.total_seconds()
        if time_elapse > 10:
            print ("error check you internet connection")
            main = False
            while GPIO.input(reset) == True:
                print('Press reset to\nrestart')
                time.sleep(0.5)
            break
        else:
            main = True

    if main == True:
        check_connectivity()
        print('connected')
        t3 = datetime.now()

    while True:
      GPIO.output(green, False)
      output = analogInput(0) # Reading from CH0
      output2 = analogInput(1)
      print("Input 1: {}, Input 2: {}".format(output,output2))
      time.sleep(0.1)
      if output2 >= 100:
        ss.set_servo(servo1, 130)
        GPIO.output(buzzer, True)
        GPIO.output(red, False)
        check_connectivity()
        time.sleep(1)
      elif output >= 100:
        ss.set_servo(servo1, 30)
        GPIO.output(buzzer, True)
        GPIO.output(red, False)
        check_connectivity()
        time.sleep(1)
      else:
        ss.set_servo(servo1, 75)
        GPIO.output(buzzer, False)
        GPIO.output(red, True)        
        

        
    




