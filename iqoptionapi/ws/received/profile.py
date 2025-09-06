"""Module for IQ option websocket."""
from typing import Any, Dict

def profile(api, message: Dict[str, Any]):
    if message["name"] == "profile":
        api.profile.msg = message["msg"]
        if api.profile.msg != False:
            # ---------------------------
            try:
                api.profile.balance = message["msg"]["balance"]
            except:
                pass
            # Set Default account
            if api.state.balance_id == None:
                for balance in message["msg"]["balances"]:
                    if balance["type"] == 4:
                        api.state.balance_id = balance["id"]
                        break
            try:
                api.profile.balance_id = message["msg"]["balance_id"]
            except:
                pass

            try:
                api.profile.balance_type = message["msg"]["balance_type"]
            except:
                pass

            try:
                api.profile.balances = message["msg"]["balances"]
            except:
                pass
