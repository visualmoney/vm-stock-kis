# CLAUDE.md - AI 개발 도우미 가이드

**작성일**: 2025년 12월 18일
**대상**: Claude AI 및 개발자
**목적**: VM-Stock-KIS 프로젝트의 AI 기반 개발 가이드

---

## 문서 체계

VM-Stock-KIS 프로젝트는 다음과 같은 문서 구조를 따릅니다:

```
docs/
├── guidelines/          # 규칙 및 가이드라인
│   ├── CODING_STANDARDS.md
│   ├── GIT_WORKFLOW.md
│   └── DOCUMENTATION_RULES.md
│
├── dev_logs/            # 개발 일지 (날짜별)
│   ├── 2025-12-18_phase1_week1_complete.md
│   └── YYYY-MM-DD_*.md
│
├── reports/             # 보고서 및 분석
│   ├── ARCHITECTURE_REPORT_V3_KR.md
│   ├── DEVELOPMENT_REPORT_*.md
│   └── archive/
│
├── prompts/             # 프롬프트 기록
│   ├── 2025-12-18_public_api_refactor.md
│   └── YYYY-MM-DD_*.md
│
└── user/                # 사용자 문서
    ├── QUICKSTART.md
    └── TUTORIALS.md
```

---

## AI 개발 프로세스

### 1. 프롬프트 수신 시

**단계**:
1. 프롬프트를 `docs/prompts/YYYY-MM-DD_주제.md` 형식으로 저장
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
1. **개발 일지 작성** (`docs/dev_logs/YYYY-MM-DD_주제.md`)
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

```
날짜_주제_타입.md

예시:
- 2025-12-18_public_api_refactor_prompt.md
- 2025-12-18_phase1_week1_complete_devlog.md
- 2025-12-18_testing_improvements_report.md
```

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
- [ ] 프롬프트 문서 작성 (`docs/prompts/`)
- [ ] 관련 가이드라인 확인
- [ ] 작업 분류 (규칙/일지/보고서)

### 작업 완료 시
- [ ] 개발 일지 작성 (`docs/dev_logs/`)
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

- [ARCHITECTURE_REPORT_V3_KR.md](./reports/ARCHITECTURE_REPORT_V3_KR.md) - 전체 로드맵
- [QUICKSTART.md](../QUICKSTART.md) - 빠른 시작 가이드
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 기여 가이드 (예정)

---

**마지막 업데이트**: 2025년 12월 18일
**다음 검토**: Phase 2 시작 시
