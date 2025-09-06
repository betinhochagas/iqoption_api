from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, TypedDict, Union


class InstrumentType(str, Enum):
    BINARY_OPTION = "binary-option"
    TURBO_OPTION = "turbo-option"
    DIGITAL_OPTION = "digital-option"
    FOREX = "forex"
    CFD = "cfd"
    CRYPTO = "crypto"
    FX_OPTION = "fx-option"
    MULTI_OPTION = "multi-option"


RequestId = Union[str, int]


class WsMessage(TypedDict, total=False):
    name: str
    msg: Any
    request_id: Optional[RequestId]
    microserviceName: str


@dataclass
class WsSendEnvelope:
    name: str
    msg: Dict[str, Any]
    request_id: Union[str, int, str]

