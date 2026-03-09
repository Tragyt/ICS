# Fully Virtualized – Insecure Environment

This configuration represents a fully virtualized Industrial Control System (ICS) network without security mechanisms.
All components are deployed as Docker containers connected through a Docker network.

## Architecture

### HIL (Hardware-in-the-Loop)

**Python** script that simulates a robotic arm as a **Modbus TCP** client, which executes commands read from the PLC.

### PLC (Programmable Logic Controller)

**OpenPLC** instance, including a **Modbus TCP** server (**OpenPLC runtime**) and a web interface for configuration and monitoring.

The web interfaces can be accessed at the following URLs:

- PLC1: http://localhost:8081
- PLC2: http://localhost:8082
- PLC3: http://localhost:8083
- PLC4: http://localhost:8084

### SCADA (Supervisory Control and Data Acquisition)

**ScadaBR** web interface that monitors and interacts with all PLC variables in real-time.

The web interface can be accessed at:

- http://localhost:8080/ScadaBR

## Network

```mermaid
flowchart TB

subgraph ICS Network

SCADA[SCADA]

direction LR

PLC1[PLC1]
HIL1[HIL1]
HIL1 --> PLC1
PLC1 --- HIL1

PLC2[PLC2]
HIL2[HIL2]
HIL2 --> PLC2
PLC2 --- HIL2

PLC3[PLC3]
HIL3[HIL3]
HIL3 --> PLC3
PLC3 --- HIL3

PLC4[PLC4]
HIL4[HIL4]
HIL4 --> PLC4
PLC4 --- HIL4

end

SCADA --> PLC1
SCADA --> PLC2
SCADA --> PLC3
SCADA --> PLC4

linkStyle 1 stroke: transparent
linkStyle 3 stroke: transparent
linkStyle 5 stroke: transparent
linkStyle 7 stroke: transparent
```

## Running the Environment

### Prerequisites

* Docker
* Docker Compose

### Configuration

To run this configuration, switch to the virtual unsecure environment branch:
```bash
git checkout unsafe-env
```

Set up the `.env` file:
```bash
mv .env.example .env
```

The following environment variables are the most important for the configuration:
- `OPENPLC_ADMIN` – **OpenPLC** webserver admin username, default: `openplc`. Change this only if modified through the web interface
- `OPENPLC_PASSWORD` – **OpenPLC** webserver admin password, default: `openplc`. Change this only if modified through the web interface

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