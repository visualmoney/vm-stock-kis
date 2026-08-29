"""초보자용 설정 헬퍼.

YAML 설정 파일에서 인증 정보를 읽어 `VmKis` 클라이언트를 만들거나, 대화형으로
설정 파일을 작성합니다.
"""

import getpass
import os
import warnings
from typing import Any

import yaml

from vmkis.client.auth import KisAuth
from vmkis.kis import VmKis

__all__ = ["create_client", "load_config", "save_config_interactive"]


def _env(name: str) -> str | None:
    """`VMKIS_<name>`을 읽고, 없으면 `PYKIS_<name>`으로 폴백합니다.

    0.0.1에서 접두사가 `PYKIS_`에서 `VMKIS_`로 바뀌었습니다.
    이 폴백은 1.0.0에서 제거됩니다.
    """
    if (value := os.environ.get(f"VMKIS_{name}")) is not None:
        return value

    if (value := os.environ.get(f"PYKIS_{name}")) is not None:
        warnings.warn(
            f"환경변수 `PYKIS_{name}`은 `VMKIS_{name}`으로 이름이 바뀌었습니다. 1.0.0에서 제거됩니다.",
            DeprecationWarning,
            stacklevel=3,
        )
        return value

    return None


#: 자격증명 키. `KisAuth` 의 필드와 1:1 입니다.
_CREDENTIAL_KEYS = ("id", "account", "appkey", "secretkey")

#: 실전/모의를 가르는 키.
#:
#: 별도 상수인 이유는 읽기(`load_config`)와 쓰기(`save_config_interactive`)가
#: 같은 문자열을 따로 적고 있었기 때문입니다. 한쪽만 고치면 조용히 어긋납니다.
#: #70 이 이 값을 `mode` 로 바꾸면서 불리언을 `live|paper` enum 으로 대체합니다.
_MODE_KEY = "virtual"

#: 프로필에 허용되는 키 전체. 이 밖의 키는 오타로 봅니다.
_PROFILE_KEYS = frozenset(_CREDENTIAL_KEYS) | {_MODE_KEY}


def _validate_profile(profile: Any, *, path: str, name: str | None = None) -> dict[str, Any]:
    """설정 프로필이 쓸 수 있는 모양인지 확인합니다.

    조용히 넘어가지 않는 것이 이 함수의 존재 이유입니다. `create_client` 는 키를
    하나씩 뽑아 쓰기 때문에 여분·오타 키가 아무 소리 없이 무시됐고, 판정 키가
    빠지면 기본값 `False`(실전)로 떨어졌습니다. `virtaul: true` 오타 하나로
    모의투자 의도가 실전 주문이 됩니다.

    Args:
        profile: 검사할 프로필. `dict` 가 아니면 예외
        path: 오류 메시지에 넣을 설정 파일 경로
        name: 다중 프로필일 때 프로필 이름. 단일 설정이면 `None`

    Returns:
        검증을 통과한 프로필

    Raises:
        ValueError: 모양이 아니거나, 모르는 키가 있거나, 필수 키가 빠진 경우
    """
    where = path if name is None else f"{path} 의 프로필 '{name}'"

    if not isinstance(profile, dict):
        raise ValueError(f"{where} 이(가) 매핑이 아닙니다: {type(profile).__name__}")

    if unknown := sorted(set(profile) - _PROFILE_KEYS):
        raise ValueError(
            f"{where} 에 모르는 키가 있습니다: {', '.join(unknown)}. 쓸 수 있는 키: {', '.join(sorted(_PROFILE_KEYS))}"
        )

    if missing := [key for key in _CREDENTIAL_KEYS if key not in profile]:
        raise ValueError(f"{where} 에 필수 키가 없습니다: {', '.join(missing)}")

    if _MODE_KEY not in profile:
        raise ValueError(
            f"{where} 에 `{_MODE_KEY}` 가 없습니다. 생략을 실전으로 해석하지 않습니다 — "
            f"모의는 `{_MODE_KEY}: true`, 실전은 `{_MODE_KEY}: false` 를 명시하세요."
        )

    return profile


def load_config(path: str = "config.yaml", profile: str | None = None) -> dict[str, Any]:
    """YAML 설정 파일을 읽습니다.

    구형 단일 설정과 다중 프로필 형식을 모두 지원합니다.

    다중 프로필 형식 예시::

        default: virtual
        configs:
            virtual:
                id: ...
                account: ...
                appkey: ...
                secretkey: ...
                virtual: true
            real:
                id: ...
                ...

    프로필 선택 순서:
        1. `profile` 인자
        2. 환경변수 `VMKIS_PROFILE`
        3. 다중 설정의 `default` 키
        4. 폴백 `'virtual'`

    Args:
        path: 설정 파일 경로
        profile: 사용할 프로필 이름

    Returns:
        선택된 프로필의 설정 딕셔너리

    Raises:
        ValueError: 지정한 프로필이 설정 파일에 없는 경우, 또는 프로필에 모르는
            키가 있거나 필수 키(`virtual` 포함)가 빠진 경우
    """
    profile = profile or _env("PROFILE")

    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if isinstance(cfg, dict) and "configs" in cfg:
        sel = profile or cfg.get("default") or "virtual"
        selected = cfg["configs"].get(sel)

        if not selected:
            raise ValueError(f"Profile '{sel}' not found in {path}")

        return _validate_profile(selected, path=path, name=sel)

    return _validate_profile(cfg, path=path)


def create_client(config_path: str = "config.yaml", keep_token: bool = True, profile: str | None = None) -> VmKis:
    """YAML 설정 파일로부터 `VmKis` 클라이언트를 생성합니다.

    설정의 `virtual`이 참이면 `KisAuth`를 만들어 `VmKis`의 `virtual_auth` 인자로
    전달합니다. 모의도메인 전용 인증 정보를 실전 인증 정보로 잘못 다루는 것을
    막기 위함입니다.

    Args:
        config_path: 설정 파일 경로
        keep_token: API 접속 토큰 자동 저장 여부
        profile: 사용할 프로필 이름

    Returns:
        생성된 `VmKis` 클라이언트
    """
    cfg = load_config(config_path, profile=profile)

    auth = KisAuth(
        id=cfg["id"],
        appkey=cfg["appkey"],
        secretkey=cfg["secretkey"],
        account=cfg["account"],
        # `.get(_MODE_KEY, False)` 가 아닙니다. 기본값을 두면 키가 빠지거나
        # 오타일 때 조용히 실전으로 붙습니다. `load_config` 가 이미 존재를
        # 보장하므로 여기서는 그냥 꺼냅니다.
        virtual=cfg[_MODE_KEY],
    )

    if auth.virtual:
        # 모의도메인 전용 자격증명: virtual_auth로 전달한다.
        return VmKis(None, auth, keep_token=keep_token)

    return VmKis(auth, keep_token=keep_token)


def save_config_interactive(path: str = "config.yaml") -> dict[str, Any]:
    """대화형으로 설정 값을 입력받아 YAML로 저장합니다.

    비밀키는 입력 시 화면에 표시하지 않으며, 파일을 쓰기 전에 확인을 받습니다.
    환경변수 `VMKIS_CONFIRM_SKIP=1`을 설정하면 확인 절차를 건너뜁니다
    (CI 스크립트용).

    Args:
        path: 저장할 설정 파일 경로

    Returns:
        저장된 설정 딕셔너리

    Raises:
        SystemExit: 사용자가 쓰기를 취소한 경우
    """
    data: dict[str, Any] = {}
    data["id"] = input("HTS id: ")
    data["account"] = input("Account (XXXXXXXX-XX): ")
    data["appkey"] = input("AppKey: ")
    data["secretkey"] = getpass.getpass("SecretKey (input hidden): ")
    v = input("Virtual (y/n): ").strip().lower()
    data[_MODE_KEY] = v in ("y", "yes", "true", "1")

    # 미리보기 (비밀키는 가린다)
    masked = (data["secretkey"][:4] + "...") if data.get("secretkey") else ""
    print(f"\nAbout to write the following config to: {path}")
    print(f"  id: {data['id']}")
    print(f"  account: {data['account']}")
    print(f"  appkey: {data['appkey']}")
    print(f"  secretkey: {masked}")
    print(f"  {_MODE_KEY}: {data[_MODE_KEY]}\n")

    confirm = _env("CONFIRM_SKIP") == "1"

    if not confirm:
        ans = input("Write config file? (y/N): ").strip().lower()
        confirm = ans in ("y", "yes")

    if not confirm:
        raise SystemExit("Aborted by user")

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    return data
