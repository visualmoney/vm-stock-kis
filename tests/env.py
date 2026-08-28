import os
import unittest
from typing import Literal

import vmkis.logging
from vmkis import VmKis

try:
    import dotenv

    dotenv.load_dotenv()
except ImportError:
    pass


#: 도메인별로 반드시 있어야 하는 환경변수.
#: 저장소 루트에 `.env` 를 두면 python-dotenv 가 자동으로 읽습니다.
REQUIRED_ENV: dict[str, tuple[str, ...]] = {
    "real": (
        "VMKIS_HTS_ID",
        "VMKIS_ACCOUNT_NUMBER",
        "VMKIS_APPKEY",
        "VMKIS_SECRETKEY",
    ),
    "virtual": (
        "VMKIS_HTS_ID",
        "VMKIS_APPKEY",
        "VMKIS_SECRETKEY",
        "VMKIS_VIRTUAL_ACCOUNT_NUMBER",
        "VMKIS_VIRTUAL_HTS_ID",
        "VMKIS_VIRTUAL_APPKEY",
        "VMKIS_VIRTUAL_SECRETKEY",
    ),
}


def require_credentials(domain: Literal["real", "virtual"] = "real") -> None:
    """자격증명이 없으면 테스트를 **건너뜁니다**.

    이 함수가 없으면 자격증명 없는 환경에서 `VmKis` 생성자가 `ValueError` 를
    내고, 그것이 `setUpClass` 에서 터지므로 pytest 가 **error** 로 보고합니다.
    새로 클론한 사람이 `uv run pytest` 를 처음 돌리면 17개가 빨갛게 뜹니다.

    코드는 멀쩡하고 환경이 없을 뿐입니다. 그건 error 가 아니라 skip 입니다.
    (`tests/performance/test_perf_dummy.py` 가 `RUN_PERF` 로 같은 방식을 씁니다.)

    `unittest.SkipTest` 를 쓰는 이유: 이 함수의 호출자가 전부
    `unittest.TestCase.setUpClass` 인데, unittest 는 여기서 발생한 `SkipTest` 를
    받아 **클래스 전체를 건너뜁니다.** pytest 도 그대로 skip 으로 보고합니다.
    """
    missing = [name for name in REQUIRED_ENV[domain] if not os.getenv(name)]

    if missing:
        raise unittest.SkipTest(
            f"{domain} 도메인 자격증명이 없어 건너뜁니다. "
            f"누락: {', '.join(missing)} — 저장소 루트에 .env 를 만들어 채우세요."
        )


def load_vmkis(
    domain: Literal["real", "virtual"] = "real",
    use_websocket: bool = True,
) -> VmKis:
    # 자격증명이 없으면 여기서 skip 으로 빠집니다. 호출자마다 검사할 필요가 없습니다.
    require_credentials(domain)

    vmkis.logging.setLevel("DEBUG")

    if domain == "real":
        kis = VmKis(
            id=os.getenv("VMKIS_HTS_ID"),
            account=os.getenv("VMKIS_ACCOUNT_NUMBER"),
            appkey=os.getenv("VMKIS_APPKEY"),
            secretkey=os.getenv("VMKIS_SECRETKEY"),
            use_websocket=use_websocket,
            keep_token=os.getenv("VMKIS_KEEP_TOKEN", "false").lower() == "true",
        )
    else:
        kis = VmKis(
            id=os.getenv("VMKIS_HTS_ID"),
            account=os.getenv("VMKIS_VIRTUAL_ACCOUNT_NUMBER"),
            appkey=os.getenv("VMKIS_APPKEY"),
            secretkey=os.getenv("VMKIS_SECRETKEY"),
            virtual_id=os.getenv("VMKIS_VIRTUAL_HTS_ID"),
            virtual_appkey=os.getenv("VMKIS_VIRTUAL_APPKEY"),
            virtual_secretkey=os.getenv("VMKIS_VIRTUAL_SECRETKEY"),
            use_websocket=use_websocket,
            keep_token=os.getenv("VMKIS_KEEP_TOKEN", "false").lower() == "true",
        )

    return kis
