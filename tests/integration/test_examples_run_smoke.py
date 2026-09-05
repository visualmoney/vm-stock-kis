"""채운 설정이 있을 때만 `01_basic` 읽기 예제를 실행합니다. (#154)

예전 검사는 `template_account_profiles.yaml` 을 넘겼습니다. 그 파일은
`YOUR_HTS_ID` 자리표시자라 연기가 아니라 실패이거나, 운 좋으면 키 오류입니다.
채운 `configs/account_profiles.yaml` 이 없으면 skip 합니다.

주문·웹소켓 예제는 넣지 않습니다.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.requires_api]

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FILLED_CONFIG = REPO_ROOT / "configs" / "account_profiles.yaml"
TEMPLATE_MARK = "YOUR_HTS_ID"

_READ_ONLY_BASIC = (
    "hello_world.py",
    "keep_token.py",
    "get_quote.py",
    "get_chart.py",
    "get_orderbook.py",
    "trading_hours.py",
    "get_balance.py",
    "account_lookups.py",
)


def _filled_config() -> pathlib.Path:
    if os.environ.get("RUN_INTEGRATION") != "1":
        pytest.skip("RUN_INTEGRATION=1 일 때만 예제 연기를 돌립니다")
    if not FILLED_CONFIG.is_file():
        pytest.skip(f"{FILLED_CONFIG} 가 없습니다. 템플릿을 복사해 채우세요")
    text = FILLED_CONFIG.read_text(encoding="utf-8")
    if TEMPLATE_MARK in text:
        pytest.skip(f"{FILLED_CONFIG} 가 아직 템플릿입니다")
    return FILLED_CONFIG


@pytest.mark.parametrize("name", _READ_ONLY_BASIC)
def test_basic_read_example_runs_with_filled_config(name: str) -> None:
    cfg = _filled_config()
    script = REPO_ROOT / "examples" / "01_basic" / name
    proc = subprocess.run(
        [sys.executable, str(script), "--config", str(cfg)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, f"{name} 가 {proc.returncode}:\n{proc.stderr}\n{proc.stdout}"
