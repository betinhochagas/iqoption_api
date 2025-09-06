"""Module for IQ option websocket."""
from typing import Any, Dict

def position(api, message: Dict[str, Any]):
    if message["name"] == "position":
        api.position = message
