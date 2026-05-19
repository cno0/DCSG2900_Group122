# MQTT Processing Pipeline

The MQTT Processing Pipeline makes it possible to connect a SIEM platform to ChirpStack by collecting data from ChirpStack's MQTT broker. LoRaWAN gateways configured to forward events to ChirpStack using the `LoRa Gateway MQTT Bridge` publishes gateway-level events to the MQTT broker encoded in [Protobuf](https://protobuf.dev/overview/) format, which makes it difficult to connect to a SIEM platform. This pipeline solves the log shipping and Protobuf issue by splitting the solution into two components:

- The **Python bridge** is a Python application packaged as a Docker container that decodes Protobuf encoded messages and republishes the messages as JSON under a new topic called `chirpstack-json`. 

- [Logstash](https://www.elastic.co/docs/reference/logstash) is an open source log shipping tool that has been configured to subscribe to the gateway-layer and application-layer topics and forward the events over GELF/TCP to a SIEM input. 

The pipeline is designed to be modular and flexible. If the configuration is used with a SIEM platform that does not support [GELF](https://go2docs.graylog.org/current/getting_in_log_data/gelf.html), the output format can be changed to another format (e.g. Syslog, HTTP). 

## Structure

The pipeline has the following structure. The `bridge` directory contains everything related to the `Python bridge`. The `logstash` directory contains the Logstash configuration. Both directories contain a Dockerfile for building the services locally.

```
.
├── bridge
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src
│       └── bridge
│           ├── broker.py
│           ├── config.py
│           ├── decoder.py
│           ├── __init__.py
│           └── __main__.py
├── docker-compose.yaml
├── example.env
├── logstash
│   ├── Dockerfile
│   └── pipeline
│       └── logstash.conf
└── README.md
```

## Requirements

- Docker and Docker Compose
- A running ChirpStack MQTT broker reachable at the configured IP and port

> **Note:** The Python bridge container requires a connection to the MQTT broker on startup. If the broker is unreachable, the container will restart until a connection is established.

## Configuration

Create a `.env` file in the root directory with the following variables:

```bash
cp example.env .env
```

The file must contain the following variables:


| Variable  | Default   | Description                   |
| --------- | --------- | ----------------------------- |
| MQTT_HOST | localhost | IP address of the MQTT broker |
| MQTT_PORT | 1883      | Port of the MQTT broker       |
| REGION    | eu868     | ChirpStack region prefix      |

The Logstash pipeline configuration is found in `logstash/pipeline/logstash.conf` and must be updated with the correct broker and SIEM addresses.

## Usage

Start the stack:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop the stack:
```bash
docker-compose down
```