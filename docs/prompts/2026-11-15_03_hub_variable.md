# 2026-11-15 - 인스턴스 변수 hub (D안)

## 사용자 요청
> D안으로 선택함.

## 분석
- 클래스 이름 `VmKis` 유지. `__all__` 에 `VmStockHub` 없음.
- 사용자 코드의 허브 인스턴스만 `kis` → `hub`. 스포크는 `hub.stock()` / `hub.account()`.
- 범위: `examples/` 전부 + 같은 생성 그림을 가르치는 살아 있는 문서.
- 테스트 픽스처·`src/` 내부는 그대로.

## 계획
1. examples 의 `create_client` / `VmKis` 인스턴스 변수 개명
2. USER_GUIDE, README, FAQ, SIMPLEKIS, ARCHITECTURE 사용자 상자
3. 검사기가 옛 `kis = create_client` 를 강제하지 않는지 확인
