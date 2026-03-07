import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

inPin=21

GPIO.setup(inPin,GPIO.IN)

try:
        while True:
                if GPIO.input(inPin)==0:
                        print("NOPE")
                else:
                	print("YES")
except KeyboardInterrupt:
        GPIO.cleanup()