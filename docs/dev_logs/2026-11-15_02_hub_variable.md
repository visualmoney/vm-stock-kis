# 2026-11-15 - 인스턴스 변수 hub (D안) 개발 일지

## 작업 내용

클래스 `VmKis` 는 공개 이름 그대로다. 사용자 코드의 허브 인스턴스만 `kis` 에서
`hub` 로 바꿨다. `stock = hub.stock(...)` 이 스포크다.

`as VmStockHub` 는 넣지 않았다. `__all__` 도 그대로다.

이 브랜치의 예제는 `01_basic` 만 있다. `create_client` 라 클래스 별칭이 들어갈 자리가 없었다.

마이그레이션 안내의 **python-kis 2.x** 쪽은 `kis = PyKis(...)` 로 되돌렸다.
옛 라이브러리 변수까지 hub 로 바꾸면 이전이 거짓이 된다.

`kis.py` 파일명은 `(?<!...)kis(?!\.py)` 로 건드리지 않았다.

## 변경 파일

- `examples/01_basic/*.py`, `tutorial_basic.ipynb`, README
- 살아 있는 사용자·개발 문서 (USER_GUIDE, FAQ, README, QUICKSTART, ARCHITECTURE 사용자 상자 등)
- `tests/unit/test_examples_behavior.py` — `hub = create_client` 강제

## 테스트 결과

관련 단위 테스트 192건 통과. 예제 변수 검사는 옛 `kis = create_client` 가 있으면 실패한다.
일회용 치환 스크립트는 커밋하지 않고 지운다.

## 다음 할 일

커밋·PR 은 요청 시.
