"""Module for IQ option websocket."""
from typing import Any, Dict

def candles(api, message: Dict[str, Any]):
    if message['name'] == 'candles':
        try:
            api.candles.candles_data = message["msg"]["candles"]
        except:
            pass
