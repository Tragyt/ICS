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

### Userhandler

**Flask** web interface for user registration, only `admin`user can access this service. The registration flow requires specifying a username for the new user, the registration is then completed by scanning a QR code with a smartphone to store the passkey on the device. 

   > **Note:** During the first login, the token specified in `.env` file is required for register the `admin` user.

### Logingateway

**Flask** web interface for user authentication through **WebAuthn**. The login flow requires an user to enther his username, the login is then completed by scanning a QR code with a smartphone to authenticate via passkey.

### OpenZiti

The **OpenZiti** Zero Trust overlay network is composed of the following components:

- **Ziti Controller** – responsible for authentication and authorization for every connection in the network, it configures a PKI (Public Key Infrastructure) used to create TLS (Transport Layer Security ) network connections between any two pieces of the network.

- **Ziti Router** – responsible for securely and reliably delivering traffic from one network node to destination, it is the entry point to the network for clients connections.

- **Ziti Tunnelers** – components aware of the Ziti network, are configured as sidecar containers for each client and service. Service side tunnelers are registered on the network with a name address, Client side tunnelers provide acces to registered services.