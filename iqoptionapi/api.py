"""Module for IQ Option API."""

import time
import os
import json
import logging
import threading
import requests
import ssl
import atexit
from collections import deque
from iqoptionapi import errors as api_errors
from threading import Event, Lock
from iqoptionapi.http.login import Login
from iqoptionapi.http.loginv2 import Loginv2
from iqoptionapi.http.logout import Logout
from iqoptionapi.http.login2fa import Login2FA
from iqoptionapi.http.send_sms import SMS_Sender
from iqoptionapi.http.verify import Verify
from iqoptionapi.http.getprofile import Getprofile
from iqoptionapi.http.auth import Auth
from iqoptionapi.http.token import Token
from iqoptionapi.http.appinit import Appinit
from iqoptionapi.http.billing import Billing
from iqoptionapi.http.buyback import Buyback
from iqoptionapi.http.changebalance import Changebalance
from iqoptionapi.http.events import Events
from iqoptionapi.ws.client import WebsocketClient
from iqoptionapi.ws.chanels.get_balances import *

from iqoptionapi.ws.chanels.ssid import Ssid
from iqoptionapi.ws.chanels.subscribe import *
from iqoptionapi.ws.chanels.unsubscribe import *
from iqoptionapi.ws.chanels.setactives import SetActives
from iqoptionapi.ws.chanels.candles import GetCandles
from iqoptionapi.ws.chanels.buyv2 import Buyv2
from iqoptionapi.ws.chanels.buyv3 import *
from iqoptionapi.ws.chanels.user import *
from iqoptionapi.ws.chanels.api_game_betinfo import Game_betinfo
from iqoptionapi.ws.chanels.instruments import Get_instruments
from iqoptionapi.ws.chanels.get_financial_information import GetFinancialInformation
from iqoptionapi.ws.chanels.strike_list import Strike_list
from iqoptionapi.ws.chanels.leaderboard import Leader_Board

from iqoptionapi.ws.chanels.traders_mood import Traders_mood_subscribe
from iqoptionapi.ws.chanels.traders_mood import Traders_mood_unsubscribe
from iqoptionapi.ws.chanels.technical_indicators import Technical_indicators
from iqoptionapi.ws.chanels.buy_place_order_temp import Buy_place_order_temp
from iqoptionapi.ws.chanels.get_order import Get_order
from iqoptionapi.ws.chanels.get_deferred_orders import GetDeferredOrders
from iqoptionapi.ws.chanels.get_positions import *

from iqoptionapi.ws.chanels.get_available_leverages import Get_available_leverages
from iqoptionapi.ws.chanels.cancel_order import Cancel_order
from iqoptionapi.ws.chanels.close_position import Close_position
from iqoptionapi.ws.chanels.get_overnight_fee import Get_overnight_fee
from iqoptionapi.ws.chanels.heartbeat import Heartbeat


from iqoptionapi.ws.chanels.digital_option import *
from iqoptionapi.ws.chanels.api_game_getoptions import *
from iqoptionapi.ws.chanels.sell_option import Sell_Option
from iqoptionapi.ws.chanels.sell_digital_option import Sell_Digital_Option
from iqoptionapi.ws.chanels.change_tpsl import Change_Tpsl
from iqoptionapi.ws.chanels.change_auto_margin_call import ChangeAutoMarginCall

from iqoptionapi.ws.objects.timesync import TimeSync
from iqoptionapi.ws.objects.profile import Profile
from iqoptionapi.ws.objects.candles import Candles
from iqoptionapi.ws.objects.listinfodata import ListInfoData
from iqoptionapi.ws.objects.betinfo import Game_betinfo_data
from iqoptionapi.state import State
from collections import defaultdict
from typing import Any, Dict, Optional, Union


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))


# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised.
# See: https://urllib3.readthedocs.org/en/latest/security.html
# Only disable warnings when explicitly configured as insecure.
if str(os.getenv("IQOPTIONAPI_INSECURE_SSL", "false")).lower() in ("1", "true", "yes"):  # pylint: disable=no-member
    requests.packages.urllib3.disable_warnings()


class IQOptionAPI(object):  # pylint: disable=too-many-instance-attributes
    """Class for communication with IQ Option API."""

    # pylint: disable=too-many-public-methods
    socket_option_opened = {}
    socket_option_closed = {}
    timesync = TimeSync()
    profile = Profile()
    candles = Candles()
    listinfodata = ListInfoData()
    api_option_init_all_result = []
    api_option_init_all_result_v2 = []
    # for digital
    underlying_list_data = None
    position_changed = None
    instrument_quites_generated_data = nested_dict(2, dict)
    instrument_quotes_generated_raw_data = nested_dict(2, dict)
    instrument_quites_generated_timestamp = nested_dict(2, dict)
    strike_list = None
    leaderboard_deals_client = None
    #position_changed_data = nested_dict(2, dict)
    # microserviceName_binary_options_name_option=nested_dict(2,dict)
    order_async = nested_dict(2, dict)
    order_binary = {}
    game_betinfo = Game_betinfo_data()
    instruments = None
    financial_information = None
    buy_id = None
    buy_order_id = None
    traders_mood = {}  # get hight(put) %
    technical_indicators = {}
    order_data = None
    positions = None
    position = None
    deferred_orders = None
    position_history = None
    position_history_v2 = None
    available_leverages = None
    order_canceled = None
    close_position_data = None
    overnight_fee = None
    # ---for real time
    digital_option_placed_id = {}
    live_deal_data = nested_dict(3, deque)

    subscribe_commission_changed_data = nested_dict(2, dict)
    real_time_candles = nested_dict(3, dict)
    real_time_candles_maxdict_table = nested_dict(2, dict)
    candle_generated_check = nested_dict(2, dict)
    candle_generated_all_size_check = nested_dict(1, dict)
    # ---for api_game_getoptions_result
    api_game_getoptions_result = None
    sold_options_respond = None
    sold_digital_options_respond = None
    tpsl_changed_respond = None
    auto_margin_call_changed_respond = None
    top_assets_updated_data = {}
    get_options_v2_data = None
    # --for binary option multi buy
    buy_multi_result = None
    buy_multi_option = {}
    #
    result = None
    training_balance_reset_request = None
    balances_raw = None
    user_profile_client = None
    leaderboard_userinfo_deals_client = None
    users_availability = None
    # ------------------
    digital_payout = None

    def __init__(self, host, username, password, proxies=None):
        """
        :param str host: The hostname or ip address of a IQ Option server.
        :param str username: The username of a IQ Option server.
        :param str password: The password of a IQ Option server.
        :param dict proxies: (optional) The http request proxies.
        """
        self.https_url = "https://{host}/api".format(host=host)
        self.wss_url = "wss://{host}/echo/websocket".format(host=host)
        self.websocket_client = None
        # Instance state (replaces global_value)
        self.state = State()
        # Security configuration toggles
        self.insecure_ssl = str(os.getenv("IQOPTIONAPI_INSECURE_SSL", "false")).lower() in ("1", "true", "yes")
        self.trust_env = str(os.getenv("IQOPTIONAPI_TRUST_ENV", "false")).lower() in ("1", "true", "yes")
        # Timeouts
        try:
            self.default_timeout = float(os.getenv("IQOPTIONAPI_DEFAULT_TIMEOUT", "10"))
        except Exception:
            self.default_timeout = 10.0

        self.session = requests.Session()
        # Verify TLS certificates by default; allow disabling for debug via env
        self.session.verify = False if self.insecure_ssl else True
        # Allow honoring system proxy settings if explicitly enabled
        self.session.trust_env = self.trust_env
        self.username = username
        self.password = password
        self.token_login2fa = None
        self.token_sms = None
        self.proxies = proxies
        # is used to determine if a buyOrder was set  or failed. If
        # it is None, there had been no buy order yet or just send.
        # If it is false, the last failed
        # If it is true, the last buy order was successful
        self.buy_successful = None
        self.__active_account_type = None
        # Pending request management (Phase 2)
        self._pending = {}
        self._pending_lock = Lock()
        # Result events for requests that also emit a separate 'result' message
        self._result_events = {}
        self._result_values = {}
        # WS send queue (Phase 3)
        self._send_queue = deque()
        self._send_cv = threading.Condition()
        try:
            self._send_max = int(os.getenv("IQOPTIONAPI_SEND_QUEUE_MAX", "1000"))
        except Exception:
            self._send_max = 1000
        self._sender_thread = None
        self._sender_stop = False

    # -------- Pending request helpers --------
    def register_pending(self, request_id: Union[str, int]) -> Event:
        ev = Event()
        with self._pending_lock:
            self._pending[str(request_id)] = {"event": ev, "payload": None}
        return ev

    def resolve_pending(self, request_id: Union[str, int], payload: Dict[str, Any]) -> None:
        try:
            key = str(request_id)
            with self._pending_lock:
                entry = self._pending.get(key)
                if entry is not None:
                    entry["payload"] = payload
                    entry["event"].set()
        except Exception:
            pass

    def wait_request(self, request_id: Union[str, int], timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        key = str(request_id)
        with self._pending_lock:
            entry = self._pending.get(key)
        if entry is None:
            return None
        to = timeout if timeout is not None else self.default_timeout
        if not entry["event"].wait(to):
            raise api_errors.TimeoutError(f"Timeout waiting for request_id={key}")
        with self._pending_lock:
            entry = self._pending.pop(key, entry)
        return entry.get("payload")

    # -------- Result helpers (for 'result' messages) --------
    def register_result_wait(self, request_id: Union[str, int]) -> Event:
        ev = Event()
        with self._pending_lock:
            self._result_events[str(request_id)] = ev
        return ev

    def set_result(self, request_id: Union[str, int], success: Any) -> None:
        key = str(request_id)
        with self._pending_lock:
            self._result_values[key] = bool(success)
            ev = self._result_events.get(key)
            if ev:
                ev.set()

    def wait_result(self, request_id: Union[str, int], timeout: Optional[float] = None) -> Optional[bool]:
        key = str(request_id)
        with self._pending_lock:
            ev = self._result_events.get(key)
        if not ev:
            return self._result_values.get(key)
        to = timeout if timeout is not None else self.default_timeout
        if not ev.wait(to):
            return self._result_values.get(key)
        with self._pending_lock:
            val = self._result_values.get(key)
            # cleanup
            self._result_events.pop(key, None)
            self._result_values.pop(key, None)
        return val

    def prepare_http_url(self, resource) -> str:
        """Construct http url from resource url.

        :param resource: The instance of
            :class:`Resource <iqoptionapi.http.resource.Resource>`.

        :returns: The full url to IQ Option http resource.
        """
        return "/".join((self.https_url, resource.url))

    def send_http_request(self, resource, method: str, data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None):  # pylint: disable=too-many-arguments
        """Send http request to IQ Option server.

        :param resource: The instance of
            :class:`Resource <iqoptionapi.http.resource.Resource>`.
        :param str method: The http request method.
        :param dict data: (optional) The http request data.
        :param dict params: (optional) The http request params.
        :param dict headers: (optional) The http request headers.

        :returns: The instance of :class:`Response <requests.Response>`.
        """
        logger = logging.getLogger(__name__)
        url = self.prepare_http_url(resource)

        logger.debug(url)

        try:
            response = self.session.request(method=method,
                                            url=url,
                                            data=data,
                                            params=params,
                                            headers=headers,
                                            proxies=self.proxies)
            logger.debug(response)
            logger.debug(response.text)
            logger.debug(response.headers)
            logger.debug(response.cookies)

            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                raise api_errors.from_http_response(response, e)
            return response
        except requests.RequestException as e:
            raise api_errors.NetworkError(str(e), url=url)

    def send_http_request_v2(self, url: str, method: str, data: Optional[Any] = None,
                             params: Optional[Dict[str, Any]] = None,
                             headers: Optional[Dict[str, str]] = None):  # pylint: disable=too-many-arguments
        """Send http request to IQ Option server.

        :param resource: The instance of
            :class:`Resource <iqoptionapi.http.resource.Resource>`.
        :param str method: The http request method.
        :param dict data: (optional) The http request data.
        :param dict params: (optional) The http request params.
        :param dict headers: (optional) The http request headers.

        :returns: The instance of :class:`Response <requests.Response>`.
        """
        logger = logging.getLogger(__name__)

        logger.debug(method + ": " + url + " headers: " + str(self.session.headers) +
                     " cookies:  " + str(self.session.cookies.get_dict()))

        try:
            response = self.session.request(method=method,
                                            url=url,
                                            data=data,
                                            params=params,
                                            headers=headers,
                                            proxies=self.proxies)
            logger.debug(response)
            logger.debug(response.text)
            logger.debug(response.headers)
            logger.debug(response.cookies)

            # Enforce HTTP error bubbling in v2 as well
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                raise api_errors.from_http_response(response, e)
            return response
        except requests.RequestException as e:
            raise api_errors.NetworkError(str(e), url=url)

    @property
    def websocket(self):
        """Property to get websocket.

        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client.wss

    def send_websocket_request(self, name: str, msg: Dict[str, Any], request_id: Union[str, int] = "",
                               no_force_send: bool = True) -> None:
        """Send websocket request to IQ Option server.

        :param str name: The websocket request name.
        :param dict msg: The websocket request msg.
        """

        logger = logging.getLogger(__name__)

        payload = dict(name=name, msg=msg, request_id=request_id)
        data = json.dumps(payload)

        # Enqueue for sender thread with backpressure
        with self._send_cv:
            start_t = time.time()
            while len(self._send_queue) >= self._send_max:
                # wait a bit for space
                self._send_cv.wait(0.05)
                if time.time() - start_t > self.default_timeout:
                    raise api_errors.TimeoutError("Send queue is full")
            self._send_queue.append(data)
            self._send_cv.notify()
        logger.info("ws_send name=%s req_id=%s", name, request_id)

    @property
    def logout(self):
        """Property for get IQ Option http login resource.

        :returns: The instance of :class:`Login
            <iqoptionapi.http.login.Login>`.
        """
        return Logout(self)

    @property
    def login(self):
        """Property for get IQ Option http login resource.

        :returns: The instance of :class:`Login
            <iqoptionapi.http.login.Login>`.
        """
        return Login(self)

    @property
    def login_2fa(self):
        """Property for get IQ Option http login 2FA resource.

        :returns: The instance of :class:`Login2FA
            <iqoptionapi.http.login2fa.Login2FA>`.
        """
        return Login2FA(self)

    @property
    def send_sms_code(self):
        """Property for get IQ Option http send sms code resource.

        :returns: The instance of :class:`SMS_Sender
            <iqoptionapi.http.send_sms.SMS_Sender>`.
        """
        return SMS_Sender(self)

    @property
    def verify_2fa(self):
        """Property for get IQ Option http verify 2fa resource.

        :returns: The instance of :class:`Verify
            <iqoptionapi.http.verify.Verify>`.
        """
        return Verify(self)

    @property
    def loginv2(self):
        """Property for get IQ Option http loginv2 resource.

        :returns: The instance of :class:`Loginv2
            <iqoptionapi.http.loginv2.Loginv2>`.
        """
        return Loginv2(self)

    @property
    def auth(self):
        """Property for get IQ Option http auth resource.

        :returns: The instance of :class:`Auth
            <iqoptionapi.http.auth.Auth>`.
        """
        return Auth(self)

    @property
    def appinit(self):
        """Property for get IQ Option http appinit resource.

        :returns: The instance of :class:`Appinit
            <iqoptionapi.http.appinit.Appinit>`.
        """
        return Appinit(self)

    @property
    def token(self):
        """Property for get IQ Option http token resource.

        :returns: The instance of :class:`Token
            <iqoptionapi.http.auth.Token>`.
        """
        return Token(self)

    # @property
    # def profile(self):
    #     """Property for get IQ Option http profile resource.

    #     :returns: The instance of :class:`Profile
    #         <iqoptionapi.http.profile.Profile>`.
    #     """
    #     return Profile(self)
    def reset_training_balance(self):
        # sendResults True/False
        # {"name":"sendMessage","request_id":"142","msg":{"name":"reset-training-balance","version":"2.0"}}

        self.send_websocket_request(name="sendMessage", msg={"name": "reset-training-balance",
                                                             "version": "2.0"})

    @property
    def changebalance(self):
        """Property for get IQ Option http changebalance resource.

        :returns: The instance of :class:`Changebalance
            <iqoptionapi.http.changebalance.Changebalance>`.
        """
        return Changebalance(self)

    @property
    def events(self):
        return Events(self)

    @property
    def billing(self):
        """Property for get IQ Option http billing resource.

        :returns: The instance of :class:`Billing
            <iqoptionapi.http.billing.Billing>`.
        """
        return Billing(self)

    @property
    def buyback(self):
        """Property for get IQ Option http buyback resource.

        :returns: The instance of :class:`Buyback
            <iqoptionapi.http.buyback.Buyback>`.
        """
        return Buyback(self)
# ------------------------------------------------------------------------

    @property
    def getprofile(self):
        """Property for get IQ Option http getprofile resource.

        :returns: The instance of :class:`Login
            <iqoptionapi.http.getprofile.Getprofile>`.
        """
        return Getprofile(self)
# for active code ...

    @property
    def get_balances(self):
        """Property for get IQ Option http getprofile resource.

        :returns: The instance of :class:`Login
            <iqoptionapi.http.getprofile.Getprofile>`.
        """
        return Get_Balances(self)

    @property
    def get_instruments(self):
        return Get_instruments(self)

    @property
    def get_financial_information(self):
        return GetFinancialInformation(self)
# ----------------------------------------------------------------------------

    @property
    def ssid(self):
        """Property for get IQ Option websocket ssid chanel.

        :returns: The instance of :class:`Ssid
            <iqoptionapi.ws.chanels.ssid.Ssid>`.
        """
        return Ssid(self)
# --------------------------------------------------------------------------------

    @property
    def Subscribe_Live_Deal(self):
        return Subscribe_live_deal(self)

    @property
    def Unscribe_Live_Deal(self):
        return Unscribe_live_deal(self)
# --------------------------------------------------------------------------------
# trader mood

    @property
    def subscribe_Traders_mood(self):
        return Traders_mood_subscribe(self)

    @property
    def unsubscribe_Traders_mood(self):
        return Traders_mood_unsubscribe(self)

# --------------------------------------------------------------------------------
# tecnical indicators

    @property
    def get_Technical_indicators(self):
        return Technical_indicators(self)

# --------------------------------------------------------------------------------
# --------------------------subscribe&unsubscribe---------------------------------
# --------------------------------------------------------------------------------
    @property
    def subscribe(self):
        "candle-generated"
        """Property for get IQ Option websocket subscribe chanel.

        :returns: The instance of :class:`Subscribe
            <iqoptionapi.ws.chanels.subscribe.Subscribe>`.
        """
        return Subscribe(self)

    @property
    def subscribe_all_size(self):
        return Subscribe_candles(self)

    @property
    def unsubscribe(self):
        """Property for get IQ Option websocket unsubscribe chanel.

        :returns: The instance of :class:`Unsubscribe
            <iqoptionapi.ws.chanels.unsubscribe.Unsubscribe>`.
        """
        return Unsubscribe(self)

    @property
    def unsubscribe_all_size(self):
        return Unsubscribe_candles(self)

    def portfolio(self, Main_Name, name, instrument_type, user_balance_id="", limit=1, offset=0, request_id=""):
        # Main name:"unsubscribeMessage"/"subscribeMessage"/"sendMessage"(only for portfolio.get-positions")
        # name:"portfolio.order-changed"/"portfolio.get-positions"/"portfolio.position-changed"
        # instrument_type="cfd"/"forex"/"crypto"/"digital-option"/"turbo-option"/"binary-option"
        logger = logging.getLogger(__name__)
        M_name = Main_Name
        request_id = str(request_id)
        if name == "portfolio.order-changed":
            msg = {"name": name,
                   "version": "1.0",
                   "params": {
                       "routingFilters": {"instrument_type": str(instrument_type)}
                   }
                   }

        elif name == "portfolio.get-positions":
            msg = {"name": name,
                   "version": "3.0",
                   "body": {
                       "instrument_type": str(instrument_type),
                       "limit": int(limit),
                       "offset": int(offset)
                   }
                   }

        elif name == "portfolio.position-changed":
            msg = {"name": name,
                   "version": "2.0",
                   "params": {
                       "routingFilters": {"instrument_type": str(instrument_type),
                                          "user_balance_id": user_balance_id

                                          }
                   }
                   }

        self.send_websocket_request(
            name=M_name, msg=msg, request_id=request_id)

    def set_user_settings(self, balanceId, request_id=""):
        # Main name:"unsubscribeMessage"/"subscribeMessage"/"sendMessage"(only for portfolio.get-positions")
        # name:"portfolio.order-changed"/"portfolio.get-positions"/"portfolio.position-changed"
        # instrument_type="cfd"/"forex"/"crypto"/"digital-option"/"turbo-option"/"binary-option"

        msg = {"name": "set-user-settings",
               "version": "1.0",
               "body": {
                   "name": "traderoom_gl_common",
                   "version": 3,
                   "config": {
                       "balanceId": balanceId

                   }

               }
               }
        self.send_websocket_request(
            name="sendMessage", msg=msg, request_id=str(request_id))

    def subscribe_position_changed(self, name, instrument_type, request_id):
        # instrument_type="multi-option","crypto","forex","cfd"
        # name="position-changed","trading-fx-option.position-changed",digital-options.position-changed
        msg = {"name": name,
               "version": "1.0",
               "params": {
                   "routingFilters": {"instrument_type": str(instrument_type)}

               }
               }
        self.send_websocket_request(
            name="subscribeMessage", msg=msg, request_id=str(request_id))

    def setOptions(self, request_id, sendResults):
        # sendResults True/False

        msg = {"sendResults": sendResults}

        self.send_websocket_request(
            name="setOptions", msg=msg, request_id=str(request_id))

    @property
    def Subscribe_Top_Assets_Updated(self):
        return Subscribe_top_assets_updated(self)

    @property
    def Unsubscribe_Top_Assets_Updated(self):
        return Unsubscribe_top_assets_updated(self)

    @property
    def Subscribe_Commission_Changed(self):
        return Subscribe_commission_changed(self)

    @property
    def Unsubscribe_Commission_Changed(self):
        return Unsubscribe_commission_changed(self)

# --------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------

    @property
    def setactives(self):
        """Property for get IQ Option websocket setactives chanel.

        :returns: The instance of :class:`SetActives
            <iqoptionapi.ws.chanels.setactives.SetActives>`.
        """
        return SetActives(self)

    @property
    def Get_Leader_Board(self):
        return Leader_Board(self)

    @property
    def getcandles(self):
        """Property for get IQ Option websocket candles chanel.

        :returns: The instance of :class:`GetCandles
            <iqoptionapi.ws.chanels.candles.GetCandles>`.
        """
        return GetCandles(self)

    def get_api_option_init_all(self):
        self.send_websocket_request(name="api_option_init_all", msg="")

    def get_api_option_init_all_v2(self):

        msg = {"name": "get-initialization-data",
               "version": "3.0",
               "body": {}
               }
        self.send_websocket_request(name="sendMessage", msg=msg)
# -------------get information-------------

    @property
    def get_betinfo(self):
        return Game_betinfo(self)

    @property
    def get_options(self):
        return Get_options(self)

    @property
    def get_options_v2(self):
        return Get_options_v2(self)

# ____________for_______binary_______option_____________

    @property
    def buyv3(self):
        return Buyv3(self)

    @property
    def buyv3_by_raw_expired(self):
        return Buyv3_by_raw_expired(self)

    @property
    def buy(self):
        """Property for get IQ Option websocket buyv2 request.

        :returns: The instance of :class:`Buyv2
            <iqoptionapi.ws.chanels.buyv2.Buyv2>`.
        """
        self.buy_successful = None
        return Buyv2(self)

    @property
    def sell_option(self):
        return Sell_Option(self)

    @property
    def sell_digital_option(self):
        return Sell_Digital_Option(self)
# ____________________for_______digital____________________

    def get_digital_underlying(self):
        msg = {"name": "get-underlying-list",
               "version": "2.0",
               "body": {"type": "digital-option"}
               }
        self.send_websocket_request(name="sendMessage", msg=msg)

    @property
    def get_strike_list(self):
        return Strike_list(self)

    @property
    def subscribe_instrument_quites_generated(self):
        return Subscribe_Instrument_Quites_Generated(self)

    @property
    def unsubscribe_instrument_quites_generated(self):
        return Unsubscribe_Instrument_Quites_Generated(self)

    @property
    def place_digital_option(self):
        return Digital_options_place_digital_option(self)

    @property
    def close_digital_option(self):
        return Digital_options_close_position(self)

# ____BUY_for__Forex__&&__stock(cfd)__&&__ctrpto_____
    @property
    def buy_order(self):
        return Buy_place_order_temp(self)

    @property
    def change_order(self):
        return Change_Tpsl(self)

    @property
    def change_auto_margin_call(self):
        return ChangeAutoMarginCall(self)

    @property
    def get_order(self):
        return Get_order(self)

    @property
    def get_pending(self):
        return GetDeferredOrders(self)

    @property
    def get_positions(self):
        return Get_positions(self)

    @property
    def get_position(self):
        return Get_position(self)

    @property
    def get_digital_position(self):
        return Get_digital_position(self)

    @property
    def get_position_history(self):
        return Get_position_history(self)

    @property
    def get_position_history_v2(self):
        return Get_position_history_v2(self)

    @property
    def get_available_leverages(self):
        return Get_available_leverages(self)

    @property
    def cancel_order(self):
        return Cancel_order(self)

    @property
    def close_position(self):
        return Close_position(self)

    @property
    def get_overnight_fee(self):
        return Get_overnight_fee(self)
# -------------------------------------------------------

    @property
    def heartbeat(self):
        return Heartbeat(self)
# -------------------------------------------------------

    def set_session(self, cookies, headers):
        """Method to set session cookies."""

        self.session.headers.update(headers)

        self.session.cookies.clear_session_cookies()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)

    def start_websocket(self):
        self.state.check_websocket_if_connect = None
        self.state.check_websocket_if_error = False
        self.state.websocket_error_reason = None

        self.websocket_client = WebsocketClient(self)

        # Configure SSL options: secure by default, allow insecure for debugging
        sslopt = {}
        if self.insecure_ssl:
            # for fix pyinstall error: cafile, capath and cadata cannot be all omitted
            sslopt = {"check_hostname": False, "cert_reqs": ssl.CERT_NONE, "ca_certs": "cacert.pem"}

        self.websocket_thread = threading.Thread(target=self.websocket.run_forever, kwargs={'sslopt': sslopt})
        self.websocket_thread.daemon = True
        self.websocket_thread.start()
        # Start sender worker
        self._sender_stop = False
        if not self._sender_thread or not self._sender_thread.is_alive():
            self._sender_thread = threading.Thread(target=self._send_worker)
            self._sender_thread.daemon = True
            self._sender_thread.start()
        start_t = time.time()
        while True:
            try:
                if self.state.check_websocket_if_error:
                    return False, self.state.websocket_error_reason
                if self.state.check_websocket_if_connect == 0:
                    return False, "Websocket connection closed."
                elif self.state.check_websocket_if_connect == 1:
                    return True, None
            except:
                pass
            time.sleep(0.05)
            if time.time() - start_t > max(self.default_timeout, 15):
                return False, "Websocket connection timeout."

    # @tokensms.setter
    def setTokenSMS(self, response):
        token_sms = response.json()['token']
        self.token_sms = token_sms

    # @token2fa.setter
    def setToken2FA(self, response):
        token_2fa = response.json()['token']
        self.token_login2fa = token_2fa

    def get_ssid(self):
        response = None
        try:
            if self.token_login2fa is None:
                response = self.login(
                    self.username, self.password)  # pylint: disable=not-callable
            else:
                response = self.login_2fa(
                    self.username, self.password, self.token_login2fa)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(e)
            return e
        return response

    def send_ssid(self):
        self.profile.msg = None
        self.ssid(self.state.SSID)  # pylint: disable=not-callable
        start_t = time.time()
        while self.profile.msg == None:
            time.sleep(0.05)
            if time.time() - start_t > max(self.default_timeout, 10):
                return False
        if self.profile.msg == False:
            return False
        else:
            return True

    def connect(self):

        self.state.ssl_Mutual_exclusion = False
        self.state.ssl_Mutual_exclusion_write = False
        """Method for connection to IQ Option API."""
        try:
            self.close()
        except:
            pass
        check_websocket, websocket_reason = self.start_websocket()

        if check_websocket == False:
            return check_websocket, websocket_reason

        # doing temp ssid reconnect for speed up
        if self.state.SSID != None:

            check_ssid = self.send_ssid()

            if check_ssid == False:
                # ssdi time out need reget,if sent error ssid,the weksocket will close by iqoption server
                response = self.get_ssid()
                try:
                    self.state.SSID = response.cookies["ssid"]
                except Exception:
                    reason = getattr(response, 'text', str(response))
                    return False, reason
                atexit.register(self.logout)
                self.start_websocket()
                self.send_ssid()

        # the ssid is None need get ssid
        else:
            response = self.get_ssid()
            try:
                self.state.SSID = response.cookies["ssid"]
            except Exception:
                self.close()
                reason = getattr(response, 'text', str(response))
                return False, reason
            atexit.register(self.logout)
            self.send_ssid()

        # set ssis cookie
        requests.utils.add_dict_to_cookiejar(
            self.session.cookies, {"ssid": self.state.SSID})

        self.timesync.server_timestamp = None
        start_t = time.time()
        while True:
            try:
                if self.timesync.server_timestamp != None:
                    break
            except:
                pass
            time.sleep(0.01)
            if time.time() - start_t > max(self.default_timeout, 10):
                return False, "TimeSync timeout."
        return True, None

    def _send_worker(self):
        while not self._sender_stop:
            try:
                with self._send_cv:
                    while not self._send_queue and not self._sender_stop:
                        self._send_cv.wait(0.1)
                    if self._sender_stop:
                        break
                    data = self._send_queue.popleft() if self._send_queue else None
                if data is None:
                    continue
                try:
                    # underlying websocket send
                    self.websocket.send(data)
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error("WS send error: %s", e)
            except Exception:
                pass

    def connect2fa(self, sms_code):
        response = self.verify_2fa(sms_code, self.token_sms)

        if response.json()['code'] != 'success':
            return False, response.json()['message']

        # token_2fa
        self.setToken2FA(response)
        if self.token_login2fa is None:
            return False, None
        return True, None

    def close(self):
        try:
            self._sender_stop = True
            with self._send_cv:
                self._send_cv.notify_all()
            if self._sender_thread:
                self._sender_thread.join(timeout=2)
        except Exception:
            pass
        self.websocket.close()
        self.websocket_thread.join()

    def websocket_alive(self):
        return self.websocket_thread.is_alive()

    @property
    def Get_User_Profile_Client(self):
        return Get_user_profile_client(self)

    @property
    def Request_Leaderboard_Userinfo_Deals_Client(self):
        return Request_leaderboard_userinfo_deals_client(self)

    @property
    def Get_Users_Availability(self):
        return Get_users_availability(self)

    @property
    def subscribe_digital_price_splitter(self):
        return SubscribeDigitalPriceSplitter(self)

    @property
    def unsubscribe_digital_price_splitter(self):
        return UnsubscribeDigitalPriceSplitter(self)

    @property
    def place_digital_option_v2(self):
        return DigitalOptionsPlaceDigitalOptionV2(self)
