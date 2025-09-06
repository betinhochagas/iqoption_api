"""Module for IQ option websocket."""
from typing import Any, Dict

def balances(api, message: Dict[str, Any]):
    if message["name"] == "balances":
        api.balances_raw = message
