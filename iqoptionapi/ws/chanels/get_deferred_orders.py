from iqoptionapi.ws.chanels.base import Base
import time
 
from random import randint
class GetDeferredOrders(Base):
    
    name = "sendMessage"

    def __call__(self,instrument_type):
     
        data = {"name":"get-deferred-orders",
                "version":"1.0",
                "body":{
                        "user_balance_id":int(self.api.state.balance_id),
                        "instrument_type":instrument_type                 
                     
                        }
                }

        request_id = str(randint(0, 100000))
        try:
            self.api.register_pending(request_id)
        except Exception:
            pass
        self.send_websocket_request(self.name, data, request_id)
        return request_id
