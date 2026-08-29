"""`examples/` 가 부르는 공개 API 의 인자가 실제 시그니처와 맞는지 봅니다. (이슈 #84)

## 왜 이 검사가 필요한가

#75 가 `create_client` 의 `profile` 을 `account` 로 바꾸면서 `examples/01_basic/`
3개만 고치고 **7개를 놓쳤습니다.** 그 7개는 실행하면 이렇게 죽습니다.

```text
TypeError: create_client() got an unexpected keyword argument 'profile'
```

## 왜 기존 검사가 못 잡았나

`tests/integration/test_examples_run_smoke.py` 가 예제를 실제로 **실행**합니다.
그런데

1. `RUN_INTEGRATION=1` 없이는 통째로 skip 이고, CI 는 그 변수를 주지 않습니다
2. 실행 방식이라 **자격증명과 네트워크가 필요**합니다

**이 결함은 둘 다 필요 없습니다.** `create_client` 는 호출되는 순간 죽으므로
서버에 닿을 일이 없습니다. `--help` 로 돌리는 것도 답이 아닙니다 — argparse 가
`create_client` 보다 먼저 끝나 인자 오류가 드러나지 않습니다.

그래서 **AST 로 호출부를 읽어 실제 시그니처와 대조**합니다. 자격증명도
네트워크도 없이 돌고, 다음 개명도 같은 자리에서 잡힙니다.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
from collections.abc import Callable
from typing import Any

import pytest

from vmkis import KisAuth, SimpleKIS, VmKis, create_client, save_config_interactive

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"

#: 예제가 부르는 공개 진입점. 이름은 **예제가 쓰는 이름**입니다.
CHECKED: dict[str, Callable[..., Any]] = {
    "create_client": create_client,
    "save_config_interactive": save_config_interactive,
    "KisAuth": KisAuth,
    "SimpleKIS": SimpleKIS,
    "VmKis": VmKis,
}


def _example_files() -> list[pathlib.Path]:
    return sorted(p for p in EXAMPLES.rglob("*.py") if "__pycache__" not in p.parts)


def _callee_name(node: ast.Call) -> str | None:
    """`f(...)` 와 `mod.f(...)` 에서 마지막 이름을 꺼냅니다."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _violations(source: str, origin: str) -> list[str]:
    problems: list[str] = []

    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue

        name = _callee_name(node)
        target = CHECKED.get(name or "")
        if target is None:
            continue

        params = inspect.signature(target).parameters
        accepts_var_kw = any(p.kind is p.VAR_KEYWORD for p in params.values())
        keyword_ok = {n for n, p in params.items() if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)}

        for kw in node.keywords:
            if kw.arg is None:  # `**something` — 정적으로는 알 수 없습니다
                continue
            if kw.arg not in keyword_ok and not accepts_var_kw:
                problems.append(
                    f"{origin}:{node.lineno} — {name}(...) 에 `{kw.arg}=` 를 넘깁니다. "
                    f"받는 이름은 {sorted(keyword_ok)} 입니다"
                )

        positional_ok = sum(1 for p in params.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))
        given = sum(1 for a in node.args if not isinstance(a, ast.Starred))
        if given > positional_ok and not any(p.kind is p.VAR_POSITIONAL for p in params.values()):
            problems.append(
                f"{origin}:{node.lineno} — {name}(...) 에 위치 인자 {given}개를 넘깁니다. "
                f"받는 것은 {positional_ok}개입니다"
            )

    return problems


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_example_calls_match_public_signatures(path: pathlib.Path) -> None:
    problems = _violations(path.read_text(encoding="utf-8"), str(path.relative_to(REPO_ROOT)))
    assert not problems, "예제가 존재하지 않는 인자를 넘깁니다:\n  " + "\n  ".join(problems)


def test_checker_actually_sees_the_examples() -> None:
    """검사기가 **아무것도 안 보는 상태**를 막습니다.

    경로가 틀리거나 예제가 `create_client` 를 그만 쓰면, 위 테스트는 위반이
    0건이라 조용히 통과합니다. 그때는 검사가 아니라 장식입니다.
    """
    files = _example_files()
    assert len(files) >= 10, f"예제 파일이 {len(files)}개뿐입니다. 경로가 맞습니까? {EXAMPLES}"

    seen = {
        _callee_name(node)
        for path in files
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.Call)
    }
    assert "create_client" in seen, "예제 어디에도 create_client 호출이 없습니다"


def test_checker_catches_the_original_defect() -> None:
    """#84 의 결함을 그대로 먹여 실제로 잡히는지 봅니다.

    회귀 테스트를 되돌려 확인하는 대신, **결함을 문자열로 박아** 둡니다.
    예제가 다시 고쳐져도 이 검사기 자체의 성능은 계속 검증됩니다.
    """
    defect = "create_client(config_path, profile=profile)\n"
    problems = _violations(defect, "<결함 재현>")

    assert problems, "검사기가 #84 의 원래 결함을 못 잡습니다"
    assert "profile" in problems[0]
    assert "account" in problems[0]
