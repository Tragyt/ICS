# Physical Environment

This configuration is deployed on a physical Industrial Control System (ICS) simulation, consisting of two robotic arms and two conveyors. Each node of the network runs on a dedicated **Raspberry Pi 4**.

## Architecture

### HIL (Hardware-in-the-Loop)

- **arm** – reads inputs from a PLC through **Modbus TCP** and sends commands to a **Waveshare RoArm-M2-S** robotic arm.
- **conveyor** – reads inputs from a PLC through **Modbus TCP** and sends commands to a **Raspberry Pi Pico** that operates a desktop conveyor belt.
- **color sensor** – sets a flag on a PLC through **Modbus TCP** if the object on the belt is yellow.

### PLC (Programmable Logic Controller)

Each PLC controls a robotic arm and a conveyor belt. 
The PLC runs on a **Raspberry Pi 4** using **OpenPLC** and is connected to a proximity sensor used to detect objects on the conveyor. 

The web interfaces can be accessed at:

- http://<rpi_address>:8080

> Replace `<rpi_address>` with the IP address of the **Raspberry Pi** running the PLC service.

### SCADA (Supervisory Control and Data Acquisition)

**ScadaBR** web interface that monitors and interacts with all PLC variables in real-time. 
The speed of the conveyors can be configured from this interface.

The web interface can be accessed at:

- http://<rpi_address>:8080/ScadaBR

> Replace `<rpi_address>` with the IP address of the **Raspberry Pi** running the SCADA service.

### WebAuthn DB

**PostgreSQL** database that runs on a dedicated **Raspberry Pi**. 
It stores user credentials and passkey information for **WebAuthn** authentication and is accessed by the **Userhandler** and the **Logingateway** services.
 
### Userhandler

**Flask** web interface for user registration, only `admin`user can access this service. The registration flow requires specifying a username for the new user, the registration is then completed by scanning a QR code with a smartphone to store the passkey on the device. 

The service can be accessed at:

- http://<rpi_address>:5000

> Replace `<rpi_address>` with the IP address of the **Raspberry Pi** running the **Userhandler** service.

   > **Note:** During the first login, the token specified in `.env` file is required for register the `admin` user.

### Logingateway

**Flask** web interface for user authentication through **WebAuthn**. The login flow requires an user to enter his username, the login is then completed by scanning a QR code with a smartphone to authenticate via passkey.

### OpenZiti

The **OpenZiti** Zero Trust overlay network is composed of the following components:

- **Ziti Controller** – responsible for authentication and authorization of every connection in the network. It also configures a PKI (Public Key Infrastructure) used to establish TLS (Transport Layer Security) connections between network components.

- **Ziti Router** – responsible for securely and reliably delivering traffic from one network node to another. It acts as the entry point to the overlay network for client connections.

- **Ziti Tunnelers** – services aware of the Ziti network installed on devices running clients or services. Service-side tunnelers are registered in the network with a name-based address, while client-side tunnelers provide access to those services.

## Deployment

The physical environment is deployed and configured using **Ansible**.

The `inventory.ini` file defines the nodes of the network and specifies their IP addresses.

### Prerequisites

* Ansible
* ssh
* python

### Restart NTP

Restarts the Network Time Protocol (**NTP**) service on each device to ensure time synchronization, which is critical for TLS communications.

```bash
ansible-playbook -i ansible/inventory.ini ansible/restart_ntp.yaml
```

### Install Dependencies

Installs all dependencies required by each device to run the services.

```bash
ansible-playbook -i ansible/inventory.ini ansible/install_dependencies.yaml
```

### Run the ICS Environment

Starts or stops the environment depending on the selected tag.

#### Insecure Environment

```bash
ansible-playbook -i ansible/inventory.ini ansible/runICS.yaml --tags start
```

#### Secure Environment

```bash
ansible-playbook -i ansible/inventory.ini ansible/runICS.yaml --tags start_secure
```

#### Stop the Environment

```bash
ansible-playbook -i ansible/inventory.ini ansible/runICS.yaml --tags stop
```

Before running the playbooks, ensure that the IP addresses in `inventory.ini` match the IP addresses of the **Raspberry Pi** devices in the network.
