#!/usr/bin/python
import time
import os

import RPi.GPIO as GPIO

from TCS34725 import TCS34725

from pyModbusTCP.client import ModbusClient

PLC_ADDRESS = os.environ["PLC_ADDRESS"]


def is_yellow(R, G, B) -> bool:
    if R > 150 and G > 150 and B < 120:
        if abs(R - G) < 80:
            return True
    return False


client = ModbusClient(PLC_ADDRESS, 502, unit_id=3, timeout=5)
try:
    while not client.open():
        print("waiting for " + PLC_ADDRESS + "...")
        time.sleep(0.5)

    while True:
        try:
            client.read_coils(2, 1)
            break
        except Exception as e:
            print(e)

    Light = TCS34725(0X29, debug=False)
    if (Light.TCS34725_init() == 1):
        print("TCS34725 initialization error!!")
    else:
        print("TCS34725 initialization success!!")
    time.sleep(2)
    while True:

        Light.Get_RGBData()
        Light.GetRGB888()
        Light.GetRGB565()

        R = Light.RGB888_R
        G = Light.RGB888_G
        B = Light.RGB888_B
        if is_yellow(R, G, B):
            client.write_single_coil(8, True)
            print("YELLOW")
        else:
            client.write_single_coil(8, False)
            
        # print("R: %d " % Light.RGB888_R)
        # print("G: %d " % Light.RGB888_G)
        # print("B: %d " % Light.RGB888_B)
        # print("C: %#x " % Light.C)
        # print("RGB565: %#x " % Light.RG565)
        # print("RGB888: %#x " % Light.RGB888)
        # print("LUX: %d " % Light.Get_Lux())
        # print("CT: %dK " % Light.Get_ColorTemp())
        # print("INT: %d " % Light.GetLux_Interrupt(0xff00, 0x00ff))

except:
    GPIO.cleanup()
    print("\nProgram end")
    exit()
