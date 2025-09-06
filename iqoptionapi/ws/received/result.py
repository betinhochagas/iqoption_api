"""Module for IQ option websocket."""
from typing import Any, Dict

def result(api, message: Dict[str, Any]):
    if message["name"] == "result":
        api.result = message["msg"]["success"]
