import json
import os

from time import sleep

import serial

from pyModbusTCP.client import ModbusClient

PLC_ADDRESS = os.environ["PLC_ADDRESS"]

"""
    {"action": "START", "speed":60, "direction":"forward"}
    {"action": "STOP"}
"""

def move_conveyor(ser: serial.Serial, speed):
    if not (speed > 0 and speed <= 100):
        speed = 50
    cmd = {"action": "start", "speed":speed, "direction":"forward"}
    json_cmd = json.dumps(cmd)+"\n"
    ser.write(json_cmd.encode('utf-8'))

def stop_conveyor(ser: serial.Serial):
    cmd = {"action":"stop"}
    json_cmd=json.dumps(cmd)+"\n"
    ser.write(json_cmd.encode('utf-8'))

def read_coil(client, n):
    ret = None
    while ret is None:
        ret = client.read_coils(n,1)
    return ret[0]

def get_speed(client):
    ret = None
    while ret is None:
        ret = client.read_holding_registers(1,1)
    return ret[0]

ser = serial.Serial('/dev/ttyACM0',115200, timeout=1)
client = ModbusClient(PLC_ADDRESS, 502, unit_id=2, timeout=5)
sleep(2)

moving = False
try:
    while not client.open():
        print("waiting for " + PLC_ADDRESS + "...")
        sleep(0.5)
    while True:
        try:
            current_speed = get_speed(client)
            break
        except Exception as e:
            print(e)

    while client.open():
        run = read_coil(client,2)
        if run:
            move = read_coil(client,9)
            speed = get_speed(client)
            if (not moving and move) or speed != current_speed:
                moving = True
                current_speed = speed
                move_conveyor(ser, current_speed)
            elif moving and not move:
                moving = False
                stop_conveyor(ser)
        else:
            stop_conveyor(ser)
        sleep(0.2)
    stop_conveyor(ser)
except Exception as e:
    print(e)



