from vmkis.__env__ import (
    __author__,
    __author_email__,
    __license__,
    __package_name__,
    __url__,
    __version__,
)

# 핵심 인증/클래스
from vmkis.client.auth import KisAuth
from vmkis.exceptions import *
from vmkis.kis import VmKis

# 공개 타입은 `vmkis.public_types`에서 재export
from vmkis.public_types import (
    Balance,
    Chart,
    MarketInfo,
    Order,
    Orderbook,
    Quote,
    TradingHours,
)

# 초보자용 유틸(선택적).
#
# 두 import를 분리한 이유: 하나의 try로 묶여 있으면 helpers가 실패할 때 이미
# 성공한 SimpleKIS까지 None으로 덮어써집니다. except도 Exception에서
# ImportError로 좁혔습니다 — 다른 오류까지 삼키면 원인을 알 수 없습니다.
try:
    from vmkis.simple import SimpleKIS
except ImportError:
    SimpleKIS = None

try:
    from vmkis.helpers import create_client, save_config_interactive
except ImportError:
    create_client = None
    save_config_interactive = None

__all__ = [
    # 핵심
    "VmKis",
    "KisAuth",
    # 공개 타입
    "Quote",
    "Balance",
    "Order",
    "Chart",
    "Orderbook",
    "MarketInfo",
    "TradingHours",
    # 초보자 도구
    "SimpleKIS",
    "create_client",
    "save_config_interactive",
]

# 하위 호환성: deprecated된 루트 import를 types 모듈로 위임하고 경고를 보냄
import warnings
from importlib import import_module
from typing import Any

_DEPRECATED_SOURCE = "vmkis.types"


def __getattr__(name: str) -> Any:
    # v3.0.0에서 `PyKis`가 `VmKis`로 이름이 바뀌었습니다.
    #
    # 이 별칭은 `vmkis` 패키지 *내부* 이름이라 업스트림 `python-kis` 배포판과
    # 파일이 충돌하지 않습니다. (호환용 `pykis` 패키지를 휠에 넣지 않는 이유가
    # 그 충돌입니다 — 둘 다 설치하면 last-write-wins로 덮어쓰기가 납니다.)
    #
    # 동일 객체를 반환하므로 isinstance 검사도 그대로 동작합니다.
    # `__all__`에는 넣지 않습니다. 넣으면 `from vmkis import *`가 옛 이름을
    # 계속 퍼뜨립니다. 이 별칭은 v4.0.0에서 제거됩니다.
    if name == "PyKis":
        warnings.warn(
            "`PyKis`는 `VmKis`로 이름이 바뀌었습니다. v4.0.0에서 제거됩니다.",
            DeprecationWarning,
            stacklevel=2,
        )
        return VmKis

    # Always warn about deprecated root-level imports so callers see a clear
    # deprecation notice even if the types module cannot be imported.
    warnings.warn(
        f"from vmkis import {name} is deprecated; use 'from vmkis.types import {name}' instead. This alias will be removed in a future major release.",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        module = import_module(_DEPRECATED_SOURCE)
    except Exception:
        # 원인 예외를 숨긴다. 호출자에게는 "그런 속성이 없다"가 정확한 설명이다.
        raise AttributeError(f"module 'vmkis' has no attribute '{name}'") from None

    if hasattr(module, name):
        return getattr(module, name)

    raise AttributeError(f"module 'vmkis' has no attribute '{name}'")
