# 2026-11-15 - §5.5 판정 할일을 이슈로

## 사용자 요청

> read `docs/reports/2026-08-27_ARCHITECTURE_COMPARISON_OPEN_TRADING_API_KR.md`
> `../open-trading-api` 폴더 참고 가능함.
> ### 5.5 판정 관련 할일들을 이슈로 작성하기

## 범위

- §5.5 의 할일만 이슈로 연다.
- 이미 닫힌 판정은 다시 열지 않는다.
- 동결 보고서는 고치지 않는다.
- `../open-trading-api` 는 이 절의 판정(의존 방향)에 스펙 소스로 쓰이지 않는다.

## 계획

1. §5.5 Tier 1–3 을 닫힌 이슈·현재 코드와 대조한다.
2. 남은 일만 GitHub 이슈로 연다.
3. `next-up` 은 아직 코드에 없는 필수 주석 한 건만.

## 결과

- #175 순환 우회 지연 import 사유 주석 (`next-up`)
- #176 approval key 조달을 client 밖으로
- (a)(f) 는 #17 · #18, (c) 문서와 import-linter 는 #20 · #50 · #146 · #171, (e) 는 #63 에서 동결. 새 이슈 없음.
