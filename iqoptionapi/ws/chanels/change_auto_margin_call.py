import datetime
import time
from iqoptionapi.ws.chanels.base import Base
from random import randint
class ChangeAutoMarginCall(Base):
    name = "sendMessage"
    def __call__(self,ID_Name,ID,auto_margin_call):
        data = {
            "name":"change-auto-margin-call",
            "version":"2.0",
            "body":{
                ID_Name: ID,
                "auto_margin_call": bool(auto_margin_call)
            }
        }
        request_id = str(randint(0, 100000))
        try:
            self.api.register_pending(request_id)
        except Exception:
            pass
        self.send_websocket_request(self.name, data, request_id)
        return request_id
 
 
