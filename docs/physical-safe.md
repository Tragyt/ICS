# Physical - Environment

This configuration is deployed on a physical Industrial Control System (ICS) simulation, consisting of two robotic arms and two conveyors. Each node of the network runs on a dedicated **Raspberry Pi 4**.

## Architecture

### HIL (Hardware-in-the-Loop)

- **arm** – reads inputs from a PLC through **Modbus TCP** and sends commands to a **Waveshare RoArm-M2-S** robotic arm.
- **conveyor** – reads inputs from a PLC through **Modbus TCP** and sends commands to a **Raspberry Pi Pico** that operates a desktop conveyor belt.
- **color sensor** – sets a flag on a PLC through **Modbus TCP** if the object on the belt is yellow.

### PLC (Programmable Logic Controller)

Each PLC controls a robotic arm and a conveyor belt. 
The PLC runs on a **Raspberry Pi 4** using **OpenPLC** and is connected to a proximity sensor used to detect objects on the conveyor. 

### SCADA (Supervisory Control and Data Acquisition)

A **ScadaBR** web interface that monitors and interacts with all PLC variables in real-time. 
The speed of the conveyors can be configured from this interface.