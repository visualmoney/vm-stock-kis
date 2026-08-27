import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _dist_version

APPKEY_LENGTH = 36
SECRETKEY_LENGTH = 180

REAL_DOMAIN = "https://openapi.koreainvestment.com:9443"
VIRTUAL_DOMAIN = "https://openapivts.koreainvestment.com:29443"

WEBSOCKET_REAL_DOMAIN = "ws://ops.koreainvestment.com:21000"
WEBSOCKET_VIRTUAL_DOMAIN = "ws://ops.koreainvestment.com:31000"

WEBSOCKET_MAX_SUBSCRIPTIONS = 40

REAL_API_REQUEST_PER_SECOND = 20 - 1
VIRTUAL_API_REQUEST_PER_SECOND = 2

TRACE_DETAIL_ERROR: bool = False
"""
경고: 해당 기능은 HTTPStatusCode 200이 아닌 경우. 상세한 요청, 응답을 출력합니다.

이로 인해 예외 메세지에서 앱 키가 노출될 수 있습니다.
"""

# 배포 메타데이터에서 버전을 읽습니다. 값은 hatch-vcs가 git 태그로부터 만듭니다.
#
# 인자는 반드시 **배포명**이어야 합니다. 모듈명("vmkis")을 넘기면
# PackageNotFoundError가 나고 아래 fallback이 조용히 가짜 버전을 노출합니다.
#
# except를 PackageNotFoundError로 좁힌 이유: 예전에는 `except Exception`이라
# 어떤 오류든 삼키고 하드코딩된 버전을 반환했습니다.
try:
    __version__ = _dist_version("vm-stock-kis")
except PackageNotFoundError:
    # 설치되지 않은 소스 트리에서 실행하는 경우.
    # "2.1.6+dev" 같은 그럴듯한 거짓값 대신 명백히 틀린 값을 씁니다.
    __version__ = "0.0.0+unknown"

USER_AGENT = f"VmKis/{__version__}"

__package_name__ = "vm-stock-kis"
__author__ = "soju06"
__author_email__ = "qlskssk@gmail.com"
__url__ = "https://github.com/visualmoney/vm-stock-kis"
__upstream_url__ = "https://github.com/Soju06/python-kis"
__license__ = "MIT"

if sys.version_info < (3, 10):
    raise RuntimeError(f"VmKis에는 Python 3.10 이상이 필요합니다. (Current: {sys.version})")
