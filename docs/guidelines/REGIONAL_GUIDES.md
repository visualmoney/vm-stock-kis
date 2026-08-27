# 지역별 설정 가이드 (REGIONAL_GUIDES.md)

**작성일**: 2025-12-20
**대상**: 사용자 (한국, 글로벌)
**버전**: v1.0

---

## 개요

VM-Stock-KIS는 **한국 사용자**와 **글로벌 개발자**를 모두 지원합니다. 본 문서는 지역별 특수한 설정과 제약사항을 설명합니다.

---

## 1. 한국 (Korea) - 한국투자증권 고객

### 1.1 환경 설정

#### ✅ 실제 거래 환경 (Real Trading)

**필수 조건**:
- 한국투자증권 계좌 보유
- 앱 키 (App Key) 획득
- 비밀번호 설정

**설정 파일** (`config.yaml`):

```yaml
# 한국 - 실제 거래
kis:
  server: real                    # 실제 서버
  app_key: "YOUR_APP_KEY"
  app_secret: "YOUR_APP_SECRET"
  account_number: "00000000-01"  # 계좌번호 형식

market:
  timezone: "Asia/Seoul"         # 한국 시간대
  holidays:                       # 한국 휴장일
    - "2025-01-01"  # 신정
    - "2025-02-10"  # 설날
    - "2025-03-01"  # 삼일절
    # ... (나머지 휴장일)
  trading_hours:
    - start: "09:00"             # 개장: 9시
      end: "15:30"               # 폐장: 15시 30분
      session: "normal"          # 정규거래
    - start: "15:40"
      end: "16:00"
      session: "after_hours"     # 시간외거래
```

**특수 기능**:
- ✅ 실시간 주문 가능
- ✅ 신용거래 (마진 거래)
- ✅ 공매도 (Short Selling)
- ✅ 선물/옵션 (향후 지원)
- ✅ 한국 증권 전체

**조건**:
- ⚠️ 08:00~15:30만 주문 가능
- ⚠️ 증거금 규제 적용
- ⚠️ 모니터링 대상 종목 제약
- ⚠️ 보호예수 종목 거래 불가

---

#### ⚠️ 테스트 환경 (Virtual/Sandbox)

**목적**: 실제 돈 없이 거래 연습

**설정 파일** (`config_virtual.yaml`):

```yaml
# 한국 - 가상 거래 (시뮬레이션)
kis:
  server: virtual                # 가상 서버
  app_key: "YOUR_VIRTUAL_KEY"
  app_secret: "YOUR_VIRTUAL_SECRET"
  account_number: "00000000-01"

market:
  timezone: "Asia/Seoul"
  initial_balance: 1000000000    # 초기 잔고: 10억

trading:
  allow_short_sell: true          # 공매도 허용
  allow_margin_trading: true      # 신용거래 허용
```

**특징**:
- ✅ 실제 거래 100% 동일한 로직
- ✅ 초기 잔고 설정 가능
- ✅ 손실 위험 없음
- ✅ 24시간 거래 가능 (테스트용)

**제약**:
- ❌ 실제 돈 거래 불가
- ❌ 실제 주가와 다를 수 있음
- ❌ 펀드, ETF 일부 지원 안 함

---

### 1.2 한국 특수 설정

#### 시간대 (Timezone)

```python
# 한국 시간대 (UTC+09:00)
import pytz
from datetime import datetime

tz_korea = pytz.timezone('Asia/Seoul')
now_korea = datetime.now(tz_korea)
print(f"현재 시간: {now_korea}")  # 예: 2025-12-20 14:30:45+09:00
```

#### 휴장일 (Holidays)

```python
# 2025년 한국 증시 휴장일
holidays_2025 = {
    "2025-01-01": "신정",
    "2025-02-10": "설날 연휴",
    "2025-02-11": "설날",
    "2025-02-12": "설날 연휴",
    "2025-03-01": "삼일절",
    "2025-04-09": "국회의원선거일",
    "2025-05-05": "어린이날",
    "2025-05-15": "부처님오신날",
    "2025-06-06": "현충일",
    "2025-08-15": "광복절",
    "2025-09-16": "추석 연휴",
    "2025-09-17": "추석",
    "2025-09-18": "추석 연휴",
    "2025-10-03": "개천절",
    "2025-10-09": "한글날",
    "2025-12-25": "크리스마스",
}

# 거래 불가능한 날 확인
from datetime import date
def is_market_closed(trading_date: date) -> bool:
    date_str = trading_date.strftime("%Y-%m-%d")
    return date_str in holidays_2025
```

#### 통화 (Currency)

```python
# 한국: KRW (원)
quote = kis.stock("005930").quote()  # 삼성전자
print(f"가격: {quote.price:,}원")    # 예: 60,000원
```

---

### 1.3 한국 거래 예제

```python
from vmkis import VmKis

# 1. 클라이언트 초기화
kis = VmKis(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
    account_number="00000000-01",
    server="real"  # 실제 거래
)

# 2. 주식 시세 조회
samsung = kis.stock("005930")  # 삼성전자
quote = samsung.quote()
print(f"삼성전자 현재가: {quote.price:,}원")

# 3. 계좌 잔고 확인
account = kis.account()
balance = account.balance()
print(f"보유금: {balance.cash:,}원")
print(f"평가금: {balance.evaluated_amount:,}원")

# 4. 주식 매수 (유효한 시간대: 09:00~15:30)
order = samsung.buy(quantity=10, price=60000)
print(f"주문 번호: {order.order_id}")

# 5. 주문 조회
orders = account.orders()
for o in orders:
    print(f"주문: {o.symbol} {o.quantity}주 @ {o.price:,}원")
```

---

## 2. 글로벌 (Global) - 해외 개발자

### 2.1 환경 설정

#### ⚠️ 테스트/개발 환경 (Development)

**목적**: 코드 개발 및 테스트 (실제 계정 불필요)

**설정 파일** (`config_dev.yaml`):

```yaml
# 글로벌 - 개발 환경
kis:
  server: mock                   # Mock 서버 (실제 API 미호출)
  app_key: "MOCK_KEY"
  app_secret: "MOCK_SECRET"

mock:
  mode: offline                  # 오프라인 모드
  use_dummy_data: true           # 더미 데이터 사용

development:
  debug: true                    # 디버그 로깅
  log_level: DEBUG
```

**특징**:
- ✅ 실제 API 호출 없음
- ✅ 인터넷 연결 불필요
- ✅ 빠른 테스트 가능
- ✅ 무료 (한계 없음)

**제약**:
- ❌ 실제 데이터가 아님
- ❌ 거래 기능 제한

---

### 2.2 글로벌 설정

#### 시간대 (Timezone)

```python
# 글로벌: UTC 기준 + 지역별 조정
import pytz
from datetime import datetime

# 예시: 미국 동부 시간대
tz_est = pytz.timezone('America/New_York')
now_est = datetime.now(tz_est)
print(f"Current time (EST): {now_est}")

# 예시: 유럽 중앙 시간대
tz_cet = pytz.timezone('Europe/Paris')
now_cet = datetime.now(tz_cet)
print(f"Current time (CET): {now_cet}")
```

#### 통화 환산 (Currency Conversion)

```python
# KRW → USD 환산 (향후 지원)
# 현재는 수동 환산 필요

def krw_to_usd(krw_amount: float, exchange_rate: float = 1.2) -> float:
    """KRW를 USD로 변환 (1 USD = 1,200 KRW 기준)"""
    return krw_amount / exchange_rate

price_krw = 60000
price_usd = krw_to_usd(price_krw, exchange_rate=1200)
print(f"60,000 KRW = ${price_usd:.2f}")  # 약 $50
```

#### 거래 시간 (Market Hours)

```python
# 한국 증시 거래 시간 (글로벌 사용자 기준)

# 한국 09:00~15:30 =
# - 미국 동부: 전날 19:00 ~ 다음날 01:30 (EST)
# - 유럽: 01:00 ~ 07:30 (CET)

from datetime import datetime, timedelta
import pytz

tz_korea = pytz.timezone('Asia/Seoul')
tz_est = pytz.timezone('America/New_York')

# 한국 개장 시간
market_open_korea = tz_korea.localize(datetime(2025, 12, 20, 9, 0))

# EST로 변환
market_open_est = market_open_korea.astimezone(tz_est)
print(f"Market opens in EST: {market_open_est}")
# 출력: 2025-12-19 19:00:00-05:00 (전날 저녁 7시)
```

---

### 2.3 글로벌 개발 예제

```python
# Mock 환경에서 개발 및 테스트
from vmkis import VmKis
from vmkis.mock import MockKisClient

# 1. Mock 클라이언트 생성 (실제 API 미호출)
kis = MockKisClient(
    mode="offline",
    use_dummy_data=True
)

# 2. 더미 데이터로 시세 조회 (Mock)
samsung = kis.stock("005930")
quote = samsung.quote()
print(f"Mock price: {quote.price}")  # 60,000 (더미 데이터)

# 3. 거래 로직 테스트
order = samsung.buy(quantity=10, price=60000)
print(f"Mock order ID: {order.order_id}")

# 4. 단위 테스트
import unittest

class TestVmKis(unittest.TestCase):
    def setUp(self):
        self.kis = MockKisClient(mode="offline")

    def test_quote_fetch(self):
        """주가 조회 테스트"""
        quote = self.kis.stock("005930").quote()
        self.assertGreater(quote.price, 0)

    def test_buy_order(self):
        """매수 주문 테스트"""
        order = self.kis.stock("005930").buy(10, 60000)
        self.assertIsNotNone(order.order_id)

# 5. 실행
if __name__ == '__main__':
    unittest.main()
```

---

## 3. 지역별 비교

### 3.1 기능 비교

| 기능 | 한국 (실제) | 한국 (가상) | 글로벌 (모의) |
|------|-----------|----------|-----------|
| **주식 조회** | ✅ | ✅ | ✅ Mock |
| **실시간 시세** | ✅ | ✅ | ✅ Mock |
| **주문** | ✅ 실제 | ✅ 모의 | ❌ Mock only |
| **신용거래** | ✅ | ✅ | ❌ |
| **선물/옵션** | ⚠️ 예정 | ⚠️ 예정 | ❌ |
| **계좌 관리** | ✅ | ✅ | ❌ |

---

### 3.2 설정 파일 비교

| 설정 | 한국 (실제) | 한국 (가상) | 글로벌 (모의) |
|------|-----------|----------|-----------|
| **서버** | `real` | `virtual` | `mock` |
| **인증** | 실제 키 | 가상 키 | Mock 키 |
| **계좌번호** | 실제 | 가상 | Mock |
| **거래 가능** | Yes | Yes (모의) | No |
| **비용** | 거래 수수료 | 없음 | 없음 |

---

## 4. 거래 시간 가이드

### 4.1 한국 증시 시간표

```
┌─────────────────────────────────────────────┐
│ 한국 증시 거래 시간                          │
├─────────────────────────────────────────────┤
│ 08:00~09:00   │ 시간 전 거래 (현재 미지원)   │
│ 09:00~11:30   │ 오전 거래                   │
│ 11:30~12:30   │ 점심시간                    │
│ 12:30~15:30   │ 오후 거래                   │
│ 15:40~16:00   │ 시간외 거래                 │
│ 16:00~         │ 폐장 (거래 불가)           │
└─────────────────────────────────────────────┘
```

### 4.2 글로벌 시간 변환

```python
# 거래 시간 자동 확인 함수
from datetime import datetime
import pytz

def is_trading_hours(local_tz: str = 'America/New_York') -> bool:
    """
    로컬 시간대에서 한국 증시 거래 중인지 확인
    """
    tz_korea = pytz.timezone('Asia/Seoul')
    tz_local = pytz.timezone(local_tz)

    # 현재 한국 시간
    now_korea = datetime.now(tz_korea)

    # 거래 시간 확인
    hour = now_korea.hour
    minute = now_korea.minute

    # 09:00~15:30 거래
    is_trading = (
        (hour == 9 and minute >= 0) or
        (hour > 9 and hour < 15) or
        (hour == 15 and minute < 30)
    )

    return is_trading, now_korea

# 사용 예
is_trading, now_kr = is_trading_hours('America/New_York')
print(f"한국 시간: {now_kr}")
print(f"거래 중: {'Yes' if is_trading else 'No'}")
```

---

## 5. 문제 해결 (Troubleshooting)

### 5.1 시간대 관련 오류

```
문제: "Market is closed" 에러
원인: 거래 시간 오류 (로컬 시간대 미설정)

해결:
1. 로컬 시간대 확인: timezone 설정
2. 한국 거래 시간 확인: 09:00~15:30 KST
3. 휴장일 확인: holidays 설정
```

### 5.2 통화 관련 오류

```
문제: "Currency mismatch" 에러
원인: KRW (원)가 아닌 다른 통화 사용

해결:
1. 한국은 KRW만 지원
2. USD 가격은 수동 환산
3. 환율 설정 추가 (향후)
```

### 5.3 지역별 권한 오류

```
문제: "Permission denied" 에러
원인: 비한국 사용자가 실제 거래 시도

해결:
1. 한국 계정 필요 (실제 거래)
2. 가상 환경 사용 (테스트)
3. Mock 환경 사용 (개발)
```

---

## 6. 권장사항

### 한국 사용자
```
✅ DO:
- 실제 환경에서 거래
- 보안 키 안전하게 보관
- 거래 시간 확인 후 주문
- 로깅으로 거래 기록 보관

❌ DON'T:
- 다른 사람과 키 공유
- 자동화 거래 (시작 전 충분한 테스트)
- 증거금 100% 사용
- 휴장일에 거래 시도
```

### 글로벌 사용자
```
✅ DO:
- Mock 환경에서 시작
- 가상 환경으로 로직 검증
- 한국 거래 시간 확인
- 커뮤니티 질문 (영어/한국어)

❌ DON'T:
- 실제 환경에 접근 시도 (불가능)
- 실제 계정 없이 거래 시도
- 미지원 기능 사용
```

---

## 7. 참고 자료

- [한국 거래소 공식](http://www.krx.co.kr/) - 휴장일, 거래 시간
- [한국투자증권 공식](https://www.kic.org.kr/) - API 문서
- [World Timezone Database](https://en.wikipedia.org/wiki/Tz_database) - 시간대 정보

---

**마지막 업데이트**: 2025-12-20
**검토 주기**: 분기별 (거래 시간 변경 시 즉시)
**다음 검토**: Q1 2026
