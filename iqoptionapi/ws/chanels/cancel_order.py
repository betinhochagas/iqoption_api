import datetime
import time
from iqoptionapi.ws.chanels.base import Base
from random import randint


class Cancel_order(Base):
    name = "sendMessage"
    def __call__(self,order_id):
        data = {
            "name":"cancel-order",
            "version":"1.0",
            "body":{
                "order_id":order_id
                }
        }
        request_id = str(randint(0, 100000))
        try:
            self.api.register_pending(request_id)
        except Exception:
            pass
        self.send_websocket_request(self.name, data, request_id)
        return request_id
 
