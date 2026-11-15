# 2026-11-15 - 머지된 로컬 브랜치 삭제 규칙

## 사용자 요청
> commit, pr, merge, 머지된 로컬 브랜치를 삭제하는 규칙 추가 하고 작업하기.

## 범위
- #171 살아 있는 문서 계층 서술 수정과 함께 커밋·PR·머지.
- 원격 헤드 삭제는 이미 `delete_branch_on_merge` + `#125` 검사.
- 로컬 잔여(`: gone]`, 스쿼시로 `--merged` 에 안 잡힘)를 지우는 규칙을
  `AGENTS.md` 에 둔다. always-on `.mdc` 로 문장을 복제하지 않는다.

## 계획
1. 이슈 개설
2. `AGENTS.md` · `AGENT_WORKFLOW_RULES` · `CONTRIBUTING` · session-close
3. `leftover_merged_heads` 를 로컬 이름에도 쓰는 단위 테스트
4. #171 변경과 한 PR (`Closes #171` · `Closes #172`)
