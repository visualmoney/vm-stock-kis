# 2026-11-25 - 잔고 다이어그램 분리

## 무엇을 옮겼나

상속 Mermaid 두 장을 `docs/architecture/BALANCE_CLASS_DIAGRAM.md` 로 옮겼다. `BALANCE_CLASSES.md` 에는 반환 표와 모의투자 `stocks` 교체만 남겼다.

## 다른 모듈 클래스 다이어그램이 필요한가

필요 없다. 전체 그림은 `ARCHITECTURE.md` 의 허브-스포크와 T1 판정이다. 호출자는 `KisQuote` · `KisOrder` · `KisChart` 같은 **하나의 이름**을 받고, 국내·해외 구체 클래스는 모듈 안 선언에 있다.

모듈마다 상속 그림을 두면 구현을 바꿀 때마다 그림이 어긋난다. 클래스 헤더만 보면 안 보이는 라우팅만 표로 남길 가치가 있다. 잔고의 모의투자 종목 교체가 그 예다. 일별체결·미체결·손익의 `Integration*` 조립도 같은 종류지만, 지금은 함수 docstring 과 코드로 충분하고 다이어그램 세트를 늘리지 않는다.
