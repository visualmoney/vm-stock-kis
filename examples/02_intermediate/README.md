# VM-Stock-KIS 중급 예제 (Intermediate Examples)

중급 예제는 실전에서 자주 사용되는 거래 전략과 포트폴리오 관리 기법을 보여줍니다.

## 📚 목록

## 프로파일 사용

설정 파일에 계좌가 둘 이상이면 환경변수 `VMKIS_ACCOUNT` 를 설정하거나 각 스크립트에 `--account <이름>` 을 주세요. 생략하면 설정의 `default_account` 를 씁니다. 이름은 `configs/account_profiles.yaml` 의 `accounts:` 아래 키입니다.

예:

```bash
VMKIS_ACCOUNT=acc_live1 python examples/02_intermediate/01_multiple_symbols.py
# 또는
python examples/02_intermediate/01_multiple_symbols.py --account acc_paper1
```

### 01_multiple_symbols.py - 여러 종목 동시 조회 및 분석

**난이도**: ⭐⭐ 중급

**목표**: 여러 종목의 시세를 한 번에 조회하고 성과를 비교 분석

**학습 포인트**:

- 리스트 기반 종목 조회
- 데이터 정렬 및 필터링
- 수익률 비교 분석
- 통계 계산

**실행**:

```bash
python examples/02_intermediate/01_multiple_symbols.py
```

**출력 예시**:

```text
📊 단계 1: 종목 정보 조회 중...
📈 단계 2: 성과별 정렬 (수익률)
🎯 단계 3: 상승/하락 종목 필터링
📊 단계 4: 통계
```

---

### 02_conditional_trading.py - 조건 기반 자동 거래

**난이도**: ⭐⭐⭐ 중급+

**목표**: 설정한 목표가에 도달하면 자동으로 매수/매도 실행

**학습 포인트**:

- 실시간 가격 모니터링 (폴링)
- 조건 판단 로직
- 자동 주문 실행
- 거래 안전장치

**실행**:

```bash
# 모의투자
python examples/02_intermediate/02_conditional_trading.py

# 실계좌 (주의!)
export ALLOW_LIVE_TRADES=1
python examples/02_intermediate/02_conditional_trading.py
```

**설정 (코드 내 수정 필요)**:

```python
TARGET_BUY_PRICE = 65000   # 목표 매수가
TARGET_SELL_PRICE = 70000  # 목표 매도가
POLL_INTERVAL = 5           # 폴링 간격 (초)
MAX_DURATION = 300          # 최대 모니터링 시간 (초)
```

**출력 예시**:

```text
🤖 매수 조건 만족! (현재가 64,500원 <= 목표가 65,000원)
✅ 매수 주문 완료: ORDER_ID
🤖 매도 조건 만족! (현재가 70,500원 >= 목표가 70,000원)
✅ 매도 주문 완료: ORDER_ID
```

⚠️ **주의**:

- 실계좌에서 실행하지 마세요 (실제 주문 발생!)
- 반드시 모의투자 계좌(앱의 `mode: "paper"`)로 먼저 테스트하세요

---

### 03_portfolio_analysis.py - 포트폴리오 성과 분석

**난이도**: ⭐⭐ 중급

**목표**: 현재 포트폴리오의 성과를 분석하고 시각화

**학습 포인트**:

- 잔고 정보 조회
- 자산 구성 분석
- ROI 계산
- 목표 달성률 추적

**실행**:

```bash
python examples/02_intermediate/03_portfolio_analysis.py
```

**출력 예시**:

```text
💰 예수금:        1,000,000원
📊 총자산:        1,150,000원
📈 평가손익:         150,000원
📊 평가손익률:            15%
```

---

### 04_monitoring_dashboard.py - 실시간 모니터링 대시보드

**난이도**: ⭐⭐⭐ 중급+

**목표**: 여러 종목의 가격을 실시간으로 모니터링하는 대시보드 구축

**학습 포인트**:

- 클래스 기반 설계 (`StockMonitor`)
- 실시간 데이터 갱신
- 상태 표시 (상승/하락/보합)
- 대시보드 UI

**실행**:

```bash
python examples/02_intermediate/04_monitoring_dashboard.py
```

**출력 예시**:

```text
종목       이름         현재가      변화      변화율      고가      저가    상태
005930     삼성전자      65,000     +500      +0.77%    65,500    64,500  📈 상승
000660     SK하이닉스    125,000     -1,000    -0.79%   126,000   124,000  📉 하락
```

**설정 (코드 내 수정 가능)**:

```python
duration = 60  # 모니터링 시간 (초)
interval = 5   # 갱신 간격 (초)
```

---

### 05_advanced_order_types.py - 고급 주문 타입

**난이도**: ⭐⭐⭐ 중급+

**목표**: 지정가, 시장가, 분할 매수 등 다양한 주문 방식 학습

**학습 포인트**:

- 지정가 주문 (limit order)
- 시장가 주문 (market order)
- 분할 매수 전략 (dollar-cost averaging, DCA)
- 손절/익절 설정

**실행**:

```bash
python examples/02_intermediate/05_advanced_order_types.py
```

**클래스**: `AdvancedOrderer`

- `limit_order()` - 지정가 주문
- `market_order()` - 시장가 주문
- `dollar_cost_averaging()` - 분할 매수
- `stop_loss_and_take_profit()` - 손절/익절

---

## 🚀 추천 학습 순서

1. **01_multiple_symbols.py** (기초)
   - 여러 종목 다루기
   - 데이터 처리 기본

2. **03_portfolio_analysis.py** (기초)
   - 포트폴리오 개념 이해
   - 성과 분석

3. **05_advanced_order_types.py** (중급)
   - 다양한 주문 방식
   - 거래 전략 기초

4. **04_monitoring_dashboard.py** (중급)
   - 클래스 설계
   - 실시간 모니터링

5. **02_conditional_trading.py** (중급+)
   - 자동 거래 로직
   - 실무 응용

---

## 💡 팁

### 환경 변수 설정

```bash
# 모의투자 (안전)
export ALLOW_LIVE_TRADES=0  # 또는 설정하지 않음
python examples/02_intermediate/*.py

# 실계좌 (주의!)
export ALLOW_LIVE_TRADES=1
python examples/02_intermediate/*.py
```

### 성능 최적화

여러 종목을 조회할 때는 병렬 처리를 고려하세요:

```python
from concurrent.futures import ThreadPoolExecutor

symbols = ["005930", "000660", "051910"]
with ThreadPoolExecutor(max_workers=3) as executor:
    prices = list(executor.map(simple.get_price, symbols))
```

### 에러 처리

모든 예제는 기본 에러 처리를 포함합니다:

```python
try:
    price = simple.get_price("005930")
except FileNotFoundError:
    print("❌ configs/account_profiles.yaml 이 없습니다.")
except Exception as e:
    print(f"❌ 오류: {e}")
```

---

## ⚠️ 주의사항

### 1. 실계좌 주문 안전

- 모의투자 계좌(앱의 `mode: "paper"`)로 먼저 테스트하세요
- 실계좌에서는 `ALLOW_LIVE_TRADES=1` 필수
- 소액으로 테스트 후 본격 사용

### 2. API 호출 제한

- 너무 빈번한 조회는 rate limiting에 걸릴 수 있음
- `POLL_INTERVAL`을 적절히 조정하세요 (권장: 5초 이상)

### 3. 네트워크 안정성

- 인터넷 연결이 끊어지면 거래가 중단될 수 있음
- 재시작 로직을 추가하세요

### 4. 거래 비용

- 모의투자는 수수료가 없지만 실계좌에서는 발생
- 거래 수익이 수수료를 초과하는지 확인하세요

---

## 📖 다음 단계

고급 예제를 보려면 `examples/03_advanced/`를 참조하세요:

- WebSocket 실시간 연결
- 사용자 정의 거래 전략
- 성능 모니터링

---

## 🤝 기여

예제를 개선하거나 새로운 전략을 추가하고 싶으시면:

1. Fork 또는 Pull Request 제출
2. 코드 스타일 가이드 준수 (PEP 8)
3. 충분한 주석 및 docstring 작성

---

**마지막 업데이트**: 2025-12-19
