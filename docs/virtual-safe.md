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

A **ScadaBR** web interface that monitors and interacts with all PLC variables in real-time.

### Userhandler

**Flask** web interface for user registration, only `admin`user can access this service. The registration flow requires specifying a username for the new user, the registration is then completed by scanning a QR code with a smartphone to store the passkey on the device. 

The service can be accessed at:

- http://localhost:5000

   > **Note:** During the first login, the token specified in `.env` file is required for register the `admin` user.

### Logingateway

**Flask** web interface for user authentication through **WebAuthn**. The login flow requires an user to enther his username, the login is then completed by scanning a QR code with a smartphone to authenticate via passkey.

### OpenZiti

The **OpenZiti** Zero Trust overlay network is composed of the following components:

- **Ziti Controller** – responsible for authentication and authorization of every connection in the network. It also configures a PKI (Public Key Infrastructure) used to establish TLS (Transport Layer Security) connections between network components.

- **Ziti Router** – responsible for securely and reliably delivering traffic from one network node to another. It acts as the entry point to the overlay network for client connections.

- **Ziti Tunnelers** – components aware of the Ziti network, that are configured as sidecar containers for each client and service. Service-side tunnelers are registered in the network with a name-based address, while client-side tunnelers provide access to those services.

### Nginx

**Nginx** is used as a reverse proxy to redirect unauthenticated users to the **Logingateway** before they can access services in the environment.

Services are accessible through **Nginx** at the following URLs:

- PLC1 – http://localhost:5050/plc1/
- PLC2 – http://localhost:5050/plc2/
- PLC3 – http://localhost:5050/plc3/
- PLC4 – http://localhost:5050/plc4/
- SCADA – http://localhost:5050/ScadaBR/

## Running the Environment

### Prerequisites

* Docker
* Docker Compose

### Configuration

To run this configuration, switch to the virtual secure environment branch:
```bash
git checkout virtual-safe-env
```

Set up the `.env` file:
```bash
mv .env.example .env
```

The following environment variables are the most important for the configuration:
- `OPENPLC_ADMIN` – **OpenPLC** webserver admin username, default: `openplc`. Change this only if modified through the web interface
- `OPENPLC_PASSWORD` – **OpenPLC** webserver admin password, default: `openplc`. Change this only if modified through the web interface
- `ZITI_USER` – **OpenZiti** administrator username
- `ZITI_PWD` – **OpenZiti** administrator password
- `DATABASE_USER` – **PostgreSQL** username for the **WebAuthn** user database
- `DATABASE_PASSWORD` – **PostgreSQL** password for the **WebAuthn** user database
- `SECRET_KEY_GATEWAY` – secret key used by the **Logingateway** for secure sessions
- `SECRET_KEY_USERHANDLER` – secret key used by the **Userhandler** for secure sessions
- `ADMIN_INIT_TOKEN` – token required for `admin` registration on the userhandler on first access

### Execution
    
Start the containers:
```bash
docker compose up -d
```

To stop the environment:
```bash
docker compose down
```

## Logs

If everything is working correctly, each **HIL** container should log the simulated robotic arm actions.

Show all network logs:
```bash
docker compose logs -f
```

Show specific container logs:
```bash
docker compose logs -f <container_name>
```