# 2026-11-15 - kis.py → hub.py, VmKis → VmHub 검토

## 사용자 요청
> src/vmkis/kis.py 를 hub.py 로, VmKis 를 VmHub 로. 이유는 src/vmtoss/hub.py 처럼
> 다른 증권사에서 동일 클래스명을 써서 재사용성을 높이기 위한 전략적 명칭.
> 검토 후 승인이 되면 진행.

## 범위
구현 없음. 공개 API · SemVer · 허브-스포크 불변식 · 직전 D안(`hub` 변수) ·
`#33`/`#34` 별칭 제거 · `#170` 의 `vmkis.hub` 금지 검사를 대조한다.

## 결과
채팅 검토. 권고: 1.x 에서 하지 말 것. 재사용은 이름이 아니라 Protocol.
