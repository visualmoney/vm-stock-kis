# 2026-11-15 - VmKis as VmStockHub 별칭 검토

## 사용자 요청
> 예제의 `kis = VmKis` 대신 `from vmkis import VmKis as VmStockHub`.
> 허브-스포크를 반영한 명칭. 증권사가 VmToss 로 바뀌어도 같은 `as VmStockHub`.
> 이 내용에 대하여 기술적 검토 및 아키텍처적인 검토.

## 분석
- 구현 없음. 공개 API·예제·검사기·허브-스포크 정본을 대조해 채팅에 결론.

## 결과
채팅 검토. 권고: 라이브러리 `__all__` 에 올리지 말 것. 예제 별칭은 선택.
