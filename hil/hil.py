import serial
import threading
import os
import json

from time import sleep
from enum import Enum

from pyModbusTCP.client import ModbusClient

PLC_ADDRESS = os.environ["PLC_ADDRESS"]
ARM = os.environ["ARM"]
MAX_TORQUE = 500
CLOSE_START = 2.45
STATUS_SLEEP = 0.15
TORQUE_DIFF2 = 17
TORQUE_DIFF1 = 50
MAX_RAD = 2.70

"""
    joint 1 -> base
        3.14 -> verso sinistra
        -3.14 -> verso destra

    joint 2 -> spalla
        1.57 -> verso il basso
        -1.57 -> verso l'alto
    
    joint 3 -> gomito
        3.14 -> basso
        0 -> alto

    joint 4 -> mandibola
        1.08 -> aperta
        3.14 -> chiusa
"""


class Joint(Enum):
    BASE = 1
    SHOULDER = 2
    ELBOW = 3
    JAW = 4


class Braccio:
    _speed = 0
    _acc = 3
    status = {}
    _lock = threading.Lock()

    def __init__(self, port):
        self.ser = serial.Serial(port, 115200, dsrdtr=None)
        self.ser.setRTS(False)
        self.ser.setDTR(False)

        serial_recv_thread = threading.Thread(target=self.read_serial)
        serial_recv_thread.daemon = True
        serial_recv_thread.start()

        self.default_position()
        self.piece_taken = False

    def default_position(self):
        self.open_jaw()
        sleep(0.2)
        self.raise_shoulder()
        sleep(0.2)
        self.raise_elbow()
        sleep(0.2)
        if ARM == "1":
            self.rotate_left()
        else:
            self.rotate_right()
        sleep(0.2)

    def read_serial(self):
        while True:
            data = self.ser.readline().decode('utf-8')
            if data:
                try:
                    parsed = json.loads(data)
                    with self._lock:
                        self.status = parsed
                except json.JSONDecodeError:
                    pass

    def send_command(self, command: str):
        self.ser.write(command.encode() + b'\n')

    def open_jaw(self):
        rad = 2.20
        T = 101
        command = f'{{"T":{T},"joint":{Joint.JAW.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        # {"T":101,"joint":4,"rad":1.60,"spd":0,"acc":3}
        self.send_command(command)

    def object_picked(self, rad: float) -> bool:
        status_command = '{"T":105}'
        self.send_command(status_command)
        sleep(STATUS_SLEEP)
        torque2 = abs(self.status["torH"])
        rad1 = round(abs(self.status["t"]), 2)
        torque1 = torque2

        stall = 0
        last_rad = 0
        while stall < 3 and ((torque1 == 0 or torque2 == 0) or (not abs(rad1-rad) <= 0.02 and abs(torque1 - torque2) <= TORQUE_DIFF2)):
            # print(f"{rad1=}, {rad=}")
            torque1 = torque2
            self.send_command(status_command)
            sleep(STATUS_SLEEP)
            torque2 = abs(self.status["torH"])
            last_rad = rad1
            rad1 = round(abs(self.status["t"]), 2)
            if last_rad == rad1:
                stall += 1
            else:
                stall = 0
            # print(f"{self.status=}")
            print(f"{torque1=},{torque2=}")
            if torque2 > MAX_TORQUE:
                print("TORQUE DANGER!!!")
                self.open_jaw()
                return True
        return (torque2 > 90 and abs(torque1 - torque2) >= TORQUE_DIFF1) or (torque2 > 150 and abs(torque1 - torque2) < TORQUE_DIFF2)

    def close_jaw(self, pick=False):
        rad = CLOSE_START
        T = 101
        command = f'{{"T":{T},"joint":{Joint.JAW.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        self.send_command(command)

        if pick:
            while not self.object_picked(rad):
                rad = round(rad+0.05, 2)
                # print(f"{rad=}")
                if rad > MAX_RAD:
                    print(f"WARING!! {rad=}")
                    rad = MAX_RAD
                    return
                command = f'{{"T":{T},"joint":{Joint.JAW.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
                self.send_command(command)

    def lower_shoulder(self, pose):
        if pose:
            if ARM == "1":
                rad = 0.09
            else:
                rad = 0.14
        else:
            if ARM == "1":
                rad = 0.22
            else:
                rad = 0.28
        T = 101
        command = f'{{"T":{T},"joint":{Joint.SHOULDER.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        # {"T":101,"joint":2,"rad":0.20,"spd":0,"acc":3}
        self.send_command(command)

    def raise_shoulder(self):
        rad = 0
        T = 101
        command = f'{{"T":{T},"joint":{Joint.SHOULDER.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        # {"T":101,"joint":2,"rad":0,"spd":0,"acc":3}
        self.send_command(command)

    def lower_elbow(self, pose):
        if pose:  
            if ARM == "1":
                rad = 2.45
            else:
                rad = 2.57
        else:
            if ARM == "1":
                rad = 2.45
            else:
                rad = 2.59
        T = 101
        command = f'{{"T":{T},"joint":{Joint.ELBOW.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        # {"T":101,"joint":3,"rad":2.48,"spd":0,"acc":3}
        self.send_command(command)

    def raise_elbow(self):
        rad = 1.68
        T = 101
        command = f'{{"T":{T},"joint":{Joint.ELBOW.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        # '{"T":101,"joint":3,"rad":1.68,"spd":0,"acc":3}'
        self.send_command(command)

    def rotate_right(self):
        rad = -1.57
        T = 101
        command = f'{{"T":{T},"joint":{Joint.BASE.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        self.send_command(command)

    def rotate_left(self):
        rad = 1.57
        T = 101
        command = f'{{"T":{T},"joint":{Joint.BASE.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        # '{"T":101,"joint":1,"rad":1.57,"spd":0,"acc":3}'
        self.send_command(command)

    def rotate_back(self):
        rad = -3.14
        T = 101
        command = f'{{"T":{T},"joint":{Joint.BASE.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        self.send_command(command)

    def rotate_front(self):
        rad = 0
        T = 101
        command = f'{{"T":{T},"joint":{Joint.BASE.value},"rad":{rad},"spd":{self._speed},"acc":{self._acc}}}'
        self.send_command(command)

    def wait_position(self):
        command = '{"T":105}'
        self.send_command(command)
        sleep(0.5)
        last_status = self.status
        self.send_command(command)
        sleep(0.5)

        while last_status != self.status:
            last_status = self.status
            self.send_command(command)
            sleep(0.5)
        return

    def close(self):
        self.default_position()
        self.ser.close()


def start_plc(client: ModbusClient):
    client.write_single_coil(0, True)
    sleep(0.5)  # start input
    client.write_single_coil(0, False)
    print(PLC_ADDRESS + " started")


def pick_piece(braccio: Braccio, client: ModbusClient):
    print("picking piece...")
    braccio.lower_shoulder(False)
    braccio.lower_elbow(False)
    braccio.wait_position()

    braccio.close_jaw(True)
    braccio.wait_position()
    braccio.raise_shoulder()
    # braccio.raise_elbow()
    client.write_single_coil(3, True)


def pose_on_conveyor(braccio: Braccio, client: ModbusClient):
    if ARM=="1":
        braccio.rotate_right()
    else:
        braccio.rotate_left()
    braccio.wait_position()

    braccio.lower_shoulder(True)
    braccio.lower_elbow(True)
    braccio.wait_position()

    braccio.open_jaw()
    braccio.wait_position()

    braccio.raise_shoulder()
    braccio.raise_elbow()
    # braccio.rotate_front()

    if ARM=="1":
        braccio.rotate_left()
    else:
        braccio.rotate_right()
    braccio.wait_position()
    client.write_single_coil(3, False)


def pose_on_box(braccio: Braccio, client: ModbusClient):
    #braccio.rotate_left()
    braccio.rotate_back()
    braccio.wait_position()

    braccio.lower_shoulder(True)
    braccio.lower_elbow(True)
    braccio.wait_position()

    braccio.open_jaw()
    braccio.wait_position()

    braccio.raise_shoulder()
    braccio.raise_elbow()
    # braccio.rotate_front()
    braccio.rotate_left()
    braccio.wait_position()
    client.write_single_coil(3, False)

def read_coil(client, n):
    ret = None
    while ret is None:
        ret = client.read_coils(n,1)
    return ret[0]


braccio = Braccio("/dev/ttyUSB0")
client = ModbusClient(PLC_ADDRESS, 502, unit_id=1, timeout=5)
try:
    while not client.open():
        print("waiting for " + PLC_ADDRESS + "...")
        sleep(0.5)

    while True:
        try:
            client.read_coils(2, 1)
            break
        except Exception as e:
            print(e)

    start_plc(client)
    while client.open():
        run = read_coil(client,2)
        if run:
            pick = read_coil(client,4) 
            pose_conveyor = read_coil(client,5) 
            pose_box = read_coil(client,6)
            
            if pick:
                pick_piece(braccio, client)
            elif pose_conveyor:
                pose_on_conveyor(braccio, client)
            elif pose_box:
                pose_on_box(braccio, client)
        sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    braccio.close()

braccio.close()
