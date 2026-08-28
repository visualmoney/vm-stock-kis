# CLAUDE.md - AI 개발 도우미 가이드

**작성일**: 2025년 12월 18일
**대상**: Claude AI 및 개발자
**목적**: VM-Stock-KIS 프로젝트의 AI 기반 개발 가이드

---

## 문서 체계

VM-Stock-KIS 프로젝트는 다음과 같은 문서 구조를 따릅니다:

> 아래는 **실제 존재하는 파일**만 적습니다. 없는 문서를 참조하면 그것을 믿고
> 찾다가 시간을 버립니다. 새 문서를 만들면 여기에도 추가하세요.

```text
docs/
├── guidelines/          # 규칙 및 가이드라인
│   ├── API_STABILITY_POLICY.md    # 버전·호환성 정책
│   ├── PYPI_RELEASE.md            # 배포 절차
│   ├── DEVELOPER_SETUP.md         # 개발 환경
│   ├── GUIDELINES_001_TEST_WRITING.md
│   └── ... (docs/guidelines/ 실제 목록 참고)
│
├── dev_logs/            # 개발 일지 (날짜별)
│   ├── 2025-12-18_phase1_week1_complete.md
│   └── YYYY-MM-DD_nn_*.md    # nn = 그날의 작성 순번
│
├── reports/             # 보고서 및 분석
│   ├── ARCHITECTURE_REPORT_V3_KR.md
│   ├── DEVELOPMENT_REPORT_*.md
│   └── archive/
│
├── prompts/             # 프롬프트 기록
│   ├── 2025-12-18_public_api_refactor.md
│   └── YYYY-MM-DD_nn_*.md    # nn = 그날의 작성 순번
│
└── user/                # 사용자 문서
    ├── QUICKSTART.md
    └── TUTORIALS.md
```

---

## AI 개발 프로세스

### 1. 프롬프트 수신 시

**단계**:

1. 프롬프트를 `docs/prompts/YYYY-MM-DD_nn_주제.md` 형식으로 저장
   (`nn` 은 그날의 작성 순번 — [파일명 규칙](#파일명-규칙) 참고)
2. 관련된 기존 문서 확인 (reports, guidelines)
3. 작업 범위 파악 및 todo list 생성

**예시**:

```markdown
# 2025-12-18_public_api_refactor.md

## 사용자 요청
공개 API를 정리하고 public_types.py를 생성하라

## 분석
- 현재 공개 API: 154개
- 목표: 20개 이하
- 소요 시간: 8시간
```

### 2. 작업 분류

프롬프트를 다음과 같이 분류:

| 카테고리 | 저장 위치 | 예시 |
|---------|----------|------|
| **규칙/가이드** | `docs/guidelines/` | 코딩 표준, Git 워크플로우 |
| **개발 일지** | `docs/dev_logs/` | Phase 1 완료, 버그 수정 |
| **보고서** | `docs/reports/` | 아키텍처 분석, 성능 보고서 |
| **프롬프트** | `docs/prompts/` | 모든 사용자 요청 원본 |

### 3. 작업 진행

**체크리스트**:

- [ ] 프롬프트 문서 작성
- [ ] 관련 가이드라인 확인
- [ ] 작업 수행
- [ ] 테스트 실행
- [ ] 개발 일지 작성
- [ ] 필요 시 보고서 작성
- [ ] Git commit & push

### 4. 작업 완료 시

**필수 작업**:

1. **개발 일지 작성** (`docs/dev_logs/YYYY-MM-DD_nn_주제.md`)
   - 작업 내용
   - 변경 파일 목록
   - 테스트 결과
   - 다음 할 일

2. **보고서 갱신** (Phase 완료 시)
   - 진행 상황 표시 (✅)
   - 다음 단계 표시
   - KPI 업데이트

3. **To-Do List 작성**
   - 미완료 작업
   - 다음 우선순위
   - 블로커 이슈

---

## 문서 작성 규칙

### 파일명 규칙

```text
YYYY-MM-DD_nn_주제.md
```

`nn` 은 **그날의 작성 순번**(`01`, `02`, …)입니다. 두 자리로 고정합니다.

```text
2026-08-28_01_issue2_finalize.md
2026-08-28_02_issue25_migration_review.md
2026-08-28_03_issue27_core_metadata_pin.md
```

#### 왜 순번이 필요한가

파일 목록은 **알파벳순**으로 정렬됩니다. 하루에 여러 건을 쓰면 날짜만으로는
작성 순서를 알 수 없고, 목록이 실제 진행 순서와 무관하게 섞입니다.

실제로 2026-08-28 에 10건을 쓴 결과가 이랬습니다.

```text
issue15_...  issue17_...  issue18_...  issue19_20_...  issue23_...
issue25_...  issue27_...  issue2_...   issue43_...     label_...
```

`issue2_` 가 `issue27` 보다 **뒤에** 옵니다 — `_`(0x5F)가 `7`(0x37)보다 크기
때문입니다. 순번을 앞에 두면 이런 일이 없습니다.

> **기존 파일은 그대로 둡니다.** 이름을 바꾸면 다른 문서의 링크가 깨지고,
> 기록물을 사후에 손대지 않는다는 원칙과도 어긋납니다.
> **2026-08-28 이후 새로 쓰는 것부터** 적용합니다.

같은 규칙을 `docs/prompts/` 에도 적용합니다.

### Markdown 템플릿

#### 프롬프트 문서

```markdown
# [날짜] - [주제]

## 사용자 요청
[원본 프롬프트]

## 분석
- 작업 범위
- 예상 시간
- 영향 받는 모듈

## 계획
1. ...
2. ...

## 결과
[완료 후 작성]
```

#### 개발 일지

```markdown
# [날짜] - [주제] 개발 일지

## 작업 내용
...

## 변경 파일
- `path/to/file.py` - 설명

## 테스트 결과
- 통과: X개
- 실패: Y개
- 커버리지: Z%

## 다음 할 일
- [ ] ...
```

#### 보고서

```markdown
# [주제] 보고서

**작성일**: YYYY-MM-DD
**작성자**: Claude/개발자명
**버전**: vX.Y

## 요약
...

## 상세 내용
...

## 결론 및 권장사항
...
```

---

## Phase별 문서 요구사항

### Phase 1 (긴급 개선)

- **필수**: 개발 일지 (주 1회)
- **선택**: 프롬프트 문서
- **Phase 완료 시**: 완료 보고서 + To-Do List

### Phase 2 (품질 향상)

- **필수**: 개발 일지 + 가이드라인 문서
- **선택**: 품질 분석 보고서

### Phase 3 (커뮤니티)

- **필수**: 튜토리얼 작성
- **선택**: 커뮤니티 피드백 리포트

---

## AI 작업 체크리스트

### 매 프롬프트마다

- [ ] 프롬프트 문서 작성 (`docs/prompts/YYYY-MM-DD_nn_주제.md`)
- [ ] 관련 가이드라인 확인
- [ ] 작업 분류 (규칙/일지/보고서)

### 작업 완료 시

- [ ] 개발 일지 작성 (`docs/dev_logs/YYYY-MM-DD_nn_주제.md`)
- [ ] 테스트 실행 및 결과 기록
- [ ] Git commit (적절한 메시지)
- [ ] 관련 보고서 갱신 (체크박스 표시)

### Phase 완료 시

- [ ] 완료 보고서 작성 (`docs/reports/`)
- [ ] To-Do List 작성 (다음 Phase용)
- [ ] 아키텍처 문서 갱신
- [ ] CHANGELOG 업데이트

---

## 참고 자료

- [docs/INDEX.md](./docs/INDEX.md) - 문서 인덱스 (여기서 시작하세요)
- [docs/architecture/ARCHITECTURE.md](./docs/architecture/ARCHITECTURE.md) - 구조와 **지켜야 할 불변식**
- [QUICKSTART.md](./QUICKSTART.md) - 빠른 시작 가이드
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 기여 가이드

---

**마지막 업데이트**: 2026-08-28
