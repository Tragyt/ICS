# Fully Virtualized – Secure Environment

This configuration represents a secured version on the fully virtualized Industrial Control System (ICS) network.
All components are deployed as Docker containers connected through a Docker network.

## Security improvements

The following security components are implemented in the environment:

- **OpenZiti** – provides a Zero Trust overlay network that authenticates, authorizes and encrypts all communications within the network.

- **WebAuthn** – enables passwordless authentication for management interfaces using passkeys stored on mobile devices.

    > **Note:** WebAuthn authentication has been tested with Google Chrome.

## Architecture

### HIL (Hardware-in-the-Loop)

**Python** script that simulates a robotic arm as a **Modbus TCP** client, which executes commands read from the PLC.

### PLC (Programmable Logic Controller)

**OpenPLC** instance, including a **Modbus TCP** server (**OpenPLC runtime**) and a web interface for configuration and monitoring.

### SCADA (Supervisory Control and Data Acquisition)

**ScadaBR** web interface that monitors all PLC variables in real-time.

