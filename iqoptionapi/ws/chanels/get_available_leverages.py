import datetime
import time
from iqoptionapi.ws.chanels.base import Base
from random import randint


class Get_available_leverages(Base):
    name = "sendMessage"
    def __call__(self,instrument_type,actives):
        data = {
            "name":"get-available-leverages",
            "version":"2.0",
            "body":{
                "instrument_type":instrument_type,
                "actives":[actives]
                }
        }
        request_id = str(randint(0, 100000))
        try:
            self.api.register_pending(request_id)
        except Exception:
            pass
        self.send_websocket_request(self.name, data, request_id)
        return request_id
 
