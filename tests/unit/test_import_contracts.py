"""import-linter 계약이 실제로 무언가를 검사하고 있는지 확인합니다.

계약의 **내용**은 `lint-imports` 가 검사합니다(CI 의 lint 잡, 규칙은
`pyproject.toml` 의 `[tool.importlinter]`). 여기서 보는 것은 계약이 놓치는 두 가지
— 계약이 **아무것도 못 보는 상태**와 계약이 **볼 수 없는 위반**입니다.
"""

from __future__ import annotations

import ast
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
PACKAGE_DIR = SRC / "vmkis"


def _load_pyproject() -> dict:
    if sys.version_info >= (3, 11):
        import tomllib
    else:  # import-linter 가 3.11 미만에서 tomli 를 함께 설치합니다.
        tomllib = pytest.importorskip("tomli", reason="tomli 는 import-linter 의 의존성입니다")

    with (REPO_ROOT / "pyproject.toml").open("rb") as fp:
        return tomllib.load(fp)


def _module_name(path: pathlib.Path) -> str:
    parts = list(path.relative_to(SRC).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _source_modules() -> set[str]:
    return {_module_name(p) for p in PACKAGE_DIR.rglob("*.py") if "__pycache__" not in p.parts}


def test_contract_graph_covers_every_source_module() -> None:
    """설정된 루트가 `src/vmkis` 의 모든 모듈을 그래프에 담아야 합니다.

    grimp 은 루트 패키지를 스캔할 때 `__init__.py` 가 없는 디렉터리(암묵적
    네임스페이스 패키지)를 **건너뜁니다.** 이슈 #50 당시 `src/vmkis` 의 디렉터리
    18개 중 13개가 그 상태여서, 루트 하나만 주면 모듈 92개 중 20개만 잡히고
    `utils` · `client` · `responses` · `api` · `adapter` 가 통째로 사라졌습니다.

    빠진 것이 계약의 `source_modules` 면 import-linter 가
    `Module 'vmkis.utils' does not exist.` 로 죽어 소리를 냅니다. 그러나 빠진 것이
    `forbidden_modules` 쪽이거나 계약에 아직 안 걸린 서브패키지면 **조용히 통과**합니다.

    이슈 #64 에서 `__init__.py` 를 채워 원인을 없앴습니다. 이 테스트는 그것이
    유지되는지를 봅니다 — `__init__.py` 없는 디렉터리가 새로 생기면 여기서 잡힙니다.
    """
    # grimp 은 lint 그룹(import-linter)이 끌고 옵니다. `--group test` 만 설치한
    # 환경에서는 이 검사를 건너뜁니다. 아래 AST 검사는 그런 환경에서도 돕니다.
    grimp = pytest.importorskip("grimp", reason="import-linter(lint 그룹)가 설치되어야 합니다")

    # `root_package`(단수) / `root_packages`(복수) 둘 다 import-linter 의 유효한
    # 설정입니다. 어느 쪽으로 적혀 있든 같은 성질을 검사합니다.
    session = _load_pyproject()["tool"]["importlinter"]
    roots = session.get("root_packages") or [session["root_package"]]
    graph = grimp.build_graph(*roots)

    missing = sorted(_source_modules() - set(graph.modules))

    assert not missing, (
        "다음 모듈이 import-linter 그래프에 없습니다. 계약이 이들을 검사하지 않습니다.\n"
        "해당 디렉터리에 __init__.py 가 있는지 확인하세요(이슈 #64).\n  " + "\n  ".join(missing)
    )


# 2026-11-15 에 파일 상단으로 올려 `import vmkis` 가 깨지는 곳만 모았습니다.
# 같은 날 올려도 로드가 된 곳(`adapter/websocket/price.py`,
# `adapter/product/quote.py` 의 차트 import, `kis.py` 의 `token_issue`)은
# 순환이 아니므로 여기 없습니다.
CYCLE_LAZY_IMPORTS: tuple[tuple[str, str], ...] = (
    ("adapter/account_product/order_modify.py", "vmkis.api.account.order_modify"),
    ("adapter/websocket/execution.py", "vmkis.api.websocket.order_execution"),
    ("api/account/order.py", "vmkis.api.account.pending_order"),
    ("api/account/order.py", "vmkis.api.account.orderable_amount"),
    ("api/account/order.py", "vmkis.api.account.balance"),
    ("api/base/market.py", "vmkis.api.stock.info"),
    ("api/base/product.py", "vmkis.api.stock.info"),
    ("api/base/product.py", "vmkis.scope.stock"),
    ("api/stock/trading_hours.py", "vmkis.api.stock.day_chart"),
)


def _comment_above(lines: list[str], lineno: int) -> str:
    index = lineno - 2
    while index >= 0 and lines[index].strip() == "":
        index -= 1
    if index < 0:
        return ""
    return lines[index].strip()


def test_cycle_lazy_imports_name_the_cycle() -> None:
    """순환 우회 지연 import 바로 위에 사유가 있어야 합니다 (#175).

    주석을 지우면 이 테스트가 실패합니다. import-linter 는 이 지연 import 를
    계약에 넣지 않습니다(api ↔ adapter 는 의도적 순환).
    """
    missing: list[str] = []
    for rel, module in CYCLE_LAZY_IMPORTS:
        path = PACKAGE_DIR / rel
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        found = False
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for sub in ast.walk(node):
                if not isinstance(sub, ast.ImportFrom) or sub.module != module or not sub.lineno:
                    continue
                found = True
                comment = _comment_above(lines, sub.lineno)
                if not (comment.startswith("#") and "순환" in comment):
                    missing.append(f"{rel}:{sub.lineno} {module} 앞에 순환 사유가 없습니다 ({comment!r})")
        if not found:
            missing.append(f"{rel} 에 함수 안 `{module}` import 가 없습니다")

    assert not missing, "\n".join(missing)


def test_messaging_does_not_import_api() -> None:
    """`client/messaging.py` 는 api 를 어디에서도 import 하지 않습니다 (#176).

    approval key 는 `VmKis.websocket_approval_key` 가 발급합니다.
    예전에는 함수 안 import 1건이 `ignore_imports` 면제였고, 그 면제는
    위치를 보지 않아 파일 상단으로 올려도 `lint-imports` 가 통과했습니다.
    """
    source = (PACKAGE_DIR / "client" / "messaging.py").read_text(encoding="utf-8")
    offenders = [
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("vmkis.api")
    ]

    assert not offenders, f"client/messaging.py 가 api 를 import 합니다: {offenders}"
