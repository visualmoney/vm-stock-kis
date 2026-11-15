"""살아 있는 문서가 없는 RateLimiter.wait() 를 다시 그리면 실패합니다. (#167)

`test_docs_signatures.py` 는 python 코드펜스의 import·공개 진입점만 봅니다.
ARCHITECTURE.md 시세 흐름은 ```text 다이어그램이라 그 검사가 통과합니다.
"""

from __future__ import annotations

import pathlib

from vmkis.utils.rate_limit import RateLimiter

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

SKIP_PARTS = {"reports", "dev_logs", "prompts", "archive", "generated"}

#: 코드에 없는 옛 스케치. 비교 보고서 7.4 가 적은 실제 호출은 acquire() 입니다.
FORBIDDEN = (
    "RateLimiter.wait",
    "rate_limiter.wait",
    "rate_limiter.on_success",
    "rate_limiter.on_error",
)


def _living_markdown() -> list[pathlib.Path]:
    found: set[pathlib.Path] = set()
    for root in (REPO_ROOT / "docs", REPO_ROOT):
        globber = root.rglob if root != REPO_ROOT else root.glob
        for p in globber("*.md"):
            if SKIP_PARTS & set(p.relative_to(REPO_ROOT).parts):
                continue
            if ".venv" in p.parts:
                continue
            found.add(p)
    return sorted(found)


def _hits(text: str) -> list[str]:
    return [needle for needle in FORBIDDEN if needle in text]


def test_rate_limiter_has_acquire_and_not_wait() -> None:
    assert hasattr(RateLimiter, "acquire")
    for name in ("wait", "on_success", "on_error"):
        assert not hasattr(RateLimiter, name), f"RateLimiter.{name} 은 없습니다"


def test_checker_fails_on_the_old_wait_sketch() -> None:
    """결함을 문서로 되살린 조각입니다. 검사기가 이것을 못 보면 통과만 하는 검사입니다."""
    sketch = """
RateLimiter.wait()  (rate limit check)
rate_limiter.wait()
rate_limiter.on_success()
rate_limiter.on_error()
"""
    found = _hits(sketch)
    assert found == list(FORBIDDEN), f"검사기가 옛 스케치를 못 잡습니다: {found}"


def test_living_docs_do_not_teach_rate_limiter_wait() -> None:
    problems = [
        f"{path.relative_to(REPO_ROOT)} — {needle}"
        for path in _living_markdown()
        for needle in _hits(path.read_text(encoding="utf-8"))
    ]
    assert not problems, "살아 있는 문서가 없는 RateLimiter API 를 적습니다:\n  " + "\n  ".join(problems)
