"""저장소가 배포하는 `config.example*.yaml` 3개가 실제로 읽히는지 확인합니다.

이 파일은 원래 `test_load_config_get_quote.py` 였고, `examples/01_basic/get_quote.py`
안의 **복사본** `load_config` 를 importlib 로 끌어와 테스트했습니다. 그 복사본이
5벌 중 하나였고, 테스트가 중복을 고착시키고 있었습니다 (#69).

지금은 라이브러리의 `load_config` 하나를 대상으로 합니다. 검사 대상 파일은
그대로 두었습니다 — 배포되는 예제 설정이 파싱되고 **검증을 통과하는지**는
여전히 값어치가 있고, 이제는 여분·오타 키가 예제에 섞여도 여기서 걸립니다.
"""

import pathlib

import pytest

from vmkis import load_config

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """`VMKIS_PROFILE` 이 새어 들어오면 프로필 선택이 달라집니다."""
    monkeypatch.delenv("VMKIS_PROFILE", raising=False)
    monkeypatch.delenv("PYKIS_PROFILE", raising=False)


def test_single_virtual_example():
    cfg = load_config(path=str(REPO_ROOT / "config.example.virtual.yaml"))

    assert cfg["id"] == "YOUR_VIRTUAL_ID"
    assert cfg["virtual"] is True


def test_single_real_example():
    cfg = load_config(path=str(REPO_ROOT / "config.example.real.yaml"))

    assert cfg["id"] == "YOUR_REAL_ID"
    assert cfg["virtual"] is False


def test_multi_example_uses_default():
    cfg = load_config(path=str(REPO_ROOT / "config.example.yaml"))

    assert cfg["id"] == "YOUR_VIRTUAL_ID"
    assert cfg["virtual"] is True


def test_multi_example_select_real():
    cfg = load_config(path=str(REPO_ROOT / "config.example.yaml"), profile="real")

    assert cfg["id"] == "YOUR_REAL_ID"
    assert cfg["virtual"] is False
