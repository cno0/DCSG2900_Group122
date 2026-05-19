# MQTT Replay Helper for SIEM Detection Testing

Developed for the DSCG2900 bachelor project, Group 122, by Mohammad Rdwan Alhammod, May 2026.

This repository contains `mqtt_replay.py`, a helper script used for controlled MQTT replay testing in a LoRaWAN backend lab environment. The script captures one MQTT message, stores the original payload, optionally modifies selected JSON fields, and republishes the message to an MQTT broker.

The purpose is to generate controlled MQTT events that can be searched and evaluated in Graylog during SIEM detection testing.

## Scope and Safety

This tool operates only at the MQTT/backend level. It does not capture or replay LoRa radio traffic.

Use this script only in controlled lab environments where testing is authorized. The script can publish messages to an MQTT broker and may affect logs, alerts, backend processing, or connected applications.

Generated output files may contain payloads, timestamps, topic names, broker IP addresses, device identifiers, or other lab-specific values. These files should be handled carefully.

## Requirements

The script requires a Linux-based system with:

- Python 3
- `mosquitto_sub`
- `mosquitto_pub`
- `timeout`

Install the required tools on Debian, Kali, or Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 mosquitto-clients coreutils
```

Check that the tools are available:

```bash
python3 --version
mosquitto_sub --help
mosquitto_pub --help
timeout --help
```

## Repository Structure

```text
lorawan-mqtt-replay-lab/
├── README.md
└── scripts/
    └── mqtt_replay.py
```

## Quick Start

Go to the repository folder:

```bash
cd lorawan-mqtt-replay-lab
```

Check the help menu:

```bash
python3 scripts/mqtt_replay.py --help
```

Run an exact replay test:

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --keep-identical
```

Run a modified replay test:

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --set fCnt=9888 \
  --set attack='"test_replay"'
```

The script creates output under:

```text
output/replay_runs/<run-id>/
```

## How the Script Works

The script performs the following steps:

1. Subscribes to the selected MQTT topic filter.
2. Captures the first MQTT message received.
3. Stores the original payload.
4. Optionally modifies selected JSON fields.
5. Republishes the original or modified payload.
6. Stores timestamps and metadata for later analysis.

The script uses `mosquitto_sub` to capture messages and `mosquitto_pub` to publish messages.

## Basic Syntax

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic '<topic-filter>' \
  [options]
```

## Options

### `--broker`

Specifies the MQTT broker IP address.

This option is required.

```bash
--broker <broker-ip>
```

### `--port`

Specifies the MQTT broker port.

Default:

```text
1883
```

Example:

```bash
--port 1883
```

### `--subscribe-topic`

Specifies the MQTT topic filter used to capture one message.

Default:

```text
application/#
```

Example:

```bash
--subscribe-topic 'application/#'
```

Use quotes around topic filters that contain `#` or `+`.

### `--publish-topic`

Specifies the MQTT topic used when republishing the captured message.

If this option is not used, the script republishes to the same topic where the message was captured.

Example:

```bash
--publish-topic 'application/<application-id>/device/<dev-eui>/event/up'
```

### `--timeout`

Specifies how long the script waits for a message before stopping.

Default:

```text
30 seconds
```

Example:

```bash
--timeout 60
```

### `--keep-identical`

Republishes the captured payload without modification.

Example:

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --keep-identical
```

This mode is used for exact MQTT replay testing.

### `--set`

Modifies or adds a JSON field before republishing.

Format:

```bash
--set field.path=value
```

Examples:

```bash
--set fCnt=9888
```

```bash
--set attack='"test_replay"'
```

```bash
--set deviceInfo.devEui='"TEST_DEVICE_EUI"'
```

```bash
--set rxInfo.0.gatewayId='"TEST_GATEWAY_ID"'
```

The script supports nested JSON fields using dot notation. Array values can be accessed with numeric indexes, such as `rxInfo.0.gatewayId`.

String values should be written as JSON strings:

```bash
--set attack='"modified_replay"'
```

Numbers can be written without quotes:

```bash
--set fCnt=9888
```

Boolean values use lowercase JSON syntax:

```bash
--set confirmed=false
```

Do not use `--keep-identical` and `--set` in the same run.

### `--output-dir`

Specifies where output files are stored.

Default:

```text
output/replay_runs
```

Example:

```bash
--output-dir /tmp/mqtt_replay_runs
```

## Examples

### Exact MQTT Replay

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --keep-identical
```

This captures one MQTT event and republishes it without changing the payload. In Graylog, the result can be checked by looking for repeated values such as:

```text
fCnt
data
deduplicationId
topic
timestamp
```

### Modified Replay with Changed Frame Counter

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --set fCnt=9888 \
  --set attack='"modified_replay"'
```

This changes the frame counter and adds a label that can make the test easier to find in Graylog.

### Modified Replay with Changed Device Identifier

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --set deviceInfo.devEui='"TEST_DEVICE_EUI"' \
  --set attack='"modified_device_identity"'
```

### Modified Replay with Changed Gateway Metadata

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --set rxInfo.0.gatewayId='"TEST_GATEWAY_ID"' \
  --set attack='"modified_gateway_metadata"'
```

### Replay to a Specific Topic

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --publish-topic 'application/<application-id>/device/<dev-eui>/event/up' \
  --keep-identical
```

### Store Output Outside the Repository

```bash
python3 scripts/mqtt_replay.py \
  --broker <broker-ip> \
  --subscribe-topic 'application/#' \
  --keep-identical \
  --output-dir /tmp/mqtt_replay_runs
```

## Example Fields That Can Be Modified

The values below are placeholders and should be adapted to the local lab environment.

### Top-Level Fields

```bash
--set deduplicationId='"manual-test-001"'
--set time='"2026-04-26T22:50:00.000000000+00:00"'
--set devAddr='"DEADBEEF"'
--set adr=true
--set dr=5
--set fCnt=999999
--set fPort=85
--set confirmed=false
--set data='"AAAAAA=="'
--set regionConfigId='"eu868"'
--set attack='"valid_looking_replay"'
--set attack_id='"manual-test-001"'
```

### Device Identity Fields

```bash
--set deviceInfo.devEui='"FFFFFFFFFFFFFFFF"'
--set deviceInfo.deviceName='"FAKE-DEVICE"'
--set deviceInfo.deviceProfileName='"Injected-Profile"'
--set deviceInfo.deviceClassEnabled='"CLASS_A"'
--set deviceInfo.applicationName='"TEST-APPLICATION"'
--set deviceInfo.applicationId='"TEST-APPLICATION-ID"'
--set deviceInfo.tenantName='"TEST-TENANT"'
--set deviceInfo.tenantId='"TEST-TENANT-ID"'
```

### Gateway and `rxInfo` Fields

```bash
--set rxInfo.0.gatewayId='"TEST-GATEWAY-ID"'
--set rxInfo.0.rssi=-10
--set rxInfo.0.snr=25.5
--set rxInfo.0.channel=3
--set rxInfo.0.rfChain=1
--set rxInfo.0.uplinkId=999999999
--set rxInfo.0.nsTime='"2026-04-26T22:50:00.000000000+00:00"'
--set rxInfo.0.context='"AAAAAA=="'
```

The `rxInfo.0` notation means that the script modifies the first object inside the `rxInfo` array.

### Location Fields

```bash
--set rxInfo.0.location.source='"GPS"'
--set rxInfo.0.location.latitude=59.9139
--set rxInfo.0.location.longitude=10.7522
--set rxInfo.0.location.altitude=15
```

### `txInfo` Fields

```bash
--set txInfo.frequency=868100000
--set txInfo.modulation.lora.bandwidth=125000
--set txInfo.modulation.lora.spreadingFactor=7
--set txInfo.modulation.lora.codeRate='"CR_4_5"'
```

## Output Files

Each run creates a unique folder:

```text
output/replay_runs/<run-id>/
```

Typical files:

```text
original_payload.json
replay_payload.json
metadata.txt
run_summary.csv
```

`original_payload.json` stores the captured payload.

`replay_payload.json` stores the payload that was republished.

`metadata.txt` stores run information such as broker IP, topics, timestamps, and modification mode.

`run_summary.csv` stores a compact summary of the run.

## Graylog Investigation

Useful search fields in Graylog may include:

```text
fCnt
devEui
deviceInfo.devEui
deduplicationId
data
gatewayId
topic
attack
timestamp
```

Exact replay tests are usually identified by repeated values.

Modified replay tests should be checked by comparing topic, device identifier, frame counter, gateway metadata, and timestamps.

## Limitations

- The script captures only one MQTT message per run.
- The script only modifies JSON payloads.
- If the captured payload is not valid JSON, `--set` will fail.
- The script does not perform LoRa radio capture.
- The script does not bypass MQTT authentication or authorization.
- TLS configuration is not implemented in this version.

## Troubleshooting

### No message is captured

Increase the timeout:

```bash
--timeout 60
```

Check the topic filter:

```bash
--subscribe-topic 'application/#'
```

Check broker reachability:

```bash
ping <broker-ip>
```

Check MQTT subscription manually:

```bash
mosquitto_sub -h <broker-ip> -p 1883 -t 'application/#' -v
```

### Publish fails

Check that the broker IP and port are correct:

```bash
--broker <broker-ip>
--port 1883
```

Check that publishing is allowed on the selected topic.

### JSON modification fails

The captured payload may not be valid JSON. Use exact replay mode instead:

```bash
--keep-identical
```

### String values are not set correctly

Use JSON-style quoting:

```bash
--set attack='"test_label"'
```

not:

```bash
--set attack=test_label
```

## Ethical Use

This script is intended for educational and authorized testing only. It should be used to understand how MQTT replay-like activity appears in backend logs and how SIEM rules can detect or miss such activity.
