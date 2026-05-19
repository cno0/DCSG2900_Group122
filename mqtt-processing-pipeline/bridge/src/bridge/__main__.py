"""Entry point for the Python bridge application."""

import logging

from bridge.broker import run
from bridge.config import load_config


def main():
    """Configure logging, load config and connect to the MQTT broker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = load_config()
    logging.info("MQTT broker: %s:%d", config.mqtt_host, config.mqtt_port)
    logging.info("Region: %s", config.region)

    try:
        run(config.mqtt_host, config.mqtt_port, config.region)
    except KeyboardInterrupt: # If Ctrl+C is pressed
        logging.info("Shutting down.")


if __name__ == "__main__":
    main()
