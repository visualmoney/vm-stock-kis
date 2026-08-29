"""1.0.0 게이트를 **감시**합니다. (이슈 #30)

## 왜 테스트인가 — 이슈도 문서도 아닌

CLAUDE.md 가 정한 것입니다.

> | 외부 조건 감시 | **검사**(CI·게시 전 스텝) 또는 그 조건이 걸린 파일의 주석 |
> | 이슈로 만들면 영원히 안 닫히고, 문서에 적으면 아무도 안 봅니다 |

`#30` 의 원래 선행 조건이 *"0.0.x 가 실사용자에게 충분히 노출되었는가"* 였습니다.
**판정 기준이 없어서 아무도 판정할 수 없었고**, 그 이슈에 서브이슈 4건이
매달린 채 멈춰 있었습니다.

2026-08-30 에 측정 가능한 게이트로 바꿨습니다. 그 게이트를 여기서 감시합니다.

## 근거 — 왜 지금은 아닌가 (2026-08-30 실측)

```text
0.0.1 게시   2026-08-28T04:05  ┐
0.1.0 게시   2026-08-29T16:21  ┘  0.0.x 수명 약 36시간

PyPI 다운로드 111건
  last_day == last_week == last_month == 111
  → 전부 최근 하루 안. 미러/봇 패턴이고 사람이 썼다는 증거가 없습니다.
```

호환 폴백 4종은 살아 있고 `DeprecationWarning` 도 발화하지만, **그 경고를
사람이 본 적이 있는지 알 수 없습니다.** 아무도 안 쓴 폴백을 제거하는 것은
마이그레이션 기간을 준 것이 아닙니다.
"""

from __future__ import annotations

import datetime

#: 0.1.0 게시일 (PyPI `upload_time`, UTC).
PUBLISHED_0_1_0 = datetime.date(2026, 8, 29)

#: 마이그레이션 기간. 90일은 분기 하나로, 사용자가 릴리스를 한 번은 만날 만한
#: 길이입니다. 근거가 더 생기면 줄이거나 늘리세요 — **숫자보다 판정 가능한
#: 것이 중요합니다.**
MIGRATION_WINDOW = datetime.timedelta(days=90)

#: 이 날짜가 지나면 #30 을 다시 봅니다.
REVISIT_ON = PUBLISHED_0_1_0 + MIGRATION_WINDOW


def test_one_zero_gate_is_revisited_on_schedule() -> None:
    """게이트 날짜가 지나면 **실패해서** #30 을 다시 보게 만듭니다.

    일부러 시한폭탄입니다. 조용히 지나가면 `#30` 은 또 잊히고, 서브이슈
    `#33`·`#34`·`#35`·`#36` 이 계속 `blocked` 로 남습니다. 그것이 이 게이트를
    만든 이유입니다.

    **실패했다고 코드가 잘못된 것이 아닙니다.** 판단할 때가 됐다는 뜻입니다.
    """
    today = datetime.date.today()

    assert today < REVISIT_ON, (
        f"1.0.0 게이트 조건 하나가 충족됐습니다 — 0.1.0 게시 후 "
        f"{(today - PUBLISHED_0_1_0).days}일 (기준 {MIGRATION_WINDOW.days}일).\n"
        f"\n"
        f"이슈 #30 을 다시 보세요. 남은 조건은 **외부 사용 신호 1건 이상**입니다\n"
        f"(이슈 · 질문 · 봇 아닌 다운로드).\n"
        f"\n"
        f"  충족되었다면 : #30 의 needs-decision 을 떼고 #33·#34·#35·#36 의\n"
        f"                 blocked 를 함께 뗀 뒤 1.0.0 을 진행합니다.\n"
        f"  아직이라면   : 이 파일의 MIGRATION_WINDOW 를 늘리고 **그 근거를\n"
        f"                 #30 에 적으세요.** 근거 없이 늘리면 이 검사가\n"
        f"                 형식이 됩니다."
    )


def test_gate_is_not_already_expired_by_accident() -> None:
    """게이트가 **과거로 설정되는 것**을 막습니다.

    누가 `MIGRATION_WINDOW` 를 0 으로 만들거나 게시일을 잘못 적으면 위
    테스트가 즉시 실패해 CI 를 막습니다. 그건 감시가 아니라 사고입니다.
    """
    assert REVISIT_ON > PUBLISHED_0_1_0, "게이트가 게시일보다 앞섭니다"
    assert MIGRATION_WINDOW.days >= 30, (
        f"마이그레이션 기간이 {MIGRATION_WINDOW.days}일입니다. 30일 미만이면 폴백을 예고한 의미가 없습니다."
    )
