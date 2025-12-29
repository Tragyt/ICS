import time
import os

from pyModbusTCP.client import ModbusClient

PLC_ADDRESS = 'ziti' + '.plc' + os.environ['plc']
client = ModbusClient(PLC_ADDRESS, 502)

def start_plc():
    client.write_single_coil(0, True)
    time.sleep(0.5)  # start input
    client.write_single_coil(0, False)
    print(PLC_ADDRESS + " started")


def rise_arm():
    print("Rising arm...")
    client.write_single_coil(7, False)  # unset down limit
    time.sleep(2)
    client.write_single_coil(5, True)  # set up limit
    print("Up limit reached")


def lower_arm():
    print("Lowering arm...")
    client.write_single_coil(5, False)  # unset up limit
    time.sleep(2)
    client.write_single_coil(7, True)  # set down limit
    print("Down limit reached")


def work():
    print("Working...")
    time.sleep(5)
    client.write_single_coil(10, True)
    time.sleep(0.5)  # finish input
    client.write_single_coil(10, False)
    print("Work finished")

while not client.open():
    print("waiting for " + PLC_ADDRESS + "...")
    time.sleep(0.5)

while True:
    try:
        client.read_coils(2, 1)[0]
        break
    except:
        pass

start_plc()
while client.open():
    run = client.read_coils(2, 1)[0]
    if run:
        rise_arm_signal = client.read_coils(11, 1)[0]
        up_limit_signal = client.read_coils(5, 1)[0]
        if rise_arm_signal and not up_limit_signal:
            rise_arm()

        working_signal = client.read_coils(9, 1)[0]
        if working_signal:
            work()

        lower_arm_signal = client.read_coils(8, 1)[0]
        down_limit_signal = client.read_coils(7, 1)[0]
        if lower_arm_signal and not down_limit_signal:
            lower_arm()

        work_finished_signal = client.read_coils(4, 1)[0]
        piece_available_signal = client.read_coils(6, 1)[0]
        if not work_finished_signal and up_limit_signal and not piece_available_signal:
            print("Waiting for piece...")
            time.sleep(2)
            client.write_single_coil(3, True)  # set piece ready
            print("Piece arrived")

        if work_finished_signal and up_limit_signal and piece_available_signal:
            client.write_single_coil(3, False)  # unset piece ready
            print("Piece gone")

    time.sleep(0.5)
