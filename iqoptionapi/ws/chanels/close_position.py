import datetime
import time
from iqoptionapi.ws.chanels.base import Base
from random import randint


class Close_position(Base):
    name = "sendMessage"
    def __call__(self,position_id):
        data = {
            "name":"close-position",
            "version":"1.0",
            "body":{
                "position_id":position_id
                }
        }
        request_id = str(randint(0, 100000))
        try:
            self.api.register_pending(request_id)
        except Exception:
            pass
        self.send_websocket_request(self.name, data, request_id)
        return request_id
 
