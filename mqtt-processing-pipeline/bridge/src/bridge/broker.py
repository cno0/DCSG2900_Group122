"""Subscribes to gateway events and command topic, and republish them as JSON."""

import json
import logging
import paho.mqtt.client as mqtt
from bridge.decoder import decode_gateway_event

log = logging.getLogger(__name__)

# Prefix for the republished JSON topics.
JSON_PREFIX = "chirpstack-json"


def run(mqtt_host: str, mqtt_port: int, region: str) -> None:
    """Connect to the MQTT broker and start republishing."""
    subscribe_topics = [ # Subscribe to event and command topics
        (f"{region}/gateway/+/event/+", 0),
        (f"{region}/gateway/+/command/+", 0),
    ]

    def on_connect(client, userdata, flags, reason_code, properties=None):
        """Subscribe to topics after successfull broker connection."""
        log.info("Connected to MQTT broker at %s:%d", mqtt_host, mqtt_port)
        client.subscribe(subscribe_topics)
        for topic, _ in subscribe_topics:
            log.info("Subscribed to: %s", topic)

    def on_message(client, userdata, msg):
        """Decode an incoming message and republish it as JSON."""
        parts = msg.topic.split("/")
        message_type = parts[4]
        event = decode_gateway_event(message_type, msg.payload)
        if event is None:
            return
        # Republish under chirpstack-json/gateway/{gw_id}/(event|command)/{type}
        new_topic = f"{JSON_PREFIX}/{'/'.join(parts[1:])}"
        payload = json.dumps(event)
        client.publish(new_topic, payload)
        log.debug("Republished %s -> %s", msg.topic, new_topic)

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_host, mqtt_port)
    client.loop_forever()
