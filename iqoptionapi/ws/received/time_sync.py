"""Module for IQ option websocket."""
from typing import Any, Dict

def time_sync(api, message: Dict[str, Any]):
    if message["name"] == "timeSync":
        api.timesync.server_timestamp = message["msg"]
