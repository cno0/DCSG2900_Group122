"""Decode Protobuf gateway events."""

import logging

from chirpstack_api.gw import gw_pb2
from google.protobuf.json_format import MessageToDict

log = logging.getLogger(__name__)

# Maps the event type (last part of the topic) to its Protobuf class.
GATEWAY_MESSAGES = {
    "up": gw_pb2.UplinkFrame,
    "stats": gw_pb2.GatewayStats,
    "ack": gw_pb2.DownlinkTxAck,
    "down": gw_pb2.DownlinkFrame,
}

def decode_gateway_event(event_type: str, payload: bytes) -> dict | None:
    """
    Decode a Protobuf-encoded gateway event into a dict. 

    Returns None if the event type is unknown or decoding fails.
    """
    message_class = GATEWAY_MESSAGES.get(event_type)
    if message_class is None:
        log.debug("Unknown gateway event type: %s", event_type)
        return None
    try:
        message = message_class()
        message.ParseFromString(payload)
        return MessageToDict(message)
    except Exception as e:
        log.warning("Failed to decode gateway %s event: %s", event_type, e)
        return None
