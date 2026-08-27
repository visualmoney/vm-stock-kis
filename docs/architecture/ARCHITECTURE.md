# Python KIS - 소프트웨어 아키텍처 문서

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
- **버전**: 2.1.7
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

## 2. 공개 타입 분리 정책 (v2.2.0+)

### 2.1 문제 정의 및 해결

**Phase 1 완료 (2025-12-19)**:
- 154개 → 20개로 공개 API 축소 완료
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

| 버전 | 상태 | 기존 import | 새 import |
|------|------|-------------|-----------|
| v2.2.0 | ✅ 현재 | 동작 (경고) | ✅ 권장 |
| v2.3.0~v2.9.x | 유지보수 | 동작 (경고) | ✅ 권장 |
| v3.0.0 | Breaking | ❌ 제거 | ✅ 필수 |

---

## 핵심 설계 원칙

### 1. 계층화 아키텍처 (Layered Architecture)
```
┌─────────────────────────────────────────┐
│   User Application Layer               │
│   (사용자 애플리케이션)                   │
├─────────────────────────────────────────┤
│   API Layer (Scope + Adapter)           │
│   (주식, 계좌, 실시간 이벤트)             │
├─────────────────────────────────────────┤
│   Client Layer                          │
│   (HTTP 통신, 웹소켓, 인증)              │
├─────────────────────────────────────────┤
│   Response Transform Layer              │
│   (동적 타입 변환, 객체 생성)             │
├─────────────────────────────────────────┤
│   Utility Layer                         │
│   (Rate Limit, 예외, 유틸리티)           │
├─────────────────────────────────────────┤
│   External APIs                         │
│   (KIS REST API, WebSocket)             │
└─────────────────────────────────────────┘
```

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

```
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

```
src/vmkis/
├── __init__.py           # 공개 API 노출
├── __env__.py            # 환경 설정 및 상수
├── kis.py                # VmKis 메인 클래스
├── logging.py            # 로깅 유틸리티
├── types.py              # 공개 타입 정의
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

```
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

```
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

```
src/vmkis/
├── requests (>=2.32.3)
│   └── HTTP 통신
│
├── websocket-client (>=1.8.0)
│   └── WebSocket 실시간 데이터
│
├── cryptography (>=43.0.0)
│   └── 암호화 (비밀키 암호화)
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

```
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

```
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
- 실전: 초당 19개 요청
- 모의: 초당 1개 요청

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

```
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
- 기본값: `~/.vmkis/` 디렉토리에 암호화 저장
- `cryptography` 라이브러리로 암호화
- 신뢰할 수 없는 환경에서는 사용 금지

### 2. 앱키 보호
- 코드에 하드코딩 금지
- 환경 변수 또는 파일 사용
- 깃에 커밋 금지

### 3. WebSocket 보안
- 원본 앱키 대신 WebSocket 접속키 사용
- KIS 권장사항 준수

---

## 확장성 고려사항

### 새로운 API 추가

1. **API 함수 작성** (`api/` 디렉토리)
   ```python
   def get_something(...) -> KisSomething:
       # API 호출
   ```

2. **Response 타입 정의** (`responses/` 디렉토리)
   ```python
   @dataclass
   class KisSomething(KisResponse):
       # 필드 정의
   ```

3. **Adapter Mixin 작성** (필요시)
   ```python
   class KisSomethingMixin:
       def method(self):
           pass
   ```

4. **Scope에 추가**
   ```python
   class KisStock(KisStockScope, KisSomethingMixin):
       pass
   ```

### 새로운 WebSocket 이벤트 추가

1. **WebSocket Response 타입 정의**
2. **구독 함수 작성** (`api/websocket/` 디렉토리)
3. **Adapter Mixin 작성**
4. **Scope에 추가**

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
```
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
- Poetry (의존성 관리)
- setuptools (배포)
- pytest (테스트)

### 버전 관리
- Semantic Versioning
- GitHub Tags로 자동 버전 관리
- GitHub Actions CI/CD

---

이 문서는 VM-Stock-KIS의 전체 아키텍처를 설명합니다.
더 자세한 정보는 각 모듈별 문서를 참조하세요.
