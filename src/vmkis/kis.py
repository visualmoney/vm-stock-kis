import hashlib
from collections.abc import Callable, Iterable
from datetime import timedelta
from os import PathLike
from pathlib import Path
from time import sleep
from typing import Literal, TypeVar, overload
from urllib.parse import urljoin

import requests
from requests import Response

from vmkis import logging
from vmkis.__env__ import (
    API_RETRY_INITIAL_DELAY,
    API_RETRY_MAX_ATTEMPTS,
    API_RETRY_MAX_DELAY,
    API_TOKEN_REISSUE_LIMIT,
    REAL_API_REQUEST_PER_SECOND,
    REAL_DOMAIN,
    USER_AGENT,
    VIRTUAL_API_REQUEST_PER_SECOND,
    VIRTUAL_DOMAIN,
)
from vmkis.api.auth.token import KisAccessToken
from vmkis.client.account import KisAccountNumber
from vmkis.client.appkey import KisKey
from vmkis.client.auth import KisAuth
from vmkis.client.cache import KisCacheStorage
from vmkis.client.endpoint import KisEndpoint
from vmkis.client.exceptions import KisAuthenticationError, KisHTTPError, KisRateLimitError
from vmkis.client.form import KisForm
from vmkis.client.object import KisObjectBase, kis_object_init
from vmkis.client.page import KisPage
from vmkis.client.websocket import KisWebsocketClient
from vmkis.responses.dynamic import KisDynamic, KisObject, TDynamic
from vmkis.responses.response import KisPaginationAPIResponseProtocol
from vmkis.responses.types import KisDynamicDict
from vmkis.utils.rate_limit import RateLimiter
from vmkis.utils.retry import RetryConfig
from vmkis.utils.thread_safe import thread_safe
from vmkis.utils.workspace import get_cache_path

# 전역 `retry_config` 싱글턴을 쓰지 않고 전용 인스턴스를 둡니다.
# `with_retry` 데코레이터가 그 싱글턴을 제자리에서 변형하므로, 공유하면
# 데코레이터를 한 번 쓰는 순간 이쪽 정책까지 바뀝니다.
_REQUEST_RETRY_POLICY = RetryConfig(
    max_retries=API_RETRY_MAX_ATTEMPTS,
    initial_delay=API_RETRY_INITIAL_DELAY,
    max_delay=API_RETRY_MAX_DELAY,
    exponential_base=2.0,
    jitter=True,
)


TPagination = TypeVar("TPagination", bound=KisPaginationAPIResponseProtocol)

MAX_PAGES = 100
"""연속조회 상한.

서버가 `is_last` 를 끝내 주지 않거나 커서가 진행하지 않으면 루프가 끝나지
않습니다. 조용히 도는 것보다 명시적으로 실패하는 편이 낫습니다.
"""


class VmKis:
    """한국투자증권 API"""

    appkey: KisKey
    """한국투자증권 실전도메인 API AppKey"""
    virtual_appkey: KisKey | None
    """한국투자증권 API AppKey"""
    primary_account: KisAccountNumber | None
    """한국투자증권 기본 계좌 정보"""

    @property
    def virtual(self) -> bool:
        """모의도메인 여부"""
        return self.virtual_appkey is not None

    cache: KisCacheStorage
    """캐시 저장소"""

    _rate_limiters: dict[str, RateLimiter]
    """API 호출 제한"""
    _token: KisAccessToken | None
    """실전투자 API 접속 토큰"""
    _virtual_token: KisAccessToken | None
    """API 접속 토큰"""
    _websocket: KisWebsocketClient | None
    """웹소켓 클라이언트"""
    _keep_token: Path | None
    """API 접속 토큰 자동 저장 경로"""
    _sessions: dict[Literal["real", "virtual"], requests.Session]
    """API 세션"""

    @property
    def keep_token(self) -> bool:
        """API 접속 토큰 자동 저장 여부"""
        return self._keep_token is not None

    @overload
    def __init__(
        self,
        auth: str | PathLike[str] | KisAuth | None = None,
        /,
        *,
        token: KisAccessToken | str | PathLike[str] | None = None,
        keep_token: bool | str | PathLike[str] | None = None,
        use_websocket: bool = True,
    ):
        """
        `KisAuth` 인증 정보를 이용하여 실전투자용 한국투자증권 API를 생성합니다.

        Args:
            auth (str | PathLike[str] | KisAuth | None, optional): 실전도메인 인증 정보.
            token (KisAccessToken | str | PathLike[str] | None, optional): 실전도메인 API 접속 토큰.
            keep_token (bool | str | PathLike[str] | None, optional): API 접속 토큰을 저장할지 여부. 기본 저장 폴더: `~/.vmkis/` (신뢰할 수 없는 환경에서 사용하지 마세요)
            use_websocket (bool, optional): 웹소켓 사용 여부.

        Examples:

            파일로 저장된 인증 정보를 불러와 VmKis 객체를 생성합니다.

            먼저, 인증 정보를 저장합니다.

            >>> auth = KisAuth(
            ...     id="soju06",                # HTS 로그인 ID
            ...     account="00000000-01",      # 계좌번호
            ...     appkey="PSED321z...",       # AppKey 36자리
            ...     secretkey="RR0sFMVB...",    # SecretKey 180자리
            ... )
            >>> auth.save("vmkis_auth.json")

            그 후, 저장된 인증 정보를 불러와 VmKis 객체를 생성합니다.

            >>> kis = VmKis(
            ...     "vmkis_auth.json",          # 인증 정보 파일 경로
            ...     keep_token=True             # API 접속 토큰 자동 저장
            ... )

        Raises:
            ValueError: 인증 정보가 올바르지 않을 경우
        """
        ...

    @overload
    def __init__(
        self,
        auth: str | PathLike[str] | KisAuth | None = None,
        virtual_auth: str | PathLike[str] | KisAuth | None = None,
        /,
        *,
        token: KisAccessToken | str | PathLike[str] | None = None,
        virtual_token: KisAccessToken | str | PathLike[str] | None = None,
        keep_token: bool | str | PathLike[str] | None = None,
        use_websocket: bool = True,
    ):
        """
        `KisAuth` 인증 정보를 이용하여 모의투자용 한국투자증권 API를 생성합니다.

        Args:
            auth (str | PathLike[str] | KisAuth | None, optional): 실전도메인 인증 정보.
            virtual_auth (str | PathLike[str] | KisAuth | None, optional): 모의도메인 인증 정보.
            token (KisAccessToken | str | PathLike[str] | None, optional): 실전도메인 API 접속 토큰.
            virtual_token (KisAccessToken | str | PathLike[str] | None, optional): 모의도메인 API 접속 토큰.
            keep_token (bool | str | PathLike[str] | None, optional): API 접속 토큰을 저장할지 여부. 기본 저장 폴더: `~/.vmkis/` (신뢰할 수 없는 환경에서 사용하지 마세요)
            use_websocket (bool, optional): 웹소켓 사용 여부.

        Examples:

            먼저, 실전투자 인증 정보를 저장합니다.

            >>> real_auth = KisAuth(
            ...     id="soju06",                # HTS 로그인 ID
            ...     account="00000000-01",      # 계좌번호
            ...     appkey="PSED321z...",       # AppKey 36자리
            ...     secretkey="RR0sFMVB...",    # SecretKey 180자리
            ... )
            >>> real_auth.save("vmkis_real_auth.json")

            그 다음, 모의투자 인증 정보를 저장합니다.

            >>> virtual_auth = KisAuth(
            ...     id="soju06",                # 모의투자 HTS 로그인 ID
            ...     account="00000000-01",      # 모의투자 계좌번호
            ...     appkey="PSED321z...",       # 모의투자 AppKey 36자리
            ...     secretkey="RR0sFMVB...",    # 모의투자 SecretKey 180자리
            ...     virtual=True,               # 모의투자 여부
            ... )
            >>> virtual_auth.save("vmkis_virtual_auth.json")

            그 후, 저장된 인증 정보를 불러와 VmKis 객체를 생성합니다.

            >>> kis = VmKis(
            ...     "vmkis_real_auth.json",     # 실전투자 인증 정보 파일 경로
            ...     "vmkis_virtual_auth.json",  # 모의투자 인증 정보 파일 경로
            ...     keep_token=True             # API 접속 토큰 자동 저장
            ... )

        Raises:
            ValueError: 인증 정보가 올바르지 않을 경우
        """
        ...

    @overload
    def __init__(
        self,
        /,
        *,
        id: str | None = None,
        account: str | KisAccountNumber | None = None,
        appkey: str | KisKey | None = None,
        secretkey: str | None = None,
        token: KisAccessToken | str | PathLike[str] | None = None,
        keep_token: bool | str | PathLike[str] | None = None,
        use_websocket: bool = True,
    ):
        """
        실전투자용 한국투자증권 API를 생성합니다.

        Args:
            id (str | None, optional): API ID.
            account (str | KisAccountNumber | None, optional): 계좌번호.
            appkey (str | KisKey | None, optional): API 실전도메인 AppKey.
            secretkey (str | None, optional): API 실전도메인 SecretKey.
            token (KisAccessToken | str | PathLike[str] | None, optional): 실전도메인 API 접속 토큰.
            keep_token (bool | str | PathLike[str] | None, optional): API 접속 토큰을 저장할지 여부. 기본 저장 폴더: `~/.vmkis/` (신뢰할 수 없는 환경에서 사용하지 마세요)
            use_websocket (bool, optional): 웹소켓 사용 여부.

        Examples:

            인증 정보를 입력하여 VmKis 객체를 생성합니다.

            >>> kis = VmKis(
            ...     id="soju06",                        # HTS 로그인 ID
            ...     account="00000000-01",              # 계좌번호
            ...     appkey="PSED321z...",               # AppKey 36자리
            ...     secretkey="RR0sFMVB...",            # SecretKey 180자리
            ...     keep_token=True,                    # API 접속 토큰 자동 저장
            ... )

        Raises:
            ValueError: 인증 정보가 올바르지 않을 경우
        """
        ...

    @overload
    def __init__(
        self,
        /,
        *,
        id: str | None = None,
        account: str | KisAccountNumber | None = None,
        appkey: str | KisKey | None = None,
        secretkey: str | None = None,
        token: KisAccessToken | str | PathLike[str] | None = None,
        virtual_id: str | None = None,
        virtual_appkey: str | KisKey | None = None,
        virtual_secretkey: str | None = None,
        virtual_token: KisAccessToken | str | PathLike[str] | None = None,
        keep_token: bool | str | PathLike[str] | None = None,
        use_websocket: bool = True,
    ):
        """
        모의투자용 한국투자증권 API를 생성합니다.

        Args:
            id (str | None, optional): API ID.
            appkey (str | KisKey | None, optional): API 실전도메인 AppKey.
            secretkey (str | None, optional): API 실전도메인 SecretKey.
            token (KisAccessToken | str | PathLike[str] | None, optional): 실전도메인 API 접속 토큰.
            virtual_id (str | None, optional): 모의도메인 API ID.
            virtual_appkey (str | KisKey | None, optional): 모의도메인 API AppKey.
            virtual_secretkey (str | None, optional): 모의도메인 API SecretKey.
            account (str | KisAccountNumber | None, optional): 계좌번호.
            virtual_token (KisAccessToken | str | PathLike[str] | None, optional): 모의도메인 API 접속 토큰.
            keep_token (bool | str | PathLike[str] | None, optional): API 접속 토큰을 저장할지 여부. 기본 저장 폴더: `~/.vmkis/` (신뢰할 수 없는 환경에서 사용하지 마세요)
            use_websocket (bool, optional): 웹소켓 사용 여부.

        Examples:

            인증 정보를 입력하여 모의 투자용 VmKis 객체를 생성합니다.

            >>> kis = VmKis(
            ...     id="soju06",                        # HTS 로그인 ID
            ...     account="00000000-01",              # 모의투자 계좌번호
            ...     appkey="PSED321z...",               # 실전투자 AppKey 36자리
            ...     secretkey="RR0sFMVB...",            # 실전투자 SecretKey 180자리
            ...     virtual_id="soju06",                # 모의투자 HTS 로그인 ID
            ...     virtual_appkey="PSED321z...",       # 모의투자 AppKey 36자리
            ...     virtual_secretkey="RR0sFMVB...",    # 모의투자 SecretKey 180자리
            ...     keep_token=True,                    # API 접속 토큰 자동 저장
            ... )

        Raises:
            ValueError: 인증 정보가 올바르지 않을 경우
        """
        ...

    @overload
    def __init__(
        self,
        auth: str | PathLike[str] | KisAuth | None = None,
        /,
        *,
        account: str | KisAccountNumber | None = None,
        token: KisAccessToken | str | PathLike[str] | None = None,
        virtual_id: str | None = None,
        virtual_appkey: str | KisKey | None = None,
        virtual_secretkey: str | None = None,
        virtual_token: KisAccessToken | str | PathLike[str] | None = None,
        keep_token: bool | str | PathLike[str] | None = None,
        use_websocket: bool = True,
    ):
        """
        `KisAuth` 인증 정보를 이용하여 모의투자용 한국투자증권 API를 생성합니다.

        Args:
            auth (str | PathLike[str] | KisAuth | None, optional): 실전도메인 인증 정보.
            account (str | KisAccountNumber | None, optional): 계좌번호.
            token (KisAccessToken | str | PathLike[str] | None, optional): 실전도메인 API 접속 토큰.
            virtual_id (str | None, optional): 모의도메인 API ID.
            virtual_appkey (str | KisKey | None, optional): 모의도메인 API AppKey.
            virtual_secretkey (str | None, optional): 모의도메인 API SecretKey.
            virtual_token (KisAccessToken | str | PathLike[str] | None, optional): 모의도메인 API 접속 토큰.
            keep_token (bool | str | PathLike[str] | None, optional): API 접속 토큰을 저장할지 여부. 기본 저장 폴더: `~/.vmkis/` (신뢰할 수 없는 환경에서 사용하지 마세요)
            use_websocket (bool, optional): 웹소켓 사용 여부.

        Examples:

            파일로 저장된 인증 정보를 불러와 모의투자용 VmKis 객체를 생성합니다.

            먼저, 실전투자 인증 정보를 저장합니다.

            >>> real_auth = KisAuth(
            ...     id="soju06",                        # HTS 로그인 ID
            ...     account="00000000-01",              # 모의투자 계좌번호
            ...     appkey="PSED321z...",               # AppKey 36자리
            ...     secretkey="RR0sFMVB...",            # SecretKey 180자리
            ... )
            >>> real_auth.save("vmkis_real_auth.json")

            그 후, 저장된 인증 정보를 불러와 모의투자용 VmKis 객체를 생성합니다.

            >>> kis = VmKis(
            ...     "vmkis_real_auth.json",             # 실전투자 인증 정보 파일 경로
            ...     virtual_id="soju06",                # 모의투자 HTS 로그인 ID
            ...     virtual_appkey="PSED321z...",       # 모의투자 AppKey 36자리
            ...     virtual_secretkey="RR0sFMVB...",    # 모의투자 SecretKey 180자리
            ...     keep_token=True,                    # API 접속 토큰 자동 저장
            ... )

        Raises:
            ValueError: 인증 정보가 올바르지 않을 경우
        """
        ...

    def __init__(
        self,
        auth: str | PathLike[str] | KisAuth | None = None,
        virtual_auth: str | PathLike[str] | KisAuth | None = None,
        /,
        *,
        account: str | KisAccountNumber | None = None,
        id: str | None = None,
        appkey: str | KisKey | None = None,
        secretkey: str | None = None,
        token: KisAccessToken | str | PathLike[str] | None = None,
        virtual_id: str | None = None,
        virtual_appkey: str | KisKey | None = None,
        virtual_secretkey: str | None = None,
        virtual_token: KisAccessToken | str | PathLike[str] | None = None,
        use_websocket: bool = True,
        keep_token: bool | str | PathLike[str] | None = None,
    ):
        if auth is not None:
            if not isinstance(auth, KisAuth):
                auth = KisAuth.load(auth)

            if auth.virtual:
                raise ValueError("auth에는 실전도메인 인증 정보를 입력해야 합니다.")

            id = auth.id
            appkey = auth.key
            account = auth.account_number

        if virtual_auth is not None:
            if not isinstance(virtual_auth, KisAuth):
                virtual_auth = KisAuth.load(virtual_auth)

            if not virtual_auth.virtual:
                raise ValueError("virtual_auth에는 모의도메인 인증 정보를 입력해야 합니다.")

            virtual_id = virtual_auth.id
            virtual_appkey = virtual_auth.key
            account = virtual_auth.account_number

        virtual = virtual_appkey is not None and virtual_auth is not None

        if id is None:
            raise ValueError("id를 입력해야 합니다.")

        if appkey is None:
            raise ValueError("appkey를 입력해야 합니다.")

        if virtual and virtual_id is None:
            raise ValueError("virtual_id를 입력해야 합니다.")

        if virtual and virtual_appkey is None:
            raise ValueError("virtual_appkey를 입력해야 합니다.")

        if isinstance(appkey, str):
            if secretkey is None:
                raise ValueError("secretkey를 입력해야 합니다.")

            appkey = KisKey(
                id=id,
                appkey=appkey,
                secretkey=secretkey,
            )

        self.appkey = appkey

        if isinstance(virtual_appkey, str):
            if virtual_secretkey is None:
                raise ValueError("primary_secretkey를 입력해야 합니다.")

            virtual_appkey = KisKey(
                id=id,
                appkey=virtual_appkey,
                secretkey=virtual_secretkey,
            )

        self.virtual_appkey = virtual_appkey

        if isinstance(account, str):
            account = KisAccountNumber(account)

        self.primary_account = account

        self._websocket = KisWebsocketClient(self) if use_websocket else None
        self.cache = KisCacheStorage()

        self._rate_limiters = {
            "real": RateLimiter(REAL_API_REQUEST_PER_SECOND, 1),
            "virtual": RateLimiter(VIRTUAL_API_REQUEST_PER_SECOND, 1),
        }
        self._token = token if isinstance(token, KisAccessToken) else KisAccessToken.load(token) if token else None
        self._virtual_token = (
            virtual_token
            if isinstance(virtual_token, KisAccessToken)
            else KisAccessToken.load(virtual_token)
            if self.virtual and virtual_token
            else None
        )
        self._sessions = {
            "real": requests.Session(),
            "virtual": requests.Session(),
        }

        for session in self._sessions.values():
            session.headers.update({"User-Agent": USER_AGENT})

        if keep_token:
            if keep_token is True:
                keep_token = get_cache_path()

            self._keep_token = Path(keep_token).resolve()
            self._load_cached_token(self._keep_token)
        else:
            self._keep_token = None

    def _get_hashed_token_name(self, domain: Literal["real", "virtual"]) -> str:
        appkey = self.appkey if domain == "real" else self.virtual_appkey

        if appkey is None:
            raise ValueError("모의도메인 AppKey가 없습니다.")

        hash = hashlib.sha1(f"vmkis{appkey.id}{appkey.appkey}{appkey.secretkey}token".encode()).hexdigest()

        return f"token_{domain}_{self.appkey.id}_{hash}.json"

    def _load_cached_token(self, token_dir: str | PathLike[str] | Path) -> None:
        if not isinstance(token_dir, Path):
            token_dir = Path(token_dir)

        token_dir = token_dir.resolve()
        virtual_token_path = token_dir / self._get_hashed_token_name("real")

        if virtual_token_path.exists():
            try:
                self.token = KisAccessToken.load(virtual_token_path)
                logging.logger.debug("실전도메인 API 접속 토큰을 불러왔습니다.")
            except Exception:
                # 캐시된 토큰이 손상되었거나 형식이 바뀐 경우. 새로 발급받으면 된다.
                pass

        if self.virtual:
            virtual_token_path = token_dir / self._get_hashed_token_name("virtual")

            if virtual_token_path.exists():
                try:
                    self.primary_token = KisAccessToken.load(virtual_token_path)
                    logging.logger.debug("모의도메인 API 접속 토큰을 불러왔습니다.")
                except Exception:
                    # 캐시된 토큰이 손상되었거나 형식이 바뀐 경우. 새로 발급받으면 된다.
                    pass

    def _save_cached_token(
        self,
        token_dir: str | PathLike[str] | Path,
        domain: Literal["real", "virtual"] | None = None,
        force: bool = False,
    ):
        if not isinstance(token_dir, Path):
            token_dir = Path(token_dir)

        token_dir = token_dir.resolve()
        token_dir.mkdir(parents=True, exist_ok=True)

        if domain is None or domain == "real":
            token = self.token if force else self._token

            if token is not None:
                token.save(token_dir / self._get_hashed_token_name("real"))
                logging.logger.debug("실전도메인 API 접속 토큰을 저장했습니다.")

        if self.virtual and (domain is None or domain == "virtual"):
            virtual_token = self.primary_token if force else self._virtual_token

            if virtual_token is not None:
                virtual_token.save(token_dir / self._get_hashed_token_name("virtual"))
                logging.logger.debug("모의도메인 API 접속 토큰을 저장했습니다.")

    def _rate_limit_exceeded(self) -> None:
        logging.logger.warning("API 호출 횟수를 초과하여 호출 유량 획득까지 대기합니다.")

    def request(
        self,
        path: str,
        *,
        method: Literal["GET", "POST"] = "GET",
        params: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
        form: Iterable[KisForm | None] | None = None,
        headers: dict[str, str] | None = None,
        domain: Literal["real", "virtual"] | None = None,
        appkey_location: Literal["header", "body"] | None = "header",
        form_location: Literal["header", "params", "body"] | None = None,
        auth: bool = True,
    ) -> Response:
        if method == "GET":
            if body is not None:
                raise ValueError("GET 요청에는 body를 입력할 수 없습니다.")

            if appkey_location == "body":
                raise ValueError("GET 요청에는 appkey_location을 header로 설정해야 합니다.")
        elif body is None:
            body = {}

        request_headers = headers.copy() if headers else {}

        if domain is None:
            domain = "virtual" if self.virtual else "real"

        session = self._sessions[domain]

        if appkey_location:
            appkey = self.appkey if domain == "real" else self.virtual_appkey

            if appkey is None:
                raise ValueError("모의도메인 AppKey가 없습니다.")

            appkey.build(request_headers if appkey_location == "header" else body)

        if form is not None:
            if form_location is None:
                form_location = "params" if method == "GET" else "body"

            dist = request_headers if form_location == "header" else params if form_location == "params" else body

            for f in form:
                if f is not None:
                    f.build(dist)

        rate_limit = self._rate_limiters[domain]

        # 재시도는 반드시 끝나야 합니다. 예전에는 상한이 없어, 서버가 유량 초과를
        # 계속 반환하면 이 호출이 영원히 반환되지 않았습니다.
        rate_limit_retries = 0
        token_reissues = 0

        while True:
            rate_limit.acquire(blocking_callback=self._rate_limit_exceeded)

            if auth:
                (self.token if domain == "real" else self.primary_token).build(request_headers)

            resp = session.request(
                method=method,
                url=urljoin(REAL_DOMAIN if domain == "real" else VIRTUAL_DOMAIN, path),
                headers=request_headers,
                params=params,
                json=body,
            )

            if resp.ok:
                return resp

            try:
                data = resp.json()
            except Exception:
                data = None

            error_code = data.get("msg_cd") if data is not None else None

            match error_code:
                case "EGW00201":
                    # Rate limit exceeded
                    #
                    # 로컬 유량 제한기를 통과했는데도 서버가 초과라고 답하는
                    # 상황입니다(같은 계정을 쓰는 다른 프로세스 등). 고정 간격으로
                    # 되받아치면 상황을 악화시키므로 지수 백오프 + 지터로 물러납니다.
                    if rate_limit_retries >= API_RETRY_MAX_ATTEMPTS:
                        logging.logger.error(
                            f"API 호출 유량 초과가 계속되어 중단합니다. ({API_RETRY_MAX_ATTEMPTS}회 재시도)"
                        )
                        raise KisRateLimitError(response=resp)

                    delay = _REQUEST_RETRY_POLICY.calculate_delay(rate_limit_retries)
                    rate_limit_retries += 1
                    logging.logger.warning(
                        f"API 호출 횟수를 초과하였습니다. "
                        f"{delay:.2f}초 후 재시도 ({rate_limit_retries}/{API_RETRY_MAX_ATTEMPTS})"
                    )
                    sleep(delay)
                    continue

                case "EGW00123":
                    # Token expired
                    #
                    # 재발급 후에도 같은 오류가 나면 만료가 아니라 인증 문제입니다.
                    # 반복해도 결과가 달라지지 않으므로 즉시 실패합니다.
                    if token_reissues >= API_TOKEN_REISSUE_LIMIT:
                        logging.logger.error("토큰을 재발급했는데도 만료 오류가 반복됩니다. 인증 정보를 확인하세요.")
                        raise KisAuthenticationError(response=resp)

                    token_reissues += 1

                    if domain == "real":
                        self._token = None
                    else:
                        self._virtual_token = None

                case _:
                    raise KisHTTPError(response=resp)

    def fetch(
        self,
        path: str,
        *,
        method: Literal["GET", "POST"] = "GET",
        params: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
        form: Iterable[KisForm | None] | None = None,
        headers: dict[str, str] | None = None,
        domain: Literal["real", "virtual"] | None = None,
        appkey_location: Literal["header", "body"] | None = "header",
        form_location: Literal["header", "params", "body"] | None = None,
        auth: bool = True,
        api: str | None = None,
        continuous: bool = False,
        response_type: TDynamic | type[TDynamic] | Callable[[], TDynamic] = KisDynamicDict,
        verbose: bool = True,
    ) -> TDynamic:
        if api is not None:
            if headers is None:
                headers = {}

            headers["tr_id"] = api

        if continuous:
            if headers is None:
                headers = {}

            headers["tr_cont"] = "N"

        response = self.request(
            path,
            method=method,
            params=params,
            body=body,
            form=form,
            headers=headers,
            domain=domain,
            appkey_location=appkey_location,
            form_location=form_location,
            auth=auth,
        )

        data = response.json()
        data["__response__"] = response

        if verbose:
            logging.logger.debug(
                "API [%s]: %s, %s -> %s:%s (%s)",
                api or path,
                params or ".",
                body or ".",
                data.get("rt_cd", "."),
                data.get("msg_cd", "."),
                data.get("msg1", ".").strip(),
            )

        response_object = KisObject.transform_(
            data=data,
            transform_type=response_type,
            ignore_missing_fields={"__response__"},
        )

        if isinstance(response_object, KisObjectBase):
            kis_object_init(self, response_object)

        return response_object  # type: ignore

    def call(
        self,
        endpoint: KisEndpoint,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
        form: Iterable[KisForm | None] | None = None,
        page: KisPage | None = None,
        response_type: TDynamic | type[TDynamic] | Callable[[], TDynamic] = KisDynamicDict,
        **kwargs,
    ) -> TDynamic:
        """엔드포인트 스펙으로 API 를 호출합니다.

        `fetch()` 위에 얹은 얇은 층입니다. 흩어져 있던 세 가지 규칙을 여기서만
        처리합니다.

        1. **실전/모의 TR ID 선택** — 예전에는 호출부마다
           `api="VTTC8434R" if self.virtual else "TTTC8434R"` 를 적었습니다
        2. **도메인 라우팅** — 모의 미지원 TR 은 실전으로 보냅니다.
           예전에는 `domain="real"` 을 손으로 붙였고, **빠뜨리면 모의 계정에서만
           터지는 버그**가 됐습니다
        3. **커서 길이와 연속조회** — `page.to(100)` / `continuous=not page.is_first`

        Args:
            endpoint: 엔드포인트 스펙
            page: 연속조회 커서. 주면 `endpoint.page_size` 로 길이를 맞추고
                `form` 뒤에 붙입니다. 첫 페이지가 아니면 `continuous=True`.

        `fetch()` 의 나머지 인자는 `**kwargs` 로 그대로 넘어갑니다.
        """
        tr_id, domain = endpoint.resolve(self.virtual)

        forms = list(form) if form is not None else []
        continuous = False

        if page is not None:
            if endpoint.page_size is not None:
                page = page.to(endpoint.page_size)

            forms.append(page)
            continuous = not page.is_first

        return self.fetch(
            endpoint.path,
            method=endpoint.method,
            api=tr_id,
            domain=domain,
            params=params,
            body=body,
            form=forms or None,
            continuous=continuous,
            response_type=response_type,
            **kwargs,
        )

    def fetch_pages(
        self,
        endpoint: KisEndpoint,
        *,
        response_type: Callable[[], TPagination],
        merge: Callable[[TPagination, TPagination], None],
        page: KisPage | None = None,
        continuous: bool = True,
        max_pages: int = MAX_PAGES,
        params: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
        form: Iterable[KisForm | None] | None = None,
        **kwargs,
    ) -> TPagination:
        """연속조회를 끝까지 따라가며 결과를 하나로 합칩니다.

        예전에는 이 루프를 엔드포인트마다 각자 복사했습니다(이슈 #44 착수 시점
        8곳). 골격이 전부 같고 **다른 것은 "어느 필드에 누적하는가" 한 줄뿐**
        이었습니다. `continuous` / `is_last` / `next_page` 를 잘못 다루면
        **무한 루프이거나 첫 페이지만 반환**하는데, 둘 다 조용히 틀립니다.

        Args:
            response_type: 응답 객체를 만드는 **팩토리**. 인스턴스가 아닙니다
                (아래 참고).
            merge: `merge(첫_페이지, 다음_페이지)` — 첫 페이지에 누적합니다.
                예: `lambda first, more: first.stocks.extend(more.stocks)`
            continuous: `False` 면 첫 페이지만 가져옵니다.
            max_pages: 상한. 서버가 `is_last` 를 끝내 주지 않아도 여기서 멈춥니다.

        Raises:
            TypeError: `response_type` 에 팩토리가 아니라 인스턴스를 준 경우
            RuntimeError: `max_pages` 를 넘긴 경우

        **왜 팩토리인가.** `KisObject.transform_` 은 인스턴스를 받으면 **그
        인스턴스에 그대로 파싱**합니다. 하나를 돌려 쓰면 모든 페이지가 같은
        객체가 되고, `merge(first, result)` 가 자기 자신을 이어붙여 결과가
        불어납니다. 예전 루프들이 매 반복마다 응답 객체를 새로 만든 이유가
        이것입니다.
        """
        if isinstance(response_type, KisDynamic):
            raise TypeError(
                "response_type 에는 인스턴스가 아니라 팩토리를 주세요. "
                "인스턴스를 주면 모든 페이지가 같은 객체에 파싱되어 결과가 불어납니다. "
                "예: response_type=lambda: KisDomesticBalance(account_number=account)"
            )

        page = page or KisPage.first()
        first: TPagination | None = None

        for _ in range(max_pages):
            result = self.call(
                endpoint,
                params=params,
                body=body,
                form=form,
                page=page,
                response_type=response_type,
                **kwargs,
            )

            if first is None:
                first = result
            else:
                merge(first, result)

            if not continuous or result.is_last:
                return first

            page = result.next_page

        # `KisInternalError` 를 쓰지 않는 이유: 그 예외의 베이스가 `Response` 를
        # 요구하는데 여기에는 건넬 응답이 없습니다.
        raise RuntimeError(
            f"연속조회가 {max_pages}페이지를 넘겼습니다. 서버가 마지막 페이지를 알리지 않았거나 "
            f"커서가 진행하지 않고 있습니다. ({endpoint.path})"
        )

    @property
    @thread_safe("token")
    def token(self) -> KisAccessToken:
        """실전도메인 API 접속 토큰을 반환합니다."""
        if self._token is None or self._token.remaining < timedelta(minutes=10):
            from vmkis.api.auth.token import token_issue

            self._token = token_issue(self, domain="real")
            logging.logger.debug("실전도메인 API 접속 토큰을 발급했습니다.")

            if self._keep_token:
                self._save_cached_token(self._keep_token, domain="real", force=False)

        return self._token

    @token.setter
    @thread_safe("token")
    def token(self, token: KisAccessToken) -> None:
        """API 접속 토큰을 설정합니다."""
        self._token = token

    @property
    @thread_safe("primary_token")
    def primary_token(self) -> KisAccessToken:
        """API 접속 토큰을 반환합니다."""
        if not self.virtual:
            return self.token

        if self._virtual_token is None or self._virtual_token.remaining < timedelta(minutes=10):
            from vmkis.api.auth.token import token_issue

            self._virtual_token = token_issue(self, domain="virtual")
            logging.logger.debug("모의도메인 API 접속 토큰을 발급했습니다.")

            if self._keep_token:
                self._save_cached_token(self._keep_token, domain="virtual", force=False)

        return self._virtual_token

    @primary_token.setter
    @thread_safe("primary_token")
    def primary_token(self, token: KisAccessToken) -> None:
        """API 접속 토큰을 설정합니다."""
        self._virtual_token = token

    def discard(self, domain: Literal["real", "virtual"] | None = None) -> None:
        """API 접속 토큰을 폐기합니다."""
        from vmkis.api.auth.token import token_revoke

        if self._token is not None and (domain is None or domain == "real"):
            token_revoke(self, self._token.token)
            self._token = None

        if self._virtual_token is not None and (domain is None or (domain == "virtual" and self.virtual)):
            token_revoke(self, self._virtual_token.token)
            self._virtual_token = None

    @property
    def primary(self) -> KisAccountNumber:
        """
        기본 계좌 정보를 반환합니다.

        Raises:
            ValueError: 기본 계좌 정보가 없을 경우
        """
        if self.primary_account is None:
            raise ValueError("기본 계좌 정보가 없습니다.")

        return self.primary_account

    @property
    def websocket(self) -> KisWebsocketClient:
        """웹소켓 클라이언트를 반환합니다."""
        if self._websocket is None:
            raise ValueError("웹소켓 클라이언트가 초기화되지 않았습니다.")

        return self._websocket

    def close(self) -> None:
        """API 세션을 종료합니다."""
        # `getattr` 로 방어하는 이유: 생성자가 중간에 실패하면(잘못된 인증 정보로
        # `ValueError`) `_sessions` 가 설정되기 전에 객체가 소멸합니다. 그때
        # `__del__` -> `close()` 가 없는 속성을 참조해 AttributeError 를 냅니다.
        # 파이썬이 `__del__` 의 예외를 삼키므로 치명적이지는 않지만, 실행할 때마다
        # PytestUnraisableExceptionWarning 노이즈가 쌓입니다.
        #
        # 이 가드를 걷어내면 `tests/unit/test_kis.py` 의 초기화 실패 테스트 3건이
        # 실패합니다. 예전에는 그 테스트들이 `__del__` 을 무력화해 우회하고 있어서
        # 아무 일도 일어나지 않았습니다(이슈 #42). 지금은 `pyproject.toml` 의
        # `filterwarnings` 가 그 경고를 오류로 올립니다.
        for session in getattr(self, "_sessions", {}).values():
            session.close()

    def __del__(self) -> None:
        """API 세션을 종료합니다."""
        self.close()

    from vmkis.api.stock.trading_hours import trading_hours
    from vmkis.scope.account import account
    from vmkis.scope.stock import stock
