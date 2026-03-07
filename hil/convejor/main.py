from motorDriver import MotorDriver
import uselect as select
import usys as sys
import json
import time

"""
    {"action": "START", "speed":60, "direction":"forward"}
    {"action": "STOP"}
"""

if __name__ == '__main__':
    m = MotorDriver()
    
#     poller = select.poll()
#     poller.register(sys.stdin.buffer, select.POLLIN)
#     while True:
#         if poller.poll(-1):
#             print(sys.stdin.buffer.readline())
#             m.MotorRun('MA', 'forward', 50)
#             time.sleep(2)
#             m.MotorStop('MA')
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            command = sys.stdin.readline()
            print("[DEBUG] command: ", command)
            
            try:
                data = json.loads(command)
                
                action = data.get("action","").upper()
                if action == "START":
                    speed = int(data["speed"])
                    direction = data["direction"]
                    m.MotorRun('MA', direction, speed)
                elif action == "STOP":
                    m.MotorStop('MA')
                else:
                    print("unknown action ", action)
                    
                print("waiting command...")
            except json.JSONDecodeError:
                print("ERROR: invalid json ", command)
            except KeyError as e:
                print("ERROR: missing json field ", e)
            except Exception as e:
                print("ERROR: ",e)
        time.sleep(0.01)
        
