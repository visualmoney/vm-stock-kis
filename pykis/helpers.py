"""초보자용 설정 헬퍼.

YAML 설정 파일에서 인증 정보를 읽어 `PyKis` 클라이언트를 만들거나, 대화형으로
설정 파일을 작성합니다.
"""

import getpass
import os
from typing import Any

import yaml

from pykis.client.auth import KisAuth
from pykis.kis import PyKis

__all__ = ["create_client", "load_config", "save_config_interactive"]


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
        2. 환경변수 `PYKIS_PROFILE`
        3. 다중 설정의 `default` 키
        4. 폴백 `'virtual'`

    Args:
        path: 설정 파일 경로
        profile: 사용할 프로필 이름

    Returns:
        선택된 프로필의 설정 딕셔너리

    Raises:
        ValueError: 지정한 프로필이 설정 파일에 없는 경우
    """
    profile = profile or os.environ.get("PYKIS_PROFILE")

    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if isinstance(cfg, dict) and "configs" in cfg:
        sel = profile or cfg.get("default") or "virtual"
        selected = cfg["configs"].get(sel)

        if not selected:
            raise ValueError(f"Profile '{sel}' not found in {path}")

        return selected

    return cfg


def create_client(config_path: str = "config.yaml", keep_token: bool = True, profile: str | None = None) -> PyKis:
    """YAML 설정 파일로부터 `PyKis` 클라이언트를 생성합니다.

    설정의 `virtual`이 참이면 `KisAuth`를 만들어 `PyKis`의 `virtual_auth` 인자로
    전달합니다. 모의도메인 전용 인증 정보를 실전 인증 정보로 잘못 다루는 것을
    막기 위함입니다.

    Args:
        config_path: 설정 파일 경로
        keep_token: API 접속 토큰 자동 저장 여부
        profile: 사용할 프로필 이름

    Returns:
        생성된 `PyKis` 클라이언트
    """
    cfg = load_config(config_path, profile=profile)

    auth = KisAuth(
        id=cfg["id"],
        appkey=cfg["appkey"],
        secretkey=cfg["secretkey"],
        account=cfg["account"],
        virtual=cfg.get("virtual", False),
    )

    if auth.virtual:
        # 모의도메인 전용 자격증명: virtual_auth로 전달한다.
        return PyKis(None, auth, keep_token=keep_token)

    return PyKis(auth, keep_token=keep_token)


def save_config_interactive(path: str = "config.yaml") -> dict[str, Any]:
    """대화형으로 설정 값을 입력받아 YAML로 저장합니다.

    비밀키는 입력 시 화면에 표시하지 않으며, 파일을 쓰기 전에 확인을 받습니다.
    환경변수 `PYKIS_CONFIRM_SKIP=1`을 설정하면 확인 절차를 건너뜁니다
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
    data["virtual"] = v in ("y", "yes", "true", "1")

    # 미리보기 (비밀키는 가린다)
    masked = (data["secretkey"][:4] + "...") if data.get("secretkey") else ""
    print(f"\nAbout to write the following config to: {path}")
    print(f"  id: {data['id']}")
    print(f"  account: {data['account']}")
    print(f"  appkey: {data['appkey']}")
    print(f"  secretkey: {masked}")
    print(f"  virtual: {data['virtual']}\n")

    confirm = os.environ.get("PYKIS_CONFIRM_SKIP") == "1"

    if not confirm:
        ans = input("Write config file? (y/N): ").strip().lower()
        confirm = ans in ("y", "yes")

    if not confirm:
        raise SystemExit("Aborted by user")

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    return data
