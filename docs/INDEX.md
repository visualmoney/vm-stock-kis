# 문서 인덱스 및 저장소 구조

**작성일**: 2025-12-17
**최종 업데이트**: 2025-12-20
**목적**: 프로젝트 문서 및 리소스 중앙 집중식 관리
**버전**: 1.1 (Phase 4 완료 반영)

---

## 📁 문서 저장 구조

```text
docs/
├── README.md                          # 프로젝트 소개
├── architecture/                      # 아키텍처 문서
│   └── ARCHITECTURE.md               # 시스템 아키텍처 설명
├── developer/                         # 개발자 가이드
│   └── DEVELOPER_GUIDE.md            # 개발 가이드 및 설정
├── user/                             # 사용자 문서
│   ├── ko/                            # 한국어 문서
│   │   ├── README.md                  # 한국어 프로젝트 개요 ✅
│   │   ├── QUICKSTART.md              # 한국어 빠른 시작 ✅
│   │   └── FAQ.md                     # 한국어 FAQ ✅
│   └── en/                            # 영어 문서
│       ├── README.md                  # English Project Overview ✅
│       ├── QUICKSTART.md              # English Quick Start ✅
│       └── FAQ.md                     # English FAQ ✅
├── guidelines/                        # 📌 개발 규칙 및 가이드
│   ├── GUIDELINES_001_TEST_WRITING.md   # 테스트 코드 작성 표준
│   ├── MULTILINGUAL_SUPPORT.md          # 다국어 지원 정책 ✅
│   ├── REGIONAL_GUIDES.md               # 지역별 설정 가이드 ✅
│   ├── API_STABILITY_POLICY.md          # API 안정성 정책 ✅
│   ├── GITHUB_DISCUSSIONS_SETUP.md      # GitHub Discussions 설정 ✅
│   ├── VIDEO_SCRIPT.md                  # 튜토리얼 영상 스크립트 ✅
│   └── README.md                        # 가이드라인 목록
├── prompts/                           # 프롬프트 기록
│   ├── PROMPT_001_TEST_COVERAGE_AND_TESTS.md  # Phase 1 테스트 개선 ✅
│   ├── 2025-12-20_phase4_week1_prompt.md      # Phase 4 Week 1 글로벌 확장 ✅
│   ├── 2025-12-20_phase4_week3_script_discussions_prompt.md  # Phase 4 Week 3 ✅
│   └── README.md                       #개발 일지
│   ├── 2025-12-18_phase1_week1_complete.md    # Phase 1 완료 ✅
│   ├── 2025-12-20_phase4_week1_global_docs_devlog.md  # Phase 4 Week 1 ✅
│   ├── 2025-12-20_phase4_week3_devlog.md      # Phase 4 Week 3 ✅ 개발 일지
│   ├── DEV_LOG_2025_12_*.md           # (주간/월간 일지)
│   └── README.md                       # 일지 인덱스
├── reports/                 3_KR.md   # 최신 아키텍처 분석 보고서 ✅
│   ├── PHASE4_WEEK1_COMPLETION_REPORT.md    # Phase 4 Week 1 완료 ✅
│   ├── PHASE4_WEEK3_COMPLETION_REPORT.md    # Phase 4 Week 3 완료 ✅
│   ├── PHASE2_WEEK3-4_STATUS.md       # Phase 2 Week 3-4 현황 ✅
│   ├── FINAL_REPORT.md                # 최종 완료 보고서
│   ├── TASK_PROGRESS.md               # 작업 진행 현황
│   ├── CODE_REVIEW.md                 # 코드 리뷰 결과
│   ├── TEST_COVERAGE_REPORT.md        # 테스트 커버리지 보고서
│   ├── test_reports/                  # 테스트 보고서
│   │   ├── TEST_REPORT_2025_12_17.md  # 2025-12-17 테스트 보고서 ✅
│   │   ├── TEST_REPORT_2025_12_17.md  # 2025-12-17 테스트 보고서
│   │   └── TEST_REPORT_2025_12_*.md   # (주간 보고서)
│   ├── README.md                       # 보고서 목록
│   └── coverage/                       # HTML 커버리지 리포트
└── examples/                          # 📌 추후 추가: 예제 코드
    ├── 01_basic/                      # 기본 예제
    ├── 02_intermediate/               # 중급 예제
    └── 03_advanced/                   # 고급 예제
```

---
완료 |
| [MULTILINGUAL_SUPPORT.md](c:\Python\github.com\python-kis\docs\guidelines\MULTILINGUAL_SUPPORT.md) | 다국어 지원 정책 및 프로세스 | 개발팀 | ✅ 완료 |
| [REGIONAL_GUIDES.md](c:\Python\github.com\python-kis\docs\guidelines\REGIONAL_GUIDES.md) | 한국/글로벌 환경 설정 가이드 | 개발자 | ✅ 완료 |
| [API_STABILITY_POLICY.md](c:\Python\github.com\python-kis\docs\guidelines\API_STABILITY_POLICY.md) | API 버전 정책 및 마이그레이션 | 사용자/개발자 | ✅ 완료 |
| [GITHUB_DISCUSSIONS_SETUP.md](c:\Python\github.com\python-kis\docs\guidelines\GITHUB_DISCUSSIONS_SETUP.md) | GitHub Discussions 설정 가이드 | 관리자 | ✅ 완료 |
| [VIDEO_SCRIPT.md](c:\Python\github.com\python-kis\docs\guidelines\VIDEO_SCRIPT.md) | 튜토리얼 영상 스크립트 (5분) | 마케팅팀 | ✅ 완료

### 규칙 & 가이드라인 (Guidelines)

| 문서 | 목적 | 대상 | 상태 |
|------|------|------|------|
| [GUIDELINES_001_TEST_WRITING.md](c:\Python\github.com\python-kis\docs\guidelines\GUIDELINES_001_TEST_WRITING.md) | 테스트 코드 작성 표준 | 테스터/개발자 | ✅ 작성됨 |
| GUIDELINES_002_*.md | (추후 작성) | - | ⏳ 계획 중 |

### 프롬프트 기록 (Prompts)| 874개 테스트, 94% 커버리지 | ✅ 완료 |

| [2025-12-20_phase4_week1_prompt.md](c:\Python\github.com\python-kis\docs\prompts\2025-12-20_phase4_week1_prompt.md) | 글로벌 문서 및 다국어 확장 | 3,500줄 문서화 | ✅ 완료 |
| [2025-12-20_phase4_week3_script_discussions_prompt.md](c:\Python\github.com\python-kis\docs\prompts\2025-12-20_phase4_week3_script_discussions_prompt.md) | 영상 스크립트 & Discussions | 1,390줄 문서화 | ✅ 완료

| 문서 | 주제 | 결과 | 상태 |
|------|------|------|------|
| [PROMPT_001_TEST_COVERAGE_AND_TESTS.md](c:\Python\github.com\python-kis\docs\prompts\PROMPT_001_TEST_COVERAGE_AND_TESTS.md) | 테스트 커버리지 개선 + test_daily_chart/test_info 구현 | 12개 테스트 추가 | ✅ 완료 |
| PROMPT_002_*.md | (추후 기록) | - | ⏳ 계획 중 |

### 개발 일지 (Development Logs)

| 문서 | 기간 | 작업 내용 | 상태 |
|--2025-12-18_phase1_week1_complete.md](c:\Python\github.com\python-kis\docs\dev_logs\2025-12-18_phase1_week1_complete.md) | Phase 1 | API 리팩토링, 문서화 | ✅ 완료 |
| [2025-12-20_phase4_week1_global_docs_devlog.md](c:\Python\github.com\python-kis\docs\dev_logs\2025-12-20_phase4_week1_global_docs_devlog.md) | Phase 4 Week 1 | 글로벌 문서 (3,500줄) | ✅ 완료 |
| [2025-12-20_phase4_week3_devlog.md](c:\Python\github.com\python-kis\docs\dev_logs\2025-12-20_phase4_week3_devlog.md) | Phase 4 Week 3 | 영상 스크립트 & Discussions | ✅ 완료python-kis\docs\dev_logs\DEV_LOG_2025_12_17.md) | 2025-12-10 ~ 12-17 | 테스트 개선 & 문서화 | ✅ 완료 |
| DEV_LOG_2025_12_*.md | (매주 업데이트) | - | ⏳ 계획 중 |

### 테스트 보고서 (Test Reports)

| 문서 | 일자 | 테스트 결과 | 커버리지 | 상태 |
|------|------|-----------|---------|------|74 pass, 19 skip | 89.7% | ✅ 완료 |
| [PHASE2_WEEK3-4_STATUS.md](c:\Python\github.com\python-kis\docs\reports\PHASE2_WEEK3-4_STATUS.md) | 2025-12-20 | CI/CD 완성, 통합 테스트 추가 | 89.7% | ✅ 완료 |
| [PHASE4_WEEK1_COMPLETION_REPORT.md](c:\Python\github.com\python-kis\docs\reports\PHASE4_WEEK1_COMPLETION_REPORT.md) | 2025-12-20 | 영문 문서 3개 + 가이드라인 3개 | - | ✅ 완료 |
| [PHASE4_WEEK3_COMPLETION_REPORT.md](c:\Python\github.com\python-kis\docs\reports\PHASE4_WEEK3_COMPLETION_REPORT.md) | 2025-12-20 | 영상 스크립트 + Discussions | - | ✅ 완료on-kis\docs\reports\test_reports\TEST_REPORT_2025_12_17.md) | 2025-12-17 | 840 pass, 5 skip | 94% (unit) | ✅ 완료 |
| TEST_REPORT_2025_12_*.md | (매주 업데이트) | - | - | ⏳ 계획 중 |

### 종합 보고서 (Main Reports)

3_KR.md](c:\Python\github.com\python-kis\docs\reports\ARCHITECTURE_REPORT_V3_KR.md) | 종합 아키텍처 분석 | 2025-12-20 | ✅ 최신 |
| [PHASE4_WEEK1_COMPLETION_REPORT.md](c:\Python\github.com\python-kis\docs\reports\PHASE4_WEEK1_COMPLETION_REPORT.md) | Phase 4 Week 1 완료 현황 | 2025-12-20 | ✅ 완료 |
| [PHASE4_WEEK3_COMPLETION_REPORT.md](c:\Python\github.com\python-kis\docs\reports\PHASE4_WEEK3_COMPLETION_REPORT.md) | Phase 4 Week 3 완료 현황 | 2025-12-20 | ✅ 완료 |
| [PHASE2_WEEK3-4_STATUS.md](c:\Python\github.com\python-kis\docs\reports\PHASE2_WEEK3-4_STATUS.md) | Phase 2 Week 3-4 완료 현황 | 2025-12-20 | ✅ 완료
| [ARCHITECTURE_REPORT_V2_KR.md](c:\Python\github.com\python-kis\docs\reports\ARCHITECTURE_REPORT_V2_KR.md) | 종합 아키텍처 분석 | 2025-12-17 | ✅ 업데이트됨 |
| [TODO_LIST_2025_12_17.md](c:\Python\github.com\python-kis\docs\reports\TODO_LIST_2025_12_17.md) | 다음 할일 목록 | 2025-12-17 | ✅ 생성됨 |
| FINAL_REPORT.md | 최종 완료 보고서 | - | ⏳ 계획 중 |

---

## 🎯 문서별 활용 가이드

### 처음 시작하는 개발자

1. **[GUIDELINES_001_TEST_WRITING.md](c:\Python\github.com\python-kis\docs\guidelines\GUIDELINES_001_TEST_WRITING.md)** 읽기
   - 테스트 작성 표준 이해
   - Mock 패턴 학습
   - 마켓 코드 선택 기준 이해

2. **[PROMPT_001_TEST_COVERAGE_AND_TESTS.md](c:\Python\github.com\python-kis\docs\prompts\PROMPT_001_TEST_COVERAGE_AND_TESTS.md)** 참고
   - 실제 구현 예시 확인
   - KisObject.transform_() 패턴 학습

3. **[TEST_REPORT_2025_12_17.md](c:\Python\github.com\python-kis\docs\reports\test_reports\TEST_REPORT_2025_12_17.md)** 확인
   - 현재 테스트 현황 파악
   - 개선 필요 영역 식별

### 코드 리뷰어

1. **[ARCHITECTURE_REPORT_V2_KR.md](c:\Python\github.com\python-kis\docs\reports\ARCHITECTURE_REPORT_V2_KR.md)** 검토
   - 아키텍처 이해
   - 문제점 파악
   - 개선 방안 참고

2. **[DEV_LOG_2025_12_17.md](c:\Python\github.com\python-kis\docs\dev_logs\DEV_LOG_2025_12_17.md)** 확인
   - 최근 작업 내역
   - 주요 학습 사항
   - 지표 변화 추적

### 프로젝트 관리자

1. **[TODO_LIST_2025_12_17.md](c:\Python\github.com\python-kis\docs\reports\TODO_LIST_2025_12_17.md)** 참고
   - 다음 작업 계획
   - 우선순위 및 소요 시간
   - 일정표 확인

2. **[TEST_REPORT_2025_12_17.md](c:\Python\github.com\python-kis\docs\reports\test_reports\TEST_REPORT_2025_12_17.md)** 모니터링
   - 테스트 커버리지 추이
   - 품질 지표 확인
   - 위험 영역 식별 (2025-12-20)

### Phase 진행도

```text
Phase 1: ✅ 완료 (2025-12-18)
  └─ API 리팩토링, 테스트 강화

Phase 2: ✅ 완료 (2025-12-20)
  ├─ Week 1-2: 문서화 (4,260줄)
  └─ Week 3-4: CI/CD 파이프라인

Phase 3: ⏳ 준비 중
  └─ 커뮤니티 확장 (예제/튜토리얼)

Phase 4: ✅ 완료 (2025-12-20)
  ├─ Week 1: 글로벌 문서 (3,500줄)
  └─ Week 3: 영상 & Discussions (1,390줄)
```

### 테스트 현황

```text
테스트 통과:        874개 ✅
테스트 스킵:        19개 ⏳
커버리지 (단위):    89.7% 🟡 (목표 90% 근접)
통합 테스트:        31개 ✅
성능 테스트:        43개 ✅
```

### 문서화 현황

```text
총 신규 문서:       20+개 ✅
가이드라인:         6개 ✅
개발 일지:          3개 ✅
완료 보고서:        4개 ✅
영문 문서:          3개 ✅ (국제 확대)
```

### 아키텍처 평가

```text
설계:      4.5/5.0 🟢
코드 품질: 4.0/5.0 🟢
테스트:    4.3/5.0 🟢 (개선됨)
문서:      4.7/5.0 🟢 (대폭 개선)
글로벌화: 4.5/5.0 🟢 (새로 추가)
코드 품질: 4.0/5.0 🟢
테스트:    3.0/5.0 🟡
문서:      4.5/5.0 🟢
사용성:    3.5/5.0 🟡
```

---

## 🔄 문서 유지보수 일정

### 매일

- [ ] 테스트 실행 결과 확인
- [ ] 주요 변경 사항 기록

### 매주 (매 목요일)

- [ ] DEV_LOG 업데이트 (주간 일지)
- [ ] TEST_REPORT 생성 (최신 커버리지)
- [ ] 완료된 작업 TODO_LIST에서 체크
- [ ] 다음 주 우선순위 재설정

### 매월 (매 달 17일)

- [ ] ARCHITECTURE_REPORT 업데이트
- [ ] 분기 목표 검토
- [ ] 새로운 PROMPT 기록 (있으면)
- [ ] 새로운 GUIDELINE 추가 (필요시)

---

## 🚀 신규 문서 생성 체크리스트

### 새로운 프롬프트 기록 시

- [ ] PROMPT_00X_TITLE.md 생성
- [ ] 프롬프트 요청사항 기록
- [ ] 구현 세부사항 기술
- [ ] 최종 결과 요약
- [ ] 관련 파일 링크 추가

### 새로운 가이드라인 작성 시

- [ ] GUIDELINES_00X_TOPIC.md 생성
- [ ] 규칙 및 원칙 정의
- [ ] 코드 예시 포함
- [ ] 체크리스트 제공
- [ ] 주의사항 기술

### 주간 개발 일지 시

- [ ] DEV_LOG_YYYY_MM_DD.md 생성
- [ ] 완료된 작업 기술
- [ ] 진행 지표 기록
- [ ] 문제점 및 해결책 기록
- [ ] 다음 단계 계획

### 테스트 보고서 생성 시

- [ ] TEST_REPORT_YYYY_MM_DD.md 생성
- [ ] 테스트 결과 요약
- [ ] 모듈별 커버리지 분석
- [ ] 문제점 식별
- [ ] 개선 방안 제시

---

## 📖 문서 작성 원칙

### 1. 명확성 (Clarity)

```text
✅ 좋은 예
# 테스트 코드 작성 가이드라인
이 문서는 python-kis 프로젝트의 테스트 코드 작성 표준을 정의합니다.

❌ 나쁜 예
# 가이드
여러 규칙들을 정의합니다.
```

### 2. 구조화 (Structure)

```text
✅ 좋은 예
## 섹션 1: 기본 규칙
### 1.1 파일 구조
### 1.2 명명 규칙

❌ 나쁜 예
## 규칙들
파일, 명명, 기타 등 모두 섞여있음
```

### 3. 실행 가능성 (Actionable)

```text
✅ 좋은 예
## 체크리스트
- [ ] 테스트 명칭이 명확한가?
- [ ] Mock이 완전한가?
- [ ] 모든 테스트가 pass하는가?

❌ 나쁜 예
테스트를 잘 작성해야 합니다.
```

### 4. 예시 포함 (Examples)

```text
✅ 좋은 예
def test_feature():
    # 이렇게 하세요
    result = function()
    assert result == expected

❌ 나쁜 예
테스트를 작성하세요.
```

---

## 🎓 자주 묻는 질문 (FAQ)

### Q: 새로운 테스트를 작성했는데, 어디에 기록해야 하나요?

**A**: 다음과 같이 기록합니다:

1. 테스트 코드: `tests/unit/...` (또는 `tests/integration/...`)
2. 개발 일지: 주간 DEV_LOG에 기술
3. 테스트 보고서: 주간 TEST_REPORT에 반영
4. 문서화 필요시: GUIDELINES 업데이트

### Q: 기존 문서를 수정하려면?

**A**: 다음을 확인하세요:

1. 문서 버전 업데이트
2. 수정 일자 기록 ("최종 수정: YYYY-MM-DD")
3. 변경 내용 요약 ("주요 변경내용:" 섹션)
4. 관련 파일 검토 (링크 정확성)

### Q: 새로운 카테고리 폴더를 추가하려면?

**A**: 다음 구조를 따르세요:

```text
docs/new_category/
├── README.md (목록 및 설명)
├── DOCUMENT_001.md
├── DOCUMENT_002.md
└── ...
```

---

## 🔗 상호 참조 지도

```text
프롬프🎯 다음 단계

### Phase 3 (1월 예정)
- [ ] 커뮤니티 확장 (예제/튜토리얼 추가)
- [ ] 예제 Jupyter Notebook 작성
- [ ] 기여자 커뮤니티 구축
- [ ] 피드백 수집 및 반영

### 지속적 유지보수
- [ ] 주간 테스트 리포트 생성
- [ ] 월간 개발 일지 작성
- [ ] 분기별 아키텍처 리뷰
- [ ] 버전별 마이그레이션 가이드 업데이트

---

## 📞 연락처 및 기여

**관리자**: Claude AI (GitHub Copilot)
**마지막 업데이트**: 2025-12-20
**다음 리뷰**: 2025-12-27 (Phase 3 시작)

**기여하려면**:
1. 새 문서 작성 시 이 인덱스 업데이트
2. 깨진 링크 보고
3. 제안사항 또는 오류 기록

---

**상태**: 🟢 활성 (Phase 4 완료)
**버전**: 1.1
**라이센스**: MIT
**커밋**: Git commit 완료 (GitHub Discussions 템플릿)

---

## 📞 연락처 및 기여

**관리자**: AI Assistant (GitHub Copilot)
**마지막 업데이트**: 2025-12-17
**다음 리뷰**: 2025-12-24

**기여하려면**:
1. 새 문서 작성 시 이 인덱스 업데이트
2. 깨진 링크 보고
3. 제안사항 기록

---

**상태**: 🟢 활성
**버전**: 1.0
**라이센스**: MIT
