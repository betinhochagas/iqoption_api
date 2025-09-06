"""Module for IQ option websocket."""
from typing import Any, Dict

def order_canceled(api, message: Dict[str, Any]):
    if message["name"] == "order-canceled":
        api.order_canceled = message
