"""Module for IQ option websocket."""
from typing import Any, Dict

def order(api, message: Dict[str, Any]):
    if message["name"] == "order":
        api.order_data = message
