from pathlib import Path

import pytest

from vmkis.utils.workspace import get_cache_path, get_workspace_path


def test_get_workspace_and_cache_paths_resolve(monkeypatch, tmp_path):
    # make a temporary fake home directory
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    # monkeypatch Path.home to return our fake home
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    ws = get_workspace_path()
    assert isinstance(ws, Path)
    expected_ws = (fake_home / ".vmkis").resolve()
    assert ws == expected_ws
    # cache path should be a child "cache" under workspace
    cache = get_cache_path()
    assert isinstance(cache, Path)
    assert cache == (expected_ws / "cache").resolve()


def test_get_workspace_path_is_idempotent_and_absolute(monkeypatch, tmp_path):
    fake_home = tmp_path / "another_home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    p1 = get_workspace_path()
    p2 = get_workspace_path()
    # both calls return the same resolved absolute Path
    assert p1 == p2
    assert p1.is_absolute()
    # the returned path ends with .vmkis
    assert p1.name == ".vmkis"


# ---------------------------------------------------------------------------
# v2.x 레거시 경로 폴백
#
# v3.0.0에서 작업공간이 ~/.pykis → ~/.vmkis로 바뀌었다. 기존 사용자의 토큰
# 캐시가 고아가 되지 않도록, 새 경로가 없고 예전 경로만 있으면 예전 경로를 쓴다.
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_home(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    return home


def test_prefers_new_path_when_neither_exists(fake_home):
    """둘 다 없으면 새 경로를 쓴다 (신규 사용자)"""
    assert get_workspace_path() == (fake_home / ".vmkis").resolve()


def test_falls_back_to_legacy_path_with_warning(fake_home):
    """예전 경로만 있으면 그것을 쓰고 DeprecationWarning을 낸다"""
    legacy = fake_home / ".pykis"
    legacy.mkdir()

    with pytest.warns(DeprecationWarning, match=r"\.vmkis"):
        assert get_workspace_path() == legacy.resolve()


def test_new_path_wins_when_both_exist(fake_home, recwarn):
    """둘 다 있으면 새 경로를 쓰고 경고하지 않는다"""
    (fake_home / ".pykis").mkdir()
    (fake_home / ".vmkis").mkdir()

    assert get_workspace_path() == (fake_home / ".vmkis").resolve()
    assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]


def test_cache_path_follows_legacy_fallback(fake_home):
    """캐시 경로도 폴백된 작업공간을 따라간다"""
    legacy = fake_home / ".pykis"
    legacy.mkdir()

    with pytest.warns(DeprecationWarning):
        assert get_cache_path() == (legacy / "cache").resolve()
