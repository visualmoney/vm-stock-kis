import sys
from email.utils import getaddresses as _getaddresses
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as _dist_metadata
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


# 저자 정보도 배포 메타데이터에서 읽습니다. pyproject.toml 의 [project] authors /
# maintainers 가 유일한 출처이며, 여기에 값을 적어 두면 두 곳이 각자 진실을
# 주장하다 어긋납니다. 실제로 이 파일은 포크 이후에도 업스트림 저자만 담고 있어
# pyproject.toml(두 저자 + visualmoney 관리자)과 불일치 상태였습니다.
#
# PEP 621 은 authors/maintainers 를 목록으로 담으므로 메타데이터에는
# "Soju06 <qlskssk@gmail.com>, visualmoney <visualmoney2@gmail.com>" 형태로
# 들어갑니다. email.utils.getaddresses 로 분해합니다.
def _read_people(field: str) -> list[tuple[str, str]]:
    """배포 메타데이터의 사람 목록을 (이름, 이메일) 목록으로 반환합니다."""
    try:
        raw = _dist_metadata(__package_name__).get(field)
    except PackageNotFoundError:
        return []

    return [(name, email) for name, email in _getaddresses([raw or ""]) if name or email]


#: 이 배포판의 저자 목록 (pyproject.toml [project] authors)
__authors__ = _read_people("Author-email")
#: 이 배포판의 관리자 목록 (pyproject.toml [project] maintainers)
__maintainers__ = _read_people("Maintainer-email")

# `__author__` 는 이 배포판을 내는 주체를 가리킵니다. 관리자가 지정되어 있으면
# 그쪽이, 없으면 첫 번째 저자가 됩니다. 업스트림 크레딧은 아래에 따로 둡니다.
_primary = (__maintainers__ or __authors__ or [("", "")])[0]
__author__ = _primary[0]
__author_email__ = _primary[1]

__url__ = "https://github.com/visualmoney/vm-stock-kis"

# 이 라이브러리는 아래 프로젝트의 포크입니다.
__upstream_author__ = "Soju06"
__upstream_url__ = "https://github.com/Soju06/python-kis"

__license__ = "MIT"

# ruff는 target-version=py310 기준으로 이 블록을 죽은 코드로 보지만, 그렇지 않다.
# requires-python은 pip 설치만 막을 뿐, 소스 트리에서 직접 실행하는 경우는 막지 못한다.
# 이 파일에는 3.10 전용 문법이 없어 3.9에서도 여기까지 도달하며, 그때 이 가드가
# 알아보기 어려운 SyntaxError 대신 명확한 메시지를 준다.
if sys.version_info < (3, 10):  # noqa: UP036
    raise RuntimeError(f"VmKis에는 Python 3.10 이상이 필요합니다. (Current: {sys.version})")
