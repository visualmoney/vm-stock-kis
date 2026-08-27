# API 안정성 정책 (API_STABILITY_POLICY.md)

**작성일**: 2025-12-20
**대상**: 개발자, 사용자, 라이브러리 유지보수자
**버전**: v1.0

---

## 개요

VM-Stock-KIS의 **API 안정성 보장 정책**을 정의합니다. 사용자는 본 정책에 따라 버전 선택 및 업그레이드 계획을 수립할 수 있습니다.

---

## 1. API 안정성 레벨

### 1.1 레벨 정의

VM-Stock-KIS의 모든 공개 API는 다음 중 하나의 안정성 레벨을 갖습니다:

| 레벨 | 기호 | 설명 | 하위 호환성 | 지원 기간 |
|------|------|------|-----------|---------|
| **Stable** | 🟢 | 프로덕션 사용 완벽 안전 | 보장 | 12개월 |
| **Beta** | 🟡 | 곧 안정화될 기능 | 부분 | 6개월 |
| **Deprecated** | 🔴 | 곧 제거될 기능 | 그대로 | 6개월 |
| **Removed** | ⚫ | 이미 제거된 기능 | 불가 | N/A |

---

## 2. 버전별 안정성 보장

### 2.1 의미론적 버전 (Semantic Versioning)

```text
Major.Minor.Patch-PreRelease+Metadata
^      ^     ^
|      |     └─ Patch 증가: 버그 수정 (호환성 보장)
|      └─────── Minor 증가: 기능 추가 (호환성 보장)
└──────────────── Major 증가: Breaking Change (호환성 미보장)
```

### 2.2 Major 버전 정책

| Major 버전 | 라이프사이클 | 호환성 | 지원 기간 |
|-----------|-----------|-------|---------|
| v1.x | 🔴 레거시 (2025년 이전) | 부분 | 즉시 종료 |
| v2.x | 🟢 **현재** (2025-12 이후) | ✅ 완벽 | 12개월 |
| v3.x | 🟡 예정 (2026년 중반) | ⚠️ Breaking | 12개월 |

---

## 3. Breaking Change 정책

### 3.1 Breaking Change 정의

Breaking Change는 **기존 코드를 수정하지 않으면 작동하지 않게 하는 변경**입니다.

**예시**:

```python
# ✅ Breaking Change 아님 (Minor 버전)
# v2.0: kis.stock("005930").quote()
# v2.1: kis.stock("005930").quote(include_extended=True)  # 선택적 파라미터 추가

# ❌ Breaking Change (Major 버전)
# v2.x: kis.stock("005930").quote()
# v3.0: kis.stock("005930").get_quote()  # 메서드명 변경
```

### 3.2 Breaking Change 종류

| 종류 | 영향 | 예시 | 버전 |
|------|------|------|------|
| **메서드 삭제** | 매우 높음 | `quote()` 제거 | Major |
| **파라미터 제거** | 높음 | `price` 파라미터 제거 | Major |
| **반환 타입 변경** | 높음 | List → Dict 반환 | Major |
| **예외 처리 변경** | 중간 | 새로운 예외 발생 | Major |
| **기본값 변경** | 중간 | `timeout=30` → `timeout=60` | Minor* |
| **선택적 파라미터 추가** | 낮음 | `quote(include_extended=False)` | Minor |

*기본값 변경은 논쟁의 여지가 있으므로 v2.x 유지 예정

---

## 4. 마이그레이션 경로

### 4.1 Deprecation 프로세스

```text
준비 → 경고 → 마이그레이션 → 제거
Release: v2.x → v2.x~v2.9.x → v3.0 → (제거됨)
```

### 4.2 Deprecation 3단계

#### 1️⃣ 준비 (v2.x 특정 버전)

- ✅ 신규 기능 제공 (권장)
- 🔴 경고 없음 (기존 코드 정상 작동)

**예시**:

```python
# v2.1: 신규 기능 추가
from vmkis.types import KisObjectProtocol  # 신규 경로

# v2.0 스타일 계속 작동 (경고 없음)
from vmkis import KisObjectProtocol  # 기존 경로
```

#### 2️⃣ 경고 (v2.x~v2.9.x)

- ✅ 신규 기능 권장
- ⚠️ 경고 표시 (DeprecationWarning)
- ✅ 기존 코드 계속 작동

**예시**:

```python
# v2.2~v2.9: Deprecation 경고
from vmkis import KisObjectProtocol

# 출력:
# DeprecationWarning: 'from vmkis import KisObjectProtocol'은(는)
# 더 이상 권장되지 않습니다.
# 대신 'from vmkis.types import KisObjectProtocol'을(를) 사용하세요.
# 이 기능은 v3.0.0에서 제거될 예정입니다.
```

#### 3️⃣ 제거 (v3.0)

- ✅ 신규 기능만 제공
- ❌ 기존 경로 작동 불가

**예시**:

```python
# v3.0: Deprecation 경로 완전 제거
from vmkis import KisObjectProtocol  # ❌ 에러!
# AttributeError: module 'vmkis' has no attribute 'KisObjectProtocol'

# ✅ 올바른 방식
from vmkis.types import KisObjectProtocol
```

### 4.3 마이그레이션 타임라인

```text
┌─────────────────────────────────────────────────────────────┐
│ Breaking Change 제거 프로세스 (공개 API)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  v2.2.0 (2025-12)  →  v2.3~v2.9 (2026-01~06)  →  v3.0 (2026-06+)
│  신규 경로 추가          경고 표시                  완전 제거
│  (기존 경로 유지)      (기존 경로 유지)
│
│  User Action:
│  ┌─────────┐      ┌──────────────────┐       ┌─────────┐
│  │초기 준비 │──→   │마이그레이션 실행  │  →    │업그레이드│
│  │(필요없음)│      │(v2.9.x까지 유예)  │       │(필수)   │
│  └─────────┘      └──────────────────┘       └─────────┘
│
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 보장되는 안정성

### 5.1 메이저 버전 내 보장

**v2.x에서 보장**:

```python
# ✅ v2.x 내 안정성 보장
from vmkis import VmKis, Quote, Balance, Order

# 모든 v2.0~v2.9.9 버전에서 동일하게 작동
kis = VmKis(app_key="...", app_secret="...")
quote = kis.stock("005930").quote()  # Always works
```

**보장 범위**:

- 공개 API 메서드 이름
- 반환 타입 구조
- 파라미터 순서
- 기본 기능

**보장 안 하는 범위**:

- 내부 구현 (vmkis._internal)
- 성능 특성
- 에러 메시지 정확한 문구
- 시간 초과 값

### 5.2 Minor 버전 내 추가 사항

**호환성 유지 변경**:

- ✅ 선택적 파라미터 추가
- ✅ 새로운 클래스/함수 추가
- ✅ 새로운 예외 타입 추가
- ✅ 성능 최적화
- ✅ 버그 수정

**예시**:

```python
# v2.0
quote = kis.stock("005930").quote()
# {'price': 60000, 'volume': 1000000}

# v2.1 (호환성 유지)
quote = kis.stock("005930").quote(include_extended=True)
# {'price': 60000, 'volume': 1000000, 'extended': {...}}

# ✅ v2.0 코드도 v2.1에서 계속 작동
quote = kis.stock("005930").quote()
```

---

## 6. 버전 선택 가이드

### 6.1 버전별 권장 사용자

| 버전 | 상태 | 추천 | 이유 |
|------|------|------|------|
| **v1.x** | 🔴 END-OF-LIFE | ❌ 사용 금지 | 보안 업데이트 없음 |
| **v2.0~v2.1** | 🟢 안정 | ✅ 프로덕션 | 안정적이고 지원됨 |
| **v2.2~v2.9** | 🟢 안정 (개선중) | ✅ 권장 | 최신 기능 + 호환성 |
| **v3.0-beta** | 🟡 베타 | ⚠️ 테스트용 | 새 기능 미리보기 |

### 6.2 업그레이드 계획

```text
✅ 프로덕션 환경:
1. v2.0 → v2.9.x: 안전 (호환성 보장)
2. v2.9.x → v3.0: 마이그레이션 가이드 필요

⚠️ 테스트 환경:
1. 항상 최신 버전 권장
2. 주 1회 업그레이드 테스트

❌ 레거시 코드:
1. v1.x 즉시 마이그레이션
2. 보안 취약점 위험
```

---

## 7. 지원 정책

### 7.1 버전별 지원 기간

```text
v1.x  ════════════════════════════ (END-OF-LIFE, 2025년 이전)
      0개월 지원 (이미 종료)

v2.x  ════════════════════════════════════════════════════════
      2025-12 ~  2026-12 (12개월 지원)
      ↓
v3.0-beta ════════════════════════════════════════════════════
           2026-01 ~ 2027-01 (12개월 지원 계획)

Key:
━ 일반 지원 (보안 업데이트)
 Security patch 지원
```

### 7.2 지원 유형

| 지원 유형 | 내용 | 기간 |
|---------|------|------|
| **일반 지원** | 버그 수정, 성능 개선 | 12개월 |
| **보안 패치** | 보안 취약점 수정 | 12개월 (최소 3개월 추가) |
| **하위 호환성** | Breaking Change 없음 | 버전 내내 |
| **질문/이슈** | GitHub Issues/토론 | 지속 (우선순위 낮음) |

---

## 8. 버전 확인 및 업데이트

### 8.1 현재 버전 확인

```python
import vmkis

print(f"VmKis 버전: {vmkis.__version__}")
# 출력: VmKis 버전: 2.2.0
```

### 8.2 최신 버전 확인

```bash
# PyPI에서 최신 버전 확인
pip index versions vmkis

# 또는
pip list --outdated | grep vmkis
```

### 8.3 버전 고정 (권장)

```bash
# requirements.txt
vmkis>=2.0.0,<3.0.0          # v2.x만 사용 (호환성 보장)

# 또는 특정 버전
vmkis==2.2.0                 # 정확히 v2.2.0만 사용

# 또는 최신 유지
vmkis~=2.2                   # v2.2.x 최신 (v2.3은 미포함)
```

### 8.4 안전한 업그레이드

```bash
# 1. 테스트 환경에서 먼저 테스트
pip install --upgrade vmkis --dry-run

# 2. 충돌 확인
pip check

# 3. 실제 업그레이드
pip install --upgrade vmkis

# 4. 버전 확인
python -c "import vmkis; print(vmkis.__version__)"

# 5. 테스트 실행
pytest tests/
```

---

## 9. 마이그레이션 가이드

### 9.1 v1.x → v2.x 마이그레이션

**변경 사항**:

```python
# v1.x
from vmkis.kis import KIS
kis = KIS(...)
quote = kis.get_quote("005930")

# v2.x
from vmkis import VmKis
kis = VmKis(...)
quote = kis.stock("005930").quote()
```

### 9.2 v2.x → v3.x 마이그레이션 (향후)

**주요 변경**:

- 공개 API 축소 (154개 → 15개)
- Protocol import 변경
- Breaking Change 일부

---

## 10. 버전 호환성 매트릭스

### 10.1 Python 버전 지원

| Python | v2.x | v3.x | 상태 |
|--------|------|------|------|
| **3.8** | ✅ | ⚠️ | 지원 종료 예정 (2024년) |
| **3.9** | ✅ | ✅ | 지원 종료 예정 (2025년 10월) |
| **3.10** | ✅ | ✅ | 지원 종료 예정 (2026년 10월) |
| **3.11** | ✅ | ✅ | 지원 종료 예정 (2027년 10월) |
| **3.12** | ✅ | ✅ | 현재 |

### 10.2 의존성 버전 호환성

| 라이브러리 | v2.x | 호환성 |
|-----------|------|--------|
| **requests** | >=2.25.0 | ✅ 유지 |
| **pyyaml** | >=5.4 | ✅ 유지 |
| **websockets** | >=10.0 | ✅ 유지 |

---

## 11. 문제 보고 및 보안

### 11.1 보안 취약점 보고

```markdown
# 보안 취약점 발견 시:

1. GitHub Issues에 공개하지 마세요
2. security@vm-stock-kis.org 또는 private message로 보고
3. 48시간 내 응답 (목표)
4. 패치 후 공개 (조율)
```

### 11.2 버그 보고

```markdown
# GitHub Issues에서:

1. [버전 명시] vmkis==2.2.0
2. [재현 단계] 명확한 코드 예제
3. [예상] 어떻게 작동해야 함
4. [실제] 어떻게 작동하는지
```

---

## 12. FAQ

### Q1: v2.1에서 v2.2로 업그레이드해도 안전한가요?

✅ **예**. v2.x 내에서의 모든 업그레이드는 호환성을 보장합니다.

### Q2: v3.0은 언제 나오나요?

📅 **예정**: 2026년 6월경 (확정 아님)

### Q3: v2.x를 계속 사용해도 되나요?

✅ **예, 하지만**: v3.0 출시 후 12개월 지원 예정

### Q4: Breaking Change 목록을 어디서 보나요?

📋 **CHANGELOG.md** 또는 **마이그레이션 가이드** 참조

---

## 13. 참고 자료

- [Python PEP 440](https://www.python.org/dev/peps/pep-0440/) - 버전 정책
- [Semantic Versioning](https://semver.org/) - 의미론적 버전
- [Python 릴리스 정책](https://devguide.python.org/versions/) - Python 버전 지원
- [CHANGELOG.md](../../CHANGELOG.md) - 변경 기록

---

**마지막 업데이트**: 2025-12-20
**검토 주기**: 매 메이저 버전
**다음 검토**: v3.0 베타 출시 시
