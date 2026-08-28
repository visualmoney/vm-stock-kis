# VM-Stock-KIS - 소프트웨어 아키텍처 문서

## 목차

1. [개요](#개요)
2. [핵심 설계 원칙](#핵심-설계-원칙)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [모듈 구조](#모듈-구조)
5. [핵심 컴포넌트](#핵심-컴포넌트)
6. [데이터 흐름](#데이터-흐름)
7. [의존성 분석](#의존성-분석)

---

## 개요

### 프로젝트 정보

- **프로젝트명**: VM-Stock-KIS (Korea Investment Securities API Wrapper)
- **목적**: 한국투자증권의 OpenAPI를 파이썬 환경에서 쉽게 사용할 수 있도록 제공
- **버전**: 0.0.1 (이 배포명의 첫 릴리스. `CHANGELOG.md` 참고)
- **라이선스**: MIT
- **최소 Python 버전**: 3.10+

### 주요 특징

- ✅ 모든 객체에 대한 Type Hint 지원
- ✅ 웹소켓 기반 실시간 데이터 스트리밍
- ✅ 완벽한 재연결 복구 메커니즘
- ✅ 표준 영어 네이밍 컨벤션
- ✅ Rate Limiting 자동 관리
- ✅ Thread-safe 구현

---

## 2. 공개 타입 분리 정책

### 2.1 문제 정의 및 해결

포크 이후 정리한 내용입니다. 전부 `0.0.1` 에 함께 실렸습니다.

- 루트 `__all__` 을 12개로 축소
- `public_types.py` 분리 완료
- Deprecation 메커니즘 구현 완료

**공개 API 구조**:

```python
# src/vmkis/public_types.py
from typing import TypeAlias

Quote: TypeAlias = _KisQuoteResponse
Balance: TypeAlias = _KisIntegrationBalance
Order: TypeAlias = _KisOrder
Chart: TypeAlias = _KisChart
Orderbook: TypeAlias = _KisOrderbook
MarketInfo: TypeAlias = _KisMarketInfo
TradingHours: TypeAlias = _KisTradingHours

__all__ = ["Quote", "Balance", "Order", "Chart", "Orderbook", "MarketInfo", "TradingHours"]
```

```python
# src/vmkis/__init__.py
__all__ = [
    # 핵심 클래스
    "VmKis", "KisAuth",
    # 공개 타입
    "Quote", "Balance", "Order", "Chart", "Orderbook", "MarketInfo", "TradingHours",
    # 초보자 도구
    "SimpleKIS", "create_client", "save_config_interactive",
]
```

### 2.2 사용 예제

```python
# 권장 방식 (일반 사용자)
from vmkis import VmKis, KisAuth, Quote, Balance

def analyze(quote: Quote, balance: Balance) -> None:
    print(f"{quote.name}: {quote.price:,}원")

# 고급 사용자 (내부 구조 접근)
from vmkis.types import KisObjectProtocol
from vmkis.adapter.product.quote import KisQuotableProductMixin
```

### 2.3 마이그레이션 타임라인

| 버전 | 상태 | 루트 import | 명시적 경로 |
|---|---|---|---|
| 0.0.x | ✅ 현재 | 동작 (DeprecationWarning) | ✅ 권장 |
| 1.0.0 | Breaking | ❌ 제거 | ✅ 필수 |

---

## 핵심 설계 원칙

### 1. 허브-스포크 구조 (Hub-and-Spoke)

`VmKis` 를 허브로 두고, 나머지 그룹이 그 주위에 붙는 형태입니다.

```text
                         ┌──────────────────────────┐
                         │   VmKis (kis.py) — 허브   │
                         │  scope/adapter 를 클래스  │
                         │  본문 import 로 조립      │
                         └───────┬──────────────────┘
              조립(compose)      │        역참조: self: "VmKis"
        ┌───────────────┬────────┴────────┐   (TYPE_CHECKING 전용)
        ▼               ▼                 ▼
   ┌─────────┐    ┌──────────┐      ┌──────────┐
   │  scope/ │───▶│ adapter/ │◀────▶│   api/   │ ◀─ api ↔ adapter 순환은
   └─────────┘    └──────────┘ 의도적└─┬───┬────┘    의도적 (rich object)
                        순환           │   │ ▲
                                       │   │
                                       ▼   ▼
                                 ┌──────────┐   ┌────────────┐
                                 │responses/│──▶│  client/   │◀── event/
                                 └──────────┘   └─────┬──────┘   (구독·필터)
                                  의도적:              │
                                  응답은 client 위에   ▼
                                                 ┌──────────┐
                                                 │  utils/  │
                                                 └──────────┘

   느슨한 상하 순서: scope → adapter/api → event → responses → client → utils
```

> **이 그림은 "계층"이 아닙니다.** 예전 문서는 `API → Client → Response Transform
> → Utility` 하향 단방향 계층으로 서술했으나 **코드와 일치하지 않습니다.**
> AST 전수 분석 결과 런타임 모듈레벨 역방향 import 가 **12건(간선 종류로는 7종)**
> 존재합니다. `import vmkis` 가 정상 동작하는 것은 순환이 없어서가 아니라,
> 아래 불변식이 로드 순서를 지켜 주기 때문입니다.

### 1.1 반드시 지켜야 할 불변식

아래는 **암묵적으로만 지켜지던 규칙**입니다. 어기면 패키지가 import 단계에서
깨지거나, 이벤트가 조용히 사라집니다.

1. **`vmkis.kis` 를 모듈 레벨에서 import 하지 않습니다.**
   `if TYPE_CHECKING:` 블록 안에서만 허용합니다. 전체 패키지가 정상 로드되는
   **유일한 이유**입니다.

2. **새로운 모듈-레벨 역방향 간선을 만들지 않습니다.**
   하위 그룹이 상위 지식을 필요로 하면 **등록을 역전**하거나 **주입**받습니다.
   기존 역방향은 아래 세 가지로 동결합니다.

   | 간선 | 위치 | 판정 |
   |---|---|---|
   | `responses → client` | `responses/response.py`, `responses/exceptions.py` | 의도적 — 응답은 client 타입 위에 성립 |
   | `api ↔ adapter` | 주문/잔고 계열 | 의도적 — 응답 객체가 Mixin 을 상속 (rich object) |
   | ~~`client → api`~~ | ~~`client/websocket.py`~~ | ✅ **해소됨** — 자기등록으로 역전 ([#17](https://github.com/visualmoney/vm-stock-kis/issues/17)) |
   | ~~`utils → client`~~ | ~~`utils/retry.py`~~ | ✅ **해소됨** ([#18](https://github.com/visualmoney/vm-stock-kis/issues/18)) |

   **정리 대상 두 건이 모두 해소됐습니다.** 남은 역방향은 전부 의도적입니다.
   두 건을 없앤 방법이 같은 발상이라 앞으로도 참고가 됩니다.
   `utils/retry.py` 는 재시도 대상 예외 **목록**을 들고 있느라 `client` 를
   참조했습니다. 목록을 옮기는 대신 **판단 근거를 예외 자신에게 넘겼습니다** —
   `KisException.retryable` 표식을 보고 `getattr` 로 확인하므로 유틸은 아무것도
   import 하지 않습니다. 하위 계층이 상위 지식을 필요로 할 때의 일반적인 해법입니다.

   **이 불변식은 기계가 지킵니다** ([#50](https://github.com/visualmoney/vm-stock-kis/issues/50)).
   `pyproject.toml` 의 `[tool.importlinter]` 에 계약 2개가 있고 CI 의 `lint` 잡이
   `lint-imports` 로 검사합니다. 계약이 덮는 것은 **해소된 위 두 간선뿐**입니다 —
   `responses → client` 와 `api ↔ adapter` 는 의도적이라 넣지 않았고,
   `event → api` 는 아직 판정되지 않았습니다(불변식 4번).

   계약을 넣으면서 **세 번째 역방향 간선이 드러났습니다.** `utils/diagnosis.py` 가
   `import vmkis` 로 루트 파사드를 모듈 레벨에서 끌어오고 있었습니다. 루트는
   `kis` · `api` · `client` · `scope` 를 전부 import 하므로 `utils` 가 패키지 전체에
   의존한 셈입니다. 필요한 값은 버전과 배포명 둘뿐이어서 `vmkis.__env__` 를 직접
   보도록 바꿨습니다. **`import <루트패키지>` 한 줄은 간선 하나처럼 보이지만
   그래프에서는 상위 전체입니다.** 그룹 단위로만 보는 눈(그리고 사람이 쓴 AST
   스캔)은 이것을 놓칩니다.

   계약이 못 보는 것도 두 가지 적어 둡니다.

   - **면제는 모듈 쌍 단위입니다.** `client/messaging.py` 의 지연 import 1건이
     `ignore_imports` 에 있는데, 이 import 를 파일 상단으로 올려도 `lint-imports`
     는 통과합니다(실측). `tests/unit/test_import_contracts.py` 의 AST 검사가
     그 자리를 막습니다.
   - **그래프가 비어 있어도 통과합니다.** `src/vmkis` 의 디렉터리 대부분에
     `__init__.py` 가 없어 `root_packages` 를 일일이 나열해야 합니다. 빠뜨리면
     그 서브패키지는 검사되지 않은 채 초록이 됩니다. 같은 테스트 파일이
     "모든 모듈이 그래프에 있는가"를 확인합니다.

3. **순환 우회용 지연 import 에는 사유 주석을 답니다.**
   함수 안의 import 를 "정리"하려고 파일 상단으로 올리면 패키지가 로드 불능이
   될 수 있습니다. 왜 거기 있는지 적혀 있지 않으면 다음 사람이 반드시 옮깁니다.

4. **`event/` 는 이 그림에 포함됩니다.**
   예전 다이어그램에는 `event/` 가 아예 없어서 `client → event`, `event → api`
   간선을 위반인지 아닌지 판정할 수 없었습니다.

### 2. 프로토콜 기반 설계 (Protocol-Based Design)

- `KisObjectProtocol`: 모든 API 객체가 준수해야 하는 인터페이스
- `KisResponseProtocol`: API 응답 객체의 표준 인터페이스
- `KisEventFilter`: 이벤트 필터링 프로토콜

### 3. 동적 타입 시스템 (Dynamic Type System)

- `KisType` 기반의 유연한 타입 변환
- `KisObject`를 통한 자동 객체 변환
- `KisDynamic` 프로토콜로 동적 속성 접근

### 4. 이벤트 기반 아키텍처 (Event-Driven Architecture)

- 실시간 데이터는 이벤트 핸들러를 통해 처리
- Pub-Sub 패턴 구현
- GC에 의해 자동으로 관리되는 이벤트 구독

### 5. Mixin 패턴 활용

- 기능 추가를 위해 Mixin 클래스 사용
- `KisObjectBase`를 상속하고 필요한 Mixin 추가
- 예: `KisOrderableAccountProductMixin`, `KisQuotableProductMixin`

---

## 시스템 아키텍처

### 전체 데이터 흐름도

```text
┌──────────────────────────────────────────────────────────────────┐
│                      사용자 코드                                   │
│  kis = VmKis("secret.json")                                      │
│  stock = kis.stock("000660")                                     │
│  quote = stock.quote()                                           │
│  kis.account().balance()                                         │
└──────────────────────┬───────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼──────────────────┐  ┌──────▼──────────────────┐
│  Scope Layer (API 진입점) │  │  WebSocket (실시간)    │
│  - account()             │  │  - on_price()          │
│  - stock()               │  │  - on_execution()      │
│  - trading_hours()       │  │  - on_orderbook()      │
└───────┬──────────────────┘  └──────┬──────────────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  Adapter Layer (기능 추가)   │
        │  - KisQuotableProductMixin  │
        │  - KisOrderableOrderMixin   │
        │  - KisRealtimeOrderable...  │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  VmKis Client (중앙 관리)    │
        │  - HTTP Session 관리        │
        │  - WebSocket 관리           │
        │  - Token 관리               │
        │  - Rate Limiting            │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼──────────────────┐  ┌──────▼──────────────────┐
│  HTTP Client             │  │  WebSocket Client      │
│  (requests library)      │  │  (websocket-client)    │
└───────┬──────────────────┘  └──────┬──────────────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  KIS OpenAPI Servers       │
        │  - Real Domain (실전)       │
        │  - Virtual Domain (모의)    │
        └───────────────────────────┘
```

---

## 모듈 구조

### 디렉토리 레이아웃

```text
src/vmkis/
├── __init__.py           # 공개 API 노출
├── __env__.py            # 환경 설정 및 상수
├── kis.py                # VmKis 메인 클래스
├── logging.py            # 로깅 유틸리티
├── types.py              # 고급 사용자용 타입 (약 100개 export)
├── public_types.py       # 공개 타입 별칭 (9개) ← 일반 사용자는 여기
│
├── api/                  # API 계층 (REST, WebSocket)
│   ├── auth/             # 인증 관련 API
│   │   └── token.py
│   ├── stock/            # 주식 관련 API
│   │   ├── quote.py      # 시세 조회
│   │   ├── chart.py      # 차트 조회
│   │   ├── order_book.py # 호가 조회
│   │   ├── trading_hours.py
│   │   └── ...
│   └── websocket/        # 실시간 웹소켓 API
│       ├── price.py      # 실시간 시세
│       ├── order_execution.py  # 실시간 체결
│       └── order_book.py # 실시간 호가
│
├── scope/                # Scope 계층 (API 진입점)
│   ├── base.py          # Scope 베이스 클래스
│   ├── account.py       # 계좌 Scope
│   └── stock.py         # 주식 Scope
│
├── adapter/              # Adapter 계층 (기능 믹스인)
│   ├── product/          # 상품 관련 어댑터
│   │   ├── quote.py
│   │   └── ...
│   ├── account_product/  # 계좌 상품 관련 어댑터
│   │   ├── order.py
│   │   ├── order_modify.py
│   │   └── ...
│   └── websocket/        # 웹소켓 어댑터
│       ├── price.py
│       ├── execution.py
│       └── ...
│
├── client/               # Client 계층 (저수준 통신)
│   ├── auth.py          # 인증 정보 관리 (KisAuth)
│   ├── account.py       # 계좌번호 관리
│   ├── appkey.py        # 앱키 관리
│   ├── exceptions.py    # 예외 클래스
│   ├── object.py        # 객체 베이스 클래스
│   ├── form.py          # HTTP/WebSocket 폼 데이터
│   ├── messaging.py     # WebSocket 메시징
│   ├── websocket.py     # WebSocket 클라이언트
│   ├── cache.py         # 캐시 저장소
│   ├── page.py          # 페이지 네이션
│   └── ...
│
├── responses/            # Response Transform 계층
│   ├── dynamic.py       # 동적 타입 시스템
│   ├── types.py         # KisType 구현체들
│   ├── response.py      # 응답 베이스 클래스
│   ├── websocket.py     # WebSocket 응답
│   ├── exceptions.py    # 응답 레벨 예외
│   └── ...
│
├── event/                # Event 계층
│   ├── handler.py       # 이벤트 핸들러 기반 클래스
│   ├── subscription.py  # 이벤트 구독 관련
│   └── filters/         # 이벤트 필터
│       ├── subscription.py
│       ├── product.py
│       ├── order.py
│       └── ...
│
└── utils/                # Utility 계층
    ├── rate_limit.py    # Rate Limiting
    ├── thread_safe.py   # Thread-safe 데코레이터
    ├── repr.py          # 커스텀 repr 구현
    ├── workspace.py     # 워크스페이스 관리
    ├── timezone.py      # 시간대 관리
    ├── timex.py         # 시간 표현식
    ├── typing.py        # 타입 유틸리티
    ├── math.py          # 수학 유틸리티
    ├── diagnosis.py     # 진단 유틸리티
    ├── reference.py     # 참조 카운팅
    └── ...
```

---

## 핵심 컴포넌트

### 1. VmKis (메인 클래스)

**역할**: 중앙 조율자로서 모든 API 호출의 진입점

**책임사항**:

- HTTP/WebSocket 세션 관리
- 인증 토큰 발급 및 관리
- Rate Limiting 적용
- 응답 변환 및 객체 생성

**주요 메서드**:

```python
class VmKis:
    def __init__(auth, virtual_auth=None, ...)
    def account() -> KisAccount         # 계좌 Scope
    def stock(symbol) -> KisStock       # 주식 Scope
    def request(...) -> KisObject       # 저수준 API 호출
    def api(...) -> KisObject           # API 래퍼
    @property websocket                 # WebSocket 클라이언트
```

### 2. Scope 계층 (진입점)

**클래스**:

- `KisAccountScope`: 계좌 관련 API의 진입점
- `KisStockScope`: 주식 관련 API의 진입점

**역할**:

- 특정 엔티티(계좌, 주식)에 대한 컨텍스트 제공
- Adapter 기능 추가

```python
# 사용 예
account = kis.account()           # KisAccountScope
balance = account.balance()       # KisBalance

stock = kis.stock("000660")       # KisStockScope
quote = stock.quote()             # KisQuote
```

### 3. Adapter 계층 (Mixin 기능)

**목적**: Scope에 기능을 동적으로 추가

**주요 Adapter들**:

- `KisQuotableProductMixin`: 시세 조회 기능
- `KisOrderableAccountProductMixin`: 주문 기능
- `KisWebsocketQuotableProductMixin`: 실시간 시세 구독

```python
class KisStock(KisStockScope, KisQuotableProductMixin, ...):
    pass
```

### 4. Response Transform 계층

**시스템**: 동적 타입 시스템 (`KisType`, `KisObject`)

**프로세스**:

1. API 응답 JSON 수신
2. `KisObject.transform_()` 호출
3. 응답 스키마에 따라 자동 변환
4. 타입 힌팅 정보 기반 객체 생성

```python
# 내부 동작
data = response.json()
quote = KisObject.transform_(data, KisQuote)  # 자동 변환
```

### 5. WebSocket 클라이언트

**역할**: 실시간 데이터 스트리밍 관리

**기능**:

- 자동 재연결
- 구독 복구
- 이벤트 기반 처리

```python
# 사용 예
def on_price(sender, e):
    print(e.response)

ticket = stock.on("price", on_price)
```

### 6. Event 시스템

**아키텍처**: Observer 패턴 + 이벤트 필터

**컴포넌트**:

- `KisEventHandler`: 이벤트 관리
- `KisEventTicket`: 구독 관리
- `KisEventFilter`: 이벤트 필터링

---

## 데이터 흐름

### 시세 조회 (REST API)

```text
User Code
    ↓
kis.stock("000660").quote()
    ↓
KisStockScope + KisQuotableProductMixin
    ↓
VmKis.api("usdh1") / VmKis.request()
    ↓
RateLimiter.wait()  (rate limit check)
    ↓
HTTP GET to KIS Server
    ↓
Response JSON
    ↓
KisObject.transform_(data, KisQuote)
    ↓
KisObjectBase.__kis_init__(kis)  (권한 주입)
    ↓
KisQuote Object 반환
    ↓
User Code
```

### 실시간 시세 (WebSocket)

```text
User Code
    ↓
stock.on("price", callback)
    ↓
KisWebsocketQuotableProductMixin.on()
    ↓
KisWebsocketClient.subscribe(H0STCNT0, symbol)
    ↓
WebSocket Connection (if not connected)
    ↓
Subscribe Message 전송
    ↓
KIS Server 확인
    ↓
Real-time Messages Receive Loop
    ↓
Parse & Transform to KisRealtimePrice
    ↓
Event Callback 호출
    ↓
User Callback 실행
```

---

## 의존성 분석

### 외부 라이브러리 의존성

```text
src/vmkis/
├── requests (>=2.32.3)
│   └── HTTP 통신
│
├── websocket-client (>=1.8.0)
│   └── WebSocket 실시간 데이터
│
├── cryptography (>=43.0.0)
│   └── 웹소켓 페이로드 복호화 (저장되는 자격증명과 무관)
│
├── colorlog (>=6.8.2)
│   └── 색상 로깅
│
├── tzdata
│   └── 시간대 정보
│
├── typing-extensions
│   └── 확장된 타입 힌팅
│
└── python-dotenv (>=1.2.1)
    └── .env 파일 로드
```

### 개발 의존성

```text
pytest (^9.0.1)
    └── 단위 테스트

pytest-cov (^7.0.0)
    └── 코드 커버리지

pytest-html (^4.1.1)
    └── HTML 리포트

pytest-asyncio (^1.3.0)
    └── 비동기 테스트
```

### 내부 모듈 의존성 그래프

```text
VmKis (중앙)
    ├── KisAccessToken
    ├── KisAuth
    ├── KisAccountNumber
    ├── RateLimiter
    ├── KisWebsocketClient
    │   └── KisWebsocketRequest
    │   └── KisWebsocketTR
    └── HTTP Session (requests.Session)

KisAccount / KisStock
    ├── KisObjectBase
    └── 각종 Adapter Mixin
        └── VmKis (참조)

Response Objects
    ├── KisResponse
    ├── KisObject (동적 변환)
    ├── KisType (타입 정보)
    └── KisObjectBase

Event System
    ├── KisEventHandler
    ├── KisEventFilter
    └── KisEventTicket
```

---

## 설계 패턴

### 1. 싱글톤 패턴

- VmKis: 애플리케이션당 1-2개 인스턴스 (실전, 모의)

### 2. 팩토리 패턴

- `KisObject.transform_()`: 동적 객체 생성
- API 응답 객체 생성

### 3. 옵저버 패턴

- 이벤트 시스템: Pub-Sub 패턴
- WebSocket 실시간 데이터

### 4. 데코레이터 패턴

- `@thread_safe`: Thread-safe 메서드
- `@custom_repr`: 커스텀 repr

### 5. Mixin 패턴

- 기능 추가: `KisQuotableProductMixin` 등
- 유연한 기능 조합

### 6. Template Method 패턴

- `KisObjectBase.__kis_init__()`: 초기화 로직
- `KisObjectBase.__kis_post_init__()`: 초기화 후처리

---

## Rate Limiting 전략

### 목적

- 한국투자증권 API 호출 제한 준수
- 실전: 초당 19개 요청 (`REAL_API_REQUEST_PER_SECOND`)
- 모의: 초당 2개 요청 (`VIRTUAL_API_REQUEST_PER_SECOND`)

> 값의 유일한 출처는 `src/vmkis/__env__.py` 입니다. 이 문서와 어긋나면
> `__env__.py` 가 맞습니다.

### 구현

```python
class RateLimiter:
    def wait()          # 요청 전 대기
    def on_success()    # 성공 시 처리
    def on_error()      # 에러 시 처리
```

---

## 에러 처리 전략

### 예외 계층구조

```text
Exception
├── KisException (기본)
│   ├── KisHTTPError (HTTP 에러)
│   │   └── 상태 코드, 응답 바디 포함
│   │
│   └── KisAPIError (API 에러)
│       ├── RT_CD, MSG_CD 포함
│       ├── TR_ID, GT_UID 포함
│       └── KisMarketNotOpenedError (시장 미개장)
│           └── 장 미개장 시 발생
│
└── KisNoneValueError (내부)
    └── 동적 타입 변환 시 값 부재
```

---

## 보안 고려사항

### 1. 토큰 관리

- 기본값: `~/.vmkis/` 디렉토리에 **평문 JSON**으로 저장 (암호화하지 않음)
- 신뢰할 수 없는 환경에서는 `keep_token=True`를 사용 금지
- 자세한 내용은 [SECURITY.md](../../SECURITY.md) 참조

### 2. 앱키 보호

- 코드에 하드코딩 금지
- 환경 변수 또는 파일 사용
- 깃에 커밋 금지

### 3. WebSocket 보안

- 원본 앱키 대신 WebSocket 접속키 사용
- KIS 권장사항 준수

---

## 확장성 고려사항

> **먼저 읽으세요**: 대부분의 경우 라이브러리를 고칠 필요가 없습니다.
> `VmKis.fetch()` 로 임의 TR 을 호출할 수 있습니다 —
> [미지원 API 호출 가이드](../user/EXTENDING_API.md) 참고.
> 아래는 **라이브러리에 1급 시민으로 통합**할 때의 절차입니다.

### 새로운 REST API 추가 — 6단계, 250~800 LOC

| 단계 | 파일 | 작업 | LOC |
|---|---|---|---|
| 1 | `api/{stock,account}/<feature>.py` | Protocol → `@kis_repr` 클래스 → Base → 국내/해외 impl → `domestic_*`/`foreign_*`/`*` 함수 3층 → scope 바인딩 wrapper | 150~800 |
| 2 | `adapter/{product,account,account_product}/<feature>.py` | Protocol(docstring 복제) + Mixin | 50~240 |
| 3 | `scope/{stock,account}.py` | Protocol 합성 클래스와 구현 클래스 MRO 양쪽에 추가 | 2~3 |
| 4 | `public_types.py` + `__init__.py` | `Foo: TypeAlias = _KisFooResponse` + `__all__` 2곳 | 4~6 |
| 5 | `tests/unit/...` | hermetic 단위 테스트 + `requires_api` 통합 테스트 | 50~150 |
| 6 | docstring + `scripts/generate_api_reference.py` 재생성 + `CHANGELOG.md` | — | — |

**실측**: 단일 시장 신규 TR 1개 → 250~400 LOC. 국내+해외 통합 → 500~800 LOC.
**절반 이상이 Protocol / overload / docstring 중복입니다.**

페이지네이션 API 라면 `KisPaginationAPIResponse` 를 상속하고 `form=[account, page]`,
`continuous=not page.is_first`, `result.is_last` / `next_page` 루프를 씁니다.
`api/account/balance.py` 가 정본입니다.

### 새로운 WebSocket 이벤트 추가 — 5단계

1. **응답 클래스 정의** (`api/websocket/<feature>.py`)
   `__fields__` 를 `^` 분리 **순서 그대로** 나열하고 미사용 필드는 `None` 으로 둡니다.

2. **⚠️ `@register_websocket_response(...)` 데코레이터 부착**

   ```python
   @register_websocket_response("H0STANC0")
   class KisDomesticRealtimeExpectedPrice(KisWebsocketResponse, ...):
       ...
   ```

   > **이 한 줄이 없으면 구독 메시지는 전송되지만 수신 이벤트가 조용히
   > 버려집니다.** dispatch 가 레지스트리를 조회해 없으면 경고 로그만 남기고
   > 드롭합니다. **가장 빠뜨리기 쉬운 단계입니다.**
   >
   > 암호화 TR 이면 `encrypted=True` 를 함께 줍니다. 예전에는 암호화 TR 목록이
   > `client/websocket.py` 에 튜플로 하드코딩돼 있었습니다 ([#17](https://github.com/visualmoney/vm-stock-kis/issues/17)).

3. **`on_xxx` / `on_product_xxx` 구독 함수 작성** — 이벤트 필터 + `client.on(...)`

4. **adapter 확장** — `adapter/websocket/*.py` 의 `on()` 문자열 분기에 추가하고
   Protocol / Mixin 양쪽에 `@overload` 를 답니다. 보일러플레이트가 가장 많은 지점입니다.

5. **새 모듈이면 `api/websocket/__init__.py` 에 import 추가** — 그 import 가
   곧 등록입니다. 모듈이 로드되지 않으면 데코레이터가 실행되지 않습니다.

---

## 성능 최적화

### 1. Rate Limiting

- 초당 요청 제한 자동 관리
- 불필요한 대기 최소화

### 2. Connection Pooling

- `requests.Session` 재사용
- HTTP Keep-Alive

### 3. WebSocket 구독 최적화

- 최대 40개 동시 구독 (KIS 제한)
- 자동 재연결

### 4. 메모리 관리

- GC 기반 이벤트 구독 관리
- Weak reference 활용

---

## 테스트 전략

### 테스트 구조

```text
tests/
├── unit/        # 단위 테스트
├── integration/ # 통합 테스트 (API 호출 필요)
└── fixtures/    # 테스트 데이터
```

### Coverage 목표

- 최소 80% 코드 커버리지
- 핵심 기능 100%

---

## 배포 및 버전 관리

### 빌드 도구

- uv (의존성 관리 및 빌드 프론트엔드)
- hatchling + hatch-vcs (PEP 517 빌드 백엔드, git 태그 기반 버저닝)
- setuptools (배포)
- pytest (테스트)

### 버전 관리

- Semantic Versioning
- GitHub Tags로 자동 버전 관리
- GitHub Actions CI/CD

---

이 문서는 VM-Stock-KIS의 전체 아키텍처를 설명합니다.
더 자세한 정보는 각 모듈별 문서를 참조하세요.
