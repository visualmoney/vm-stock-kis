"""루트에서 내부 타입을 가져오면 실패하는지 봅니다. (#34)"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_types_and_core_imports():
    from vmkis import KisAuth, VmKis

    assert VmKis is not None
    assert KisAuth is not None

    from vmkis import Balance, Chart, Order, Orderbook, Quote

    assert Quote is not None
    assert Balance is not None
    assert Order is not None
    assert Chart is not None
    assert Orderbook is not None


def test_deprecated_root_import_is_gone():
    with pytest.raises(ImportError):
        from vmkis import KisObjectProtocol  # noqa: F401


def test_types_module_still_exports_protocols():
    from vmkis.types import KisObjectProtocol

    assert KisObjectProtocol is not None


def test_types_imports_vmkis_kis_not_hub() -> None:
    """허브 인스턴스 이름과 모듈 경로 vmkis.kis 를 섞지 않는다."""
    text = (REPO_ROOT / "src" / "vmkis" / "types.py").read_text(encoding="utf-8")

    assert "from vmkis.kis import VmKis" in text
    assert "from vmkis.hub import" not in text


def test_pykis_root_alias_is_gone():
    """#33 과 같은 표면. 루트 __getattr__ 이 없어지면 같이 사라집니다."""
    import vmkis

    with pytest.raises(AttributeError):
        _ = vmkis.PyKis
