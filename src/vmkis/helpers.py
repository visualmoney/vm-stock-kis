"""초보자용 설정 헬퍼.

설정 파일에서 인증 정보를 읽어 `VmKis` 클라이언트를 만듭니다. 스키마와 검증은
`vmkis.config` 에 있고, 사양은 `docs/guidelines/CONFIG_SCHEMA.md` 입니다.

이 모듈이 하는 일은 **번역**입니다. 설정 파일은 앱과 계좌를 나눠 적지만
`KisAuth` 는 필드 5개짜리 평평한 구조라, 그 간극을 여기서 메웁니다.
"""

import getpass
import os
import warnings
from pathlib import Path
from typing import Any

import yaml

from vmkis.client.auth import KisAuth
from vmkis.config import AccountConfig, load_kis_config
from vmkis.kis import VmKis

__all__ = ["create_client", "save_config_interactive"]

DEFAULT_CONFIG_PATH = "configs/account_profiles.yaml"


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


def _to_auth(account: AccountConfig) -> KisAuth:
    """설정의 앱+계좌를 `KisAuth` 로 번역합니다."""
    return KisAuth(
        id=account.hts_id,
        appkey=account.app_key,
        secretkey=account.app_secret,
        account=account.account,
        paper=account.is_paper,
    )


def create_client(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    keep_token: bool | None = None,
    account: str | None = None,
) -> VmKis:
    """설정 파일로부터 `VmKis` 클라이언트를 생성합니다.

    모의투자 계좌면 `KisAuth` 를 `VmKis` 의 `paper_auth` 인자로 전달합니다.
    모의도메인 전용 인증 정보를 실전 인증 정보로 잘못 다루는 것을 막기 위함입니다.

    토큰 저장 경로는 설정이 정합니다 — 앱 이름에서 파생되므로 앱이 다르면 토큰
    파일도 반드시 다릅니다. `keep_token=False` 를 주면 저장하지 않습니다.

    Args:
        config_path: 설정 파일 경로
        keep_token: 토큰 저장 여부. 생략하면 설정이 정한 경로에 저장합니다
        account: 쓸 계좌 이름. 생략하면 `VMKIS_ACCOUNT`, 그다음 `default_account`

    Returns:
        생성된 `VmKis` 클라이언트

    Raises:
        ValueError: 설정이 스키마를 어긴 경우 (`docs/guidelines/CONFIG_SCHEMA.md`)
    """
    config = load_kis_config(config_path)
    selected = config.account(account or _env("ACCOUNT"))

    auth = _to_auth(selected)
    token_path: bool | Path = False if keep_token is False else selected.token_path

    if token_path is not False:
        Path(token_path).parent.mkdir(parents=True, exist_ok=True)

    shared: dict[str, Any] = {
        "keep_token": token_path,
        "user_agent": config.user_agent,
        # #70 이전에는 여기에 `{"live": "real", "paper": "virtual"}` 번역표가
        # 있었습니다. 설정과 코드가 같은 어휘를 쓰게 되어 사라졌습니다.
        # 키 검증은 `config._parse_endpoints` 가 `MODES` 로 이미 했습니다.
        "endpoints": dict(config.endpoints or {}),
    }

    if selected.is_paper:
        return VmKis(None, auth, **shared)

    return VmKis(auth, **shared)


def save_config_interactive(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """대화형으로 설정 값을 입력받아 YAML로 저장합니다.

    비밀키는 입력 시 화면에 표시하지 않으며, 파일을 쓰기 전에 확인을 받습니다.
    환경변수 `VMKIS_CONFIRM_SKIP=1`을 설정하면 확인 절차를 건너뜁니다
    (CI 스크립트용).

    앱과 계좌를 하나씩만 만듭니다. 둘 이상이 필요하면 만들어진 파일을 손으로
    늘리세요 — 대화형으로 N개를 받는 것은 템플릿을 고치는 것보다 번거롭습니다.

    Args:
        path: 저장할 설정 파일 경로

    Returns:
        저장된 설정 딕셔너리

    Raises:
        SystemExit: 사용자가 쓰기를 취소한 경우
    """
    hts_id = input("HTS id: ")
    account_no = input("Account number (8 digits): ")
    product_code = input("Product code (01): ") or "01"
    app_key = input("AppKey: ")
    app_secret = getpass.getpass("AppSecret (input hidden): ")
    mode = "paper" if input("Paper trading? (y/n): ").strip().lower() in ("y", "yes", "true", "1") else "live"

    app_name = f"app_{mode}1"
    account_name = f"acc_{mode}1"

    data: dict[str, Any] = {
        "version": 1,
        "apps": {
            app_name: {
                "mode": mode,
                "hts_id": hts_id,
                "app_key": app_key,
                "app_secret": app_secret,
            }
        },
        "accounts": {
            account_name: {
                "app": app_name,
                "account_no": account_no,
                "product_code": product_code,
            }
        },
        "default_account": account_name,
    }

    # 미리보기 (비밀키는 가린다)
    masked = (app_secret[:4] + "...") if app_secret else ""
    print(f"\nAbout to write the following config to: {path}")
    print(f"  apps.{app_name}.mode: {mode}")
    print(f"  apps.{app_name}.hts_id: {hts_id}")
    print(f"  apps.{app_name}.app_key: {app_key}")
    print(f"  apps.{app_name}.app_secret: {masked}")
    print(f"  accounts.{account_name}: {account_no}-{product_code}\n")

    confirm = _env("CONFIRM_SKIP") == "1"

    if not confirm:
        ans = input("Write config file? (y/N): ").strip().lower()
        confirm = ans in ("y", "yes")

    if not confirm:
        raise SystemExit("Aborted by user")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    return data
