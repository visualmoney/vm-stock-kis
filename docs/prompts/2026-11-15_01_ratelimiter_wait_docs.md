# 2026-11-15 - RateLimiter.wait() 문서 드리프트

## 사용자 요청
> docs\architecture\ARCHITECTURE.md : 536 관련 에러 , RateLimiter.wait() 관련 API 없음.
> 비교 보고서 ### 7.4에서 일단 단건 호출에는 미적용 | request() 전 항상 acquire() 임.
> 이슈로 등록하고 수정할 부분 검토하여 계획을 작성하고, 승인 후 구현하기

## 분석
- 코드 정본: `RateLimiter.acquire()` (`src/vmkis/utils/rate_limit.py:53`). `wait`/`on_success`/`on_error` 없음.
- `VmKis.request()` 재시도 루프마다 `acquire()` (`kis.py:654`). 단건 REST도 포함.
- 비교 보고서 7.4 오른쪽 칸은 그 사실을 이미 적음. 왼쪽 칸(open-trading-api)만 단건 미적용.
- 살아 있는 문서가 옛 API 이름을 그림/스케치로 적음. 보고서는 동결.

## 계획
이슈 등록 → 채팅에 수정 범위와 회귀 검사 계획 → **승인 후** 구현.

## 결과
승인 후 구현. 이슈 #167. `ARCHITECTURE.md` / `DEVELOPER_GUIDE.md` 를 `acquire()` 에
맞추고 `tests/unit/test_rate_limiter_docs.py` 로 옛 스케치를 막음.
