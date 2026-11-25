# 2026-11-25 - 잔고 클래스 다이어그램

## 무엇을 만들었나

`docs/architecture/BALANCE_CLASSES.md`. `balance.py` 의 프로토콜·베이스 상속과, 국내·해외·통합 구현이 종목·예수금을 어떻게 붙이는지.

## 함정

기존 다이어그램은 없다. `docs/diagrams/src/` 에는 `api_size_comparison.puml` 만 있고, 이것은 옛 API 개수 비교다. 클래스 상속 원본이 아니다.

`foreign_balance` 의 반환 타입은 `KisForeignPresentBalance` 다. 모의투자일 때만 `stocks` 를 `_foreign_balance()` (`KisForeignBalance` / `KisForeignBalanceStock`) 로 갈아 끼운다. 예수금 클래스는 바뀌지 않는다. 다이어그램을 상속 한 장으로 그리면 이 교체가 사라진다.

`KisIntegrationBalance` 는 `KisDynamic` 이 아니다. `country is None` 일 때 국내 잔고와 `foreign_balance` 를 생성자에서 이어 붙이고, 종목의 `balance` 포인터를 통합 잔고로 다시 쓴다.

`Checkable[KisBalanceStock]` 은 종목 세 클래스에만 있다. 잔고·예수금 프로토콜은 그 검사가 없다.
