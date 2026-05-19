"""
Loads the configuration details from a .env file. 

Reads the MQTT broker IP and port, and the ChirpStack region prefix.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    mqtt_host: str
    mqtt_port: int
    region: str


def _load_env_file(path: str = ".env") -> None:
    """Loads variables from a .env file into os.environ."""
    if not Path(path).is_file():
        return

    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"): # Skip comments
            continue
        key, _, value = line.partition("=") 
        os.environ.setdefault(key.strip(), value.strip()) # Existing variables are not overwritten


def load_config() -> Config:
    """Load broker IP address and port, and ChirpStack region from a .env file."""
    _load_env_file()

    return Config(
        mqtt_host=os.getenv("MQTT_HOST", "localhost"),
        mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
        region=os.getenv("REGION", "eu868"),
    )
