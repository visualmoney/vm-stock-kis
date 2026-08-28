"""v2.x 호환 별칭 테스트.

이 포크의 첫 릴리스(0.0.1)에서 배포명·모듈명·클래스명·환경변수가 모두
바뀌었다. 업스트림 `python-kis` 사용자의 코드를 조용히 깨뜨리지 않도록
아래 셋에 폴백을 둔다. 전부 1.0.0에서 제거된다.

  1. `vmkis.PyKis` → `VmKis` 별칭
  2. `~/.pykis` 작업공간 (tests/unit/utils/test_workspace.py)
  3. `PYKIS_*` 환경변수

`pykis` 패키지 자체의 호환 shim은 **배포하지 않는다**. 업스트림
`python-kis` 휠과 디스크에서 파일이 충돌해, 둘 다 설치한 사용자가
한쪽을 uninstall하면 다른 쪽 파일이 지워지기 때문이다.
"""

import warnings

import pytest

import vmkis
from vmkis import helpers


class TestPyKisAlias:
    """`PyKis` → `VmKis` 별칭"""

    def test_alias_is_the_same_object(self):
        """동일 객체여야 isinstance 검사가 그대로 동작한다"""
        with pytest.warns(DeprecationWarning):
            assert vmkis.PyKis is vmkis.VmKis

    def test_alias_warns_with_new_name(self):
        alias_name = "PyKis"
        with pytest.warns(DeprecationWarning, match="VmKis"):
            getattr(vmkis, alias_name)

    def test_alias_is_not_exported_by_star_import(self):
        """`__all__`에 넣으면 `from vmkis import *`가 옛 이름을 계속 퍼뜨린다"""
        assert "PyKis" not in vmkis.__all__
        assert "VmKis" in vmkis.__all__

    def test_unknown_attribute_still_raises(self):
        missing_name = "NoSuchThing"

        with pytest.raises(AttributeError):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                getattr(vmkis, missing_name)


class TestEnvironmentVariableFallback:
    """`VMKIS_*` → `PYKIS_*` 폴백"""

    @pytest.fixture(autouse=True)
    def clean_env(self, monkeypatch):
        for name in ("VMKIS_PROFILE", "PYKIS_PROFILE", "VMKIS_CONFIRM_SKIP", "PYKIS_CONFIRM_SKIP"):
            monkeypatch.delenv(name, raising=False)

    def test_returns_none_when_neither_is_set(self):
        assert helpers._env("PROFILE") is None

    def test_prefers_new_prefix(self, monkeypatch, recwarn):
        monkeypatch.setenv("VMKIS_PROFILE", "new")

        assert helpers._env("PROFILE") == "new"
        assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]

    def test_falls_back_to_legacy_prefix_with_warning(self, monkeypatch):
        monkeypatch.setenv("PYKIS_PROFILE", "legacy")

        with pytest.warns(DeprecationWarning, match="VMKIS_PROFILE"):
            assert helpers._env("PROFILE") == "legacy"

    def test_new_prefix_wins_when_both_are_set(self, monkeypatch, recwarn):
        monkeypatch.setenv("VMKIS_PROFILE", "new")
        monkeypatch.setenv("PYKIS_PROFILE", "legacy")

        assert helpers._env("PROFILE") == "new"
        assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]

    def test_load_config_honours_legacy_profile_variable(self, tmp_path, monkeypatch):
        """`load_config`가 폴백을 실제로 탄다"""
        import yaml

        config = {"default": "virtual", "configs": {"virtual": {"id": "v"}, "real": {"id": "r"}}}
        path = tmp_path / "config.yaml"
        path.write_text(yaml.dump(config), encoding="utf-8")
        monkeypatch.setenv("PYKIS_PROFILE", "real")

        with pytest.warns(DeprecationWarning):
            assert helpers.load_config(str(path))["id"] == "r"


class TestUserAgentAndPackageName:
    """배포명/모듈명 구분"""

    def test_package_name_is_the_distribution_name(self):
        """모듈명(vmkis)이 아니라 배포명이어야 importlib.metadata 조회가 된다"""
        from vmkis.__env__ import __package_name__

        assert __package_name__ == "vm-stock-kis"

    def test_user_agent_uses_class_name(self):
        from vmkis.__env__ import USER_AGENT, __version__

        assert USER_AGENT == f"VmKis/{__version__}"

    def test_version_is_not_the_unknown_fallback(self):
        """설치된 상태에서는 fallback 값이 나오면 안 된다"""
        from vmkis.__env__ import __version__

        assert not __version__.startswith("0.0.0")
