# 2026-11-15 - 살아 있는 문서에서 계층·하향 서술 제거

## 사용자 요청
> 계층 아키텍처가 아닌 허브 스포크 구조임. 하향 계층이 아닙니다.
> 처음에는 layered 아키텍처를 검토하였으나, 계층 아키텍처가 아닌 것이 분명하므로,
> 활성된 문서 폴더에서 (계층 아키텍처, 하향 아키텍처 설명 오류를 수정하는
> 문서화 작업을 이슈로 생성하여 작업하기)

첨부: `docs/reports/2026-08-27_ARCHITECTURE_COMPARISON_OPEN_TRADING_API_KR.md`,
`docs/architecture/ARCHITECTURE.md`

## 범위
- 이슈 개설 후 살아 있는 문서만 고친다.
- 동결 `docs/reports/` · `dev_logs/` · `prompts/` · `archive/` 는 당시 서술로 둔다.
- 비교 보고서는 layered 렌즈로 **시작한 기록**이지 현재 정본이 아니다.

## 계획
1. GitHub 이슈. 닫는 조건: 살아 있는 문서가 허브-스포크만 가르친다.
2. `ARCHITECTURE.md` 의 "하위 계층" · "느슨한 상하 순서" 등 층 언어를 그룹·스포크로.
3. `DEVELOPER_GUIDE` · `CONTRIBUTING` · `REGIONAL_GUIDES` 의 같은 오류.
4. `test_docs_one_picture` 가 그 문구를 다시 못 들이게.
