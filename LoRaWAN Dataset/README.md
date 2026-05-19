# LoRaWAN Dataset
## Overview
This dataset contains logs collected from a LoRaWAN network monitored using Graylog as a SIEM, as part of a bachelor's thesis evaluating SIEM-based detection of backend attacks. The dataset includes normal background traffic and traffic generated during the execution of the following attack scenarios:
 
- Gateway SSH brute-force
- Network server SSH brute-force
- MQTT unauthorized publish
- Exact MQTT replay
- MQTT flood
- Modified MQTT replay and metadata manipulation

## Collection
Logs were collected from four sources and forwarded to Graylog:
 
- **RAK7268CV2 gateway** — system logs forwarded via `logd` over Syslog/TCP
- **ChirpStack VM** — system logs forwarded via `rsyslog` over Syslog/TCP
- **Logstash** — MQTT application events collected by Logstash, which subscribed to ChirpStack MQTT topics and forwarded events to Graylog over GELF/TCP
- **Docker containers** — container logs from ChirpStack and supporting services forwarded via the Docker GELF logging driver over GELF/TCP
All logs were exported from Graylog as a single CSV file covering a 3-hour window on 2026-04-26 (10:56–13:56 UTC), during which all attack scenarios were executed.
 
## Structure
The dataset is a single CSV file containing 338,656 rows and 112 columns. All attack scenarios are contained within the same file alongside normal background traffic.
 
## Usage
 
The dataset can be imported into a SIEM for further analysis. Since Graylog does not support direct CSV import, open-source tools such as Filebeat, Logstash, or NXLog can be used to ship the file into a Graylog Beats input or similar. The same tools can be used with other SIEM platforms.
 
