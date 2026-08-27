import importlib
import sys
from unittest.mock import patch

import pytest

from vmkis.__env__ import (APPKEY_LENGTH, REAL_API_REQUEST_PER_SECOND,
                           REAL_DOMAIN, SECRETKEY_LENGTH, USER_AGENT,
                           VIRTUAL_API_REQUEST_PER_SECOND, VIRTUAL_DOMAIN,
                           WEBSOCKET_MAX_SUBSCRIPTIONS, WEBSOCKET_REAL_DOMAIN,
                           WEBSOCKET_VIRTUAL_DOMAIN, __author__, __license__,
                           __version__)


def test_sys_version_info():
    """Python 버전에 따른 RuntimeError 발생을 테스트합니다."""
    # Python 3.10 미만일 경우 RuntimeError 발생
    with patch.object(sys, "version_info", (3, 9, 0)):
        with pytest.raises(
            RuntimeError, match="VmKis에는 Python 3.10 이상이 필요합니다."
        ):
            importlib.reload(sys.modules["vmkis.__env__"])

    # Python 3.10 이상일 경우 정상 실행
    with patch.object(sys, "version_info", (3, 10, 0)):
        importlib.reload(sys.modules["vmkis.__env__"])


def test_version_placeholder():
    assert __version__ != "{{VERSION_PLACEHOLDER}}"


def test_constants_and_metadata():
    """__env__.py의 상수와 메타데이터를 테스트합니다."""
    assert APPKEY_LENGTH == 36
    assert SECRETKEY_LENGTH == 180
    assert REAL_DOMAIN == "https://openapi.koreainvestment.com:9443"
    assert VIRTUAL_DOMAIN == "https://openapivts.koreainvestment.com:29443"
    assert WEBSOCKET_REAL_DOMAIN == "ws://ops.koreainvestment.com:21000"
    assert WEBSOCKET_VIRTUAL_DOMAIN == "ws://ops.koreainvestment.com:31000"
    assert WEBSOCKET_MAX_SUBSCRIPTIONS == 40
    assert REAL_API_REQUEST_PER_SECOND == 19
    assert VIRTUAL_API_REQUEST_PER_SECOND == 2

    assert USER_AGENT == f"VmKis/{__version__}"

    assert __author__ == "soju06"
    assert __license__ == "MIT"
    assert __version__ is not None
    assert len(__version__) > 0
