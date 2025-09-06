class State:
    def __init__(self):
        # Connection flags
        self.check_websocket_if_connect = None
        self.check_websocket_if_error = False
        self.websocket_error_reason = None
        # Send/receive mutual exclusion flags
        self.ssl_Mutual_exclusion = False
        self.ssl_Mutual_exclusion_write = False
        # Auth/session
        self.SSID = None
        self.balance_id = None

