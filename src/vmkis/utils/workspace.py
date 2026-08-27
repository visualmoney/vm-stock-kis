import warnings
from pathlib import Path

_LEGACY_WORKSPACE_NAME = ".pykis"
_WORKSPACE_NAME = ".vmkis"


def get_workspace_path() -> Path:
    """VmKis의 기본 작업공간 폴더를 반환합니다.

    v3.0.0에서 `~/.pykis`가 `~/.vmkis`로 바뀌었습니다. 새 경로가 아직 없고 예전
    경로만 있으면 예전 경로를 계속 씁니다. 그렇게 하지 않으면 기존 사용자의 토큰
    캐시가 고아가 되어 재인증이 강제됩니다.

    이 fallback은 v4.0.0에서 제거됩니다.
    """
    workspace = (Path.home() / _WORKSPACE_NAME).resolve()

    if workspace.exists():
        return workspace

    legacy = (Path.home() / _LEGACY_WORKSPACE_NAME).resolve()

    if legacy.exists():
        warnings.warn(
            f"작업공간 경로가 '{_LEGACY_WORKSPACE_NAME}'에서 '{_WORKSPACE_NAME}'으로 바뀌었습니다. "
            f"기존 경로({legacy})를 계속 사용합니다. "
            f"'{workspace}'로 옮기면 이 경고가 사라집니다. 이 폴백은 v4.0.0에서 제거됩니다.",
            DeprecationWarning,
            stacklevel=2,
        )
        return legacy

    return workspace


def get_cache_path() -> Path:
    """VmKis의 캐시 폴더를 반환합니다."""
    return (get_workspace_path() / "cache").resolve()
