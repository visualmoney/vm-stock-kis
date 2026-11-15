# 2026-11-15 - 머지된 로컬 브랜치 삭제 규칙

## 작업 내용

이슈 #172. 원격 헤드는 `#125` 가 지킨다. 로컬은 스쿼시 머지 뒤
`--merged` 에 안 잡히므로 `AGENTS.md` 작업 종료 절에 `git branch -D` 를
적었다. `AGENT_WORKFLOW_RULES` · `CONTRIBUTING` · session-close 가 같은
말을 가리킨다.

`leftover_merged_heads` 를 로컬 이름 집합에도 쓴다. `wip-unique` 는
머지된 PR 헤드가 아니면 남긴다.

## 함정

`git branch -d` 는 스쿼시 토픽을 거절한다. 그래서 `-D` 다. `main` 은
KEEP.

## 회귀

`AGENTS.md` 에서 `git branch -D` 를 `-d` 로 바꾸면
`test_agents_require_deleting_merged_local_branches` 가 실패하는 것을 확인했다.

## 다음 할 일

이 PR 머지 직후 로컬 토픽 브랜치를 `-D` 한다.
