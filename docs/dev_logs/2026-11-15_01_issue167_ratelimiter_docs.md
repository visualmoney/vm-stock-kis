# 2026-11-15 - #167 RateLimiter 문서 드리프트 개발 일지

## 작업 내용

시세 흐름 그림이 `RateLimiter.wait()` 를 적었고, 그 메서드는 없다.
비교 보고서 7.4 오른쪽 칸이 맞다: `request()` 전 항상 `acquire()`.

회귀 테스트를 문서 고치기 **전에** 돌렸다. 살아 있는 문서 검사가 실패했다.

```
docs/architecture/ARCHITECTURE.md — RateLimiter.wait
docs/developer/DEVELOPER_GUIDE.md — rate_limiter.wait
docs/developer/DEVELOPER_GUIDE.md — rate_limiter.on_success
docs/developer/DEVELOPER_GUIDE.md — rate_limiter.on_error
```

그 다음 두 문서를 `acquire()` 로 맞췄다. 동결 비교 보고서는 손대지 않았다.

설명 문장에 `RateLimiter.wait()` 를 다시 적으면 검사가 또 깨진다. "없다"고
쓰려다 금칙어를 넣은 셈이다. `wait` 만 적었다.

## 변경 파일

- `docs/architecture/ARCHITECTURE.md`
- `docs/developer/DEVELOPER_GUIDE.md`
- `tests/unit/test_rate_limiter_docs.py`
- `src/vmkis/kis.py` — `request()` 문서화 (동작 변경 없음)
- `src/vmkis/utils/rate_limit.py` — `acquire()` 문서화
- `tests/unit/test_kis.py` — 단건 `request()` 가 `acquire()` 를 타는지

## 테스트 결과

고치기 전: `test_living_docs_do_not_teach_rate_limiter_wait` 실패 (위 4줄).
고친 뒤: 같은 파일 재실행. `test_checker_fails_on_the_old_wait_sketch` 는
결함 조각을 직접 먹인다.

## 다음 할 일

커밋·PR 은 요청 시. PR 본문에 `Closes #167`.
