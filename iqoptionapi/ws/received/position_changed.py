"""Module for IQ option websocket."""

def position_changed(api, message):
    if message["name"] == "position-changed":
        src = message.get("msg", {}).get("source")
        micro = message.get("microserviceName")
        if micro == "portfolio" and src in ("digital-options", "trading"):
            api.order_async[int(message["msg"]["raw_event"]["order_ids"][0])][message["name"]] = message
        elif micro == "portfolio" and src == "binary-options":
            api.order_async[int(message["msg"]["external_id"])][message["name"]] = message
        else:
            api.position_changed = message
