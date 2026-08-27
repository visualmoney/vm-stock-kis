# 기여 가이드 (Contributing Guide)

VM-Stock-KIS 프로젝트에 기여해 주셔서 감사합니다! 🎉

이 문서는 프로젝트에 기여하는 방법을 설명합니다.

---

## 목차

1. [개발 환경 설정](#개발-환경-설정)
2. [브랜치 전략](#브랜치-전략)
3. [코딩 규칙](#코딩-규칙)
4. [Pull Request 프로세스](#pull-request-프로세스)
5. [테스트 작성 가이드](#테스트-작성-가이드)
6. [문서화 가이드](#문서화-가이드)
7. [Issue 작성 가이드](#issue-작성-가이드)
8. [커뮤니티 행동 강령](#커뮤니티-행동-강령)

---

## 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/Soju06/python-kis.git
cd vm-stock-kis
```

### 2. Poetry 설치 및 의존성 설치

Poetry가 없다면 먼저 설치:

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -
```

프로젝트 의존성 설치:

```bash
poetry install --with=dev
```

### 3. 가상환경 활성화

```bash
poetry shell
```

### 4. Pre-commit 훅 설정 (선택)

```bash
poetry run pre-commit install
```

### 5. 테스트 실행 확인

```bash
# 전체 테스트
poetry run pytest

# 커버리지 포함
poetry run pytest --cov=vmkis --cov-report=html

# 특정 테스트만
poetry run pytest tests/unit/test_public_api_imports.py
```

---

## 브랜치 전략

### 브랜치 명명 규칙

```
feature/<기능명>     # 새로운 기능 추가
fix/<버그명>         # 버그 수정
docs/<문서명>        # 문서 수정
refactor/<개선명>    # 리팩토링
test/<테스트명>      # 테스트 추가
chore/<작업명>       # 빌드/설정 변경
```

### 브랜치 생성 예시

```bash
# 새 기능 추가
git checkout -b feature/add-futures-api

# 버그 수정
git checkout -b fix/websocket-reconnect

# 문서 개선
git checkout -b docs/update-quickstart
```

### 작업 흐름

1. `main`에서 새 브랜치 생성
2. 변경사항 커밋
3. Push 후 Pull Request 생성
4. 리뷰 및 테스트 통과
5. `main`에 병합

---

## 코딩 규칙

### 1. Python 스타일 가이드

**PEP 8** 준수를 기본으로 하되, 프로젝트 규칙 우선:

```python
# ✅ 권장
def get_quote(symbol: str, market: str = "KRX") -> Quote:
    """시세 정보를 조회합니다.

    Args:
        symbol: 종목 코드 (예: "005930")
        market: 시장 코드 (기본값: "KRX")

    Returns:
        시세 정보 객체

    Raises:
        KisAPIError: API 호출 실패 시
    """
    return self.kis.api(...)

# ❌ 지양
def getQuote(symbol, market="KRX"):  # 카멜케이스, 타입 힌트 없음
    return self.kis.api(...)
```

### 2. 타입 힌팅 필수

모든 공개 함수/메서드에 타입 힌트 추가:

```python
from typing import Optional, List, Dict, Any

def process_orders(
    orders: List[Order],
    filter_func: Optional[Callable[[Order], bool]] = None
) -> Dict[str, Any]:
    ...
```

### 3. Docstring 작성

모든 공개 API에 Google 스타일 Docstring 작성:

```python
def buy_stock(self, symbol: str, quantity: int, price: int) -> Order:
    """주식 매수 주문을 실행합니다.

    Args:
        symbol: 종목 코드 (6자리)
        quantity: 주문 수량
        price: 주문 가격 (원)

    Returns:
        주문 정보 객체

    Raises:
        KisAPIError: 주문 실패 시
        ValueError: 잘못된 파라미터

    Example:
        >>> order = kis.stock("005930").buy(qty=10, price=65000)
        >>> print(order.order_number)
    """
    ...
```

### 4. 명명 규칙

| 타입 | 규칙 | 예시 |
|------|------|------|
| 클래스 | PascalCase | `KisQuote`, `VmKis` |
| 함수/메서드 | snake_case | `get_balance()`, `place_order()` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY`, `API_VERSION` |
| 내부 변수 | snake_case | `order_count`, `balance_info` |
| Private | `_`접두사 | `_internal_method()` |

### 5. Import 순서

```python
# 1. 표준 라이브러리
import os
import sys
from typing import Optional

# 2. 서드파티 라이브러리
import requests
from websocket import WebSocket

# 3. 로컬 모듈
from vmkis.client.auth import KisAuth
from vmkis.types import Quote
```

---

## Pull Request 프로세스

### 1. PR 생성 전 체크리스트

- [ ] 모든 테스트 통과 (`poetry run pytest`)
- [ ] 타입 체크 통과 (IDE에서 확인)
- [ ] 새로운 기능은 테스트 코드 포함
- [ ] 공개 API는 Docstring 작성
- [ ] CHANGELOG.md 업데이트 (주요 변경사항)
- [ ] 커밋 메시지 규칙 준수

### 2. PR 템플릿

```markdown
## 변경 사항

- 새로운 기능 / 버그 수정 / 리팩토링 설명

## 관련 Issue

Closes #123

## 테스트

- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 추가/수정
- [ ] 수동 테스트 완료

## 문서

- [ ] README.md 업데이트 (필요시)
- [ ] QUICKSTART.md 업데이트 (필요시)
- [ ] API 문서 업데이트 (필요시)

## Breaking Changes

- 있다면 명시, 없으면 "없음"

## 스크린샷 (선택)

(시각적 변경사항이 있다면 첨부)
```

### 3. 커밋 메시지 규칙

**형식**: `<타입>(<범위>): <제목>`

**타입**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**예시**:
```bash
feat(api): add futures trading API
fix(websocket): resolve reconnection issue
docs(quickstart): update config.yaml example
refactor(helpers): simplify load_config logic
test(unit): add tests for load_config with profiles
```

### 4. PR 리뷰 프로세스

1. **자동 검사**: GitHub Actions CI 실행
   - 테스트 실행
   - 커버리지 체크 (최소 80%)
   - 코드 스타일 검사

2. **리뷰어 지정**: 메인테이너가 리뷰

3. **피드백 반영**: 리뷰 코멘트에 응답 및 수정

4. **승인 후 병합**: 리뷰어가 승인하면 `main`에 병합

---

## 테스트 작성 가이드

### 1. 테스트 구조

```
tests/
├── unit/                    # 단위 테스트 (API 호출 없이)
│   ├── test_public_api_imports.py
│   ├── test_simple_helpers.py
│   └── test_load_config.py
│
├── integration/             # 통합 테스트 (실제 API 호출)
│   ├── test_stock_quote.py
│   ├── test_account_balance.py
│   └── test_websocket.py
│
└── fixtures/                # 테스트 데이터
    ├── config_sample.yaml
    └── mock_responses.json
```

### 2. 단위 테스트 예시

```python
# tests/unit/test_helpers.py
import pytest
from vmkis.helpers import load_config

def test_load_config_single_profile():
    """단일 프로필 설정 파일 로드 테스트"""
    cfg = load_config("config.example.virtual.yaml")

    assert cfg["id"] == "YOUR_VIRTUAL_ID"
    assert cfg["virtual"] is True

def test_load_config_multi_profile_default():
    """다중 프로필 설정 파일에서 기본 프로필 로드"""
    cfg = load_config("config.example.yaml")

    assert cfg["id"] == "YOUR_VIRTUAL_ID"  # default = virtual

def test_load_config_multi_profile_explicit():
    """다중 프로필 설정 파일에서 명시적 프로필 선택"""
    cfg = load_config("config.example.yaml", profile="real")

    assert cfg["id"] == "YOUR_REAL_ID"
    assert cfg["virtual"] is False

def test_load_config_profile_not_found():
    """존재하지 않는 프로필 선택 시 에러"""
    with pytest.raises(ValueError, match="Profile 'unknown' not found"):
        load_config("config.example.yaml", profile="unknown")
```

### 3. 통합 테스트 예시

```python
# tests/integration/test_stock_quote.py
import pytest
from vmkis import VmKis, KisAuth

@pytest.fixture
def kis_client():
    """실제 KIS 클라이언트 (모의투자)"""
    auth = KisAuth(
        id=os.environ["KIS_ID"],
        account=os.environ["KIS_ACCOUNT"],
        appkey=os.environ["KIS_APPKEY"],
        secretkey=os.environ["KIS_SECRET"],
        virtual=True,
    )
    return VmKis(auth)

def test_get_quote_samsung(kis_client):
    """삼성전자 시세 조회"""
    quote = kis_client.stock("005930").quote()

    assert quote.symbol == "005930"
    assert quote.name == "삼성전자"
    assert quote.price > 0
    assert quote.volume >= 0
```

### 4. 테스트 실행

```bash
# 전체 테스트
poetry run pytest

# 특정 파일만
poetry run pytest tests/unit/test_helpers.py

# 특정 테스트만
poetry run pytest tests/unit/test_helpers.py::test_load_config_single_profile

# 커버리지 포함
poetry run pytest --cov=vmkis --cov-report=html
```

---

## 문서화 가이드

### 1. 문서 구조

```
docs/
├── INDEX.md                  # 문서 인덱스
├── QUICKSTART.md             # 빠른 시작 (루트에도 복사)
├── SIMPLEKIS_GUIDE.md        # SimpleKIS 가이드
│
├── architecture/             # 아키텍처 문서
│   └── ARCHITECTURE.md
│
├── developer/                # 개발자 가이드
│   └── DEVELOPER_GUIDE.md
│
├── user/                     # 사용자 가이드
│   └── USER_GUIDE.md
│
└── reports/                  # 보고서
    ├── ARCHITECTURE_REPORT_V3_KR.md
    └── CODE_REVIEW.md
```

### 2. 문서 작성 규칙

**마크다운 스타일**:
```markdown
# 제목 1 (H1) - 문서 제목에만 사용

## 제목 2 (H2) - 주요 섹션

### 제목 3 (H3) - 하위 섹션

#### 제목 4 (H4) - 세부 항목

**굵게**, *기울임*, `인라인 코드`

- 목록 항목 1
- 목록 항목 2

1. 순서 목록 1
2. 순서 목록 2

[링크 텍스트](URL)

```python
# 코드 블록
def example():
    pass
```
```

**예제 코드**:
- 실제 작동하는 코드 작성
- 주석으로 설명 추가
- 민감 정보 제외 (config 예제는 `YOUR_*` 사용)

### 3. API 레퍼런스 자동 생성

```bash
# (향후 추가 예정)
poetry run sphinx-apidoc -o docs/api vmkis
poetry run sphinx-build -b html docs docs/_build
```

---

## Issue 작성 가이드

### 1. 버그 리포트

```markdown
## 버그 설명

(버그 현상을 명확히 설명)

## 재현 방법

1. ...
2. ...
3. ...

## 예상 동작

(정상적으로 작동했을 때의 결과)

## 실제 동작

(실제로 발생한 현상)

## 환경

- OS: Windows 11 / macOS 14 / Ubuntu 22.04
- Python 버전: 3.11.5
- vm-stock-kis 버전: 2.1.7
- 설치 방법: pip / poetry

## 에러 로그

```python
(에러 메시지 또는 스택 트레이스 붙여넣기)
```

## 추가 정보

(스크린샷, 관련 코드 등)
```

### 2. 기능 제안

```markdown
## 제안 배경

(왜 이 기능이 필요한지)

## 제안 내용

(어떤 기능을 추가하고 싶은지)

## 사용 예시

```python
# 제안하는 API 사용법
result = kis.new_feature(...)
```

## 대안 고려

(다른 해결 방법이 있는지)

## 기타

(추가 의견)
```

---

## 커뮤니티 행동 강령

### 우리의 약속

- 🤝 **존중**: 모든 기여자를 존중합니다
- 🌈 **포용**: 다양성을 환영합니다
- 💬 **건설적 피드백**: 긍정적이고 건설적인 피드백을 제공합니다
- 🚀 **협업**: 함께 더 나은 프로젝트를 만듭니다

### 금지 행동

- 🚫 개인 공격 또는 비방
- 🚫 괴롭힘 또는 차별
- 🚫 스팸 또는 홍보성 게시물
- 🚫 부적절한 콘텐츠

### 위반 시 조치

경고 → 일시 정지 → 영구 차단

---

## FAQ

### Q1: 코드를 처음 기여하는데 어디서부터 시작해야 하나요?

**A**: [Good First Issue](https://github.com/Soju06/python-kis/labels/good%20first%20issue) 라벨이 붙은 이슈부터 시작하세요.

### Q2: 테스트를 작성하려면 실제 API 키가 필요한가요?

**A**: 단위 테스트는 API 키 없이 작성 가능합니다. 통합 테스트는 모의투자 API 키를 사용하세요.

### Q3: 문서만 수정하고 싶은데 개발 환경 전체를 설치해야 하나요?

**A**: 아니요. GitHub 웹 인터페이스에서 직접 마크다운 파일을 수정하고 PR을 생성할 수 있습니다.

### Q4: PR이 승인되기까지 얼마나 걸리나요?

**A**: 일반적으로 1-3일 내에 리뷰가 진행됩니다. 복잡한 변경사항은 더 오래 걸릴 수 있습니다.

### Q5: Breaking Change를 제안하고 싶습니다.

**A**: Issue를 먼저 생성하여 커뮤니티 의견을 수렴한 후 PR을 작성하세요.

### Q6: 재시도 메커니즘을 어떻게 사용하나요?

**A**: 429/5xx 에러에 대한 자동 재시도를 원하면 데코레이터를 사용하세요:

```python
from vmkis.utils.retry import with_retry

@with_retry(max_retries=5, initial_delay=2.0)
def fetch_quote(symbol):
    return kis.stock(symbol).quote()
```

### Q7: JSON 로깅을 어떻게 활성화하나요?

**A**: 프로덕션 환경에서 ELK/Datadog과 연동하려면:

```python
from vmkis.logging import enable_json_logging

enable_json_logging()
# 이후 로그는 JSON 형식으로 출력됨
```

### Q8: 예외 처리는 어떻게 하나요?

**A**: 새로운 예외 클래스들이 추가되었습니다:

```python
from vmkis.exceptions import (
    KisConnectionError,
    KisAuthenticationError,
    KisRateLimitError,
    KisServerError,
)

try:
    quote = kis.stock("005930").quote()
except KisRateLimitError:
    # 속도 제한 - 재시도 가능
    pass
except KisAuthenticationError:
    # 인증 실패 - 특별 처리
    pass
```

---

## 라이선스

기여한 코드는 프로젝트의 MIT 라이선스를 따릅니다.

---

## 감사 인사

VM-Stock-KIS에 기여해 주신 모든 분들께 감사드립니다! 🙏

- [기여자 목록](https://github.com/Soju06/python-kis/graphs/contributors)

---

질문이 있으시면 [GitHub Discussions](https://github.com/Soju06/python-kis/discussions) 또는 Issue를 통해 문의하세요.
