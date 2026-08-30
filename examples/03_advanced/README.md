# VM-Stock-KIS 고급 예제 (Advanced Examples)

고급 예제는 프로덕션 환경에서 사용되는 실전 기법과 엔터프라이즈급 패턴을 보여줍니다.

## 📚 목록

## 프로파일 사용

설정 파일에 계좌가 둘 이상이면 환경변수 `VMKIS_ACCOUNT` 를 설정하거나 각 스크립트에 `--account <이름>` 을 주세요. 생략하면 설정의 `default_account` 를 씁니다. 이름은 `configs/account_profiles.yaml` 의 `accounts:` 아래 키입니다.

예:

```bash
VMKIS_ACCOUNT=acc_live1 python examples/03_advanced/01_scope_api_trading.py
# 또는
python examples/03_advanced/01_scope_api_trading.py --account acc_paper1
```

### 01_scope_api_trading.py - Scope API를 사용한 심화 거래

**난이도**: ⭐⭐⭐ 고급

**목표**: VmKis의 Scope 기반 API를 직접 사용하여 정교한 거래 구현

**학습 포인트**:

- Stock Scope 객체 사용
- Account Scope 객체 사용
- 복잡한 거래 로직 구현
- Mixin 및 Protocol 활용

**실행**:

```bash
python examples/03_advanced/01_scope_api_trading.py
```

**주요 개념**:

```python
# Stock Scope 사용
stock = kis.stock("005930")
quote = stock.quote()

# Account Scope 사용
account = kis.account()
balance = account.balance()
```

**특징**:

- SimpleKIS보다 훨씬 강력한 API
- 다양한 종목 정보 접근
- 고급 거래 기능 지원

---

### 02_performance_analysis.py - 거래 성과 분석 및 리포팅

**난이도**: ⭐⭐⭐ 고급

**목표**: 거래 기록을 분석하고 성과 리포트 생성

**학습 포인트**:

- 거래 데이터 분석
- 수익률 및 손익 계산
- 성과 지표 도출
- 파일 출력 (JSON, CSV, TXT)

**실행**:

```bash
python examples/03_advanced/02_performance_analysis.py
```

**클래스**: `PerformanceAnalyzer`

- `analyze_trades()` - 거래 분석
- `calculate_metrics()` - 성과 지표 계산
- `generate_report()` - 리포트 생성
- `export_to_json()` / `export_to_csv()` - 데이터 내보내기

**출력 파일**:

```text
performance_report.txt  - 텍스트 리포트
trades.json            - JSON 형식 거래 데이터
trades.csv             - CSV 형식 거래 데이터
```

**성과 지표**:

- 총 손익 (Total Profit)
- 평균 수익률 (Average Return)
- 승률 (Win Rate)
- 최대 수익/손실 (Max Profit/Loss)

---

### 03_error_handling.py - 에러 처리 및 재시도 로직

**난이도**: ⭐⭐⭐⭐ 고급+

**목표**: 프로덕션급 에러 처리 및 복원력 있는 시스템 구축

**학습 포인트**:

- 재시도 로직 (Retry with Exponential Backoff)
- Circuit breaker 패턴
- 로깅 및 모니터링
- 데코레이터 사용

**실행**:

```bash
python examples/03_advanced/03_error_handling.py
```

**클래스**: `ResilientTradingClient`

- `fetch_price()` - 재시도 가능한 가격 조회
- `place_order_safe()` - 안전한 주문 (재시도 + 로깅)
- `monitor_with_circuit_breaker()` - Circuit breaker 모니터링

**주요 패턴**:

#### 1. Retry with Exponential Backoff

```python
# 초기 지연 1초, 매번 2배씩 증가
# 시도: 1초, 2초, 4초, ...

@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def fetch_price(symbol):
    return simple.get_price(symbol)
```

#### 2. Circuit Breaker

```python
# 연속 실패가 임계값을 초과하면 자동 중단
# 예: 3회 연속 실패 시 모니터링 중단

consecutive_failures = 0
max_threshold = 3

if consecutive_failures >= max_threshold:
    logger.critical("Circuit breaker 작동!")
    break
```

#### 3. 로깅

```text
[2025-12-19 14:30:00] INFO: 시도 1/3: fetch_price()
[2025-12-19 14:30:01] WARNING: 시도 1 실패: Connection timeout
[2025-12-19 14:30:01] INFO: 1.0초 후 재시도...
[2025-12-19 14:30:02] INFO: 성공: fetch_price()
```

**출력 파일**:

```text
trading.log - 모든 거래 및 에러 로그
```

---

## 🚀 추천 학습 순서

1. **01_scope_api_trading.py**
   - VmKis 직접 사용 학습
   - Scope 패턴 이해

2. **02_performance_analysis.py**
   - 데이터 분석 기법
   - 리포팅 및 내보내기

3. **03_error_handling.py**
   - 프로덕션급 에러 처리
   - 복원력 있는 설계

---

## 💡 디자인 패턴

### 1. Circuit Breaker 패턴

**언제 사용?**

- 외부 API 호출 중복 실패 방지
- 시스템 리소스 보호
- Cascading failure 예방

**구현**:

```python
consecutive_failures = 0
max_threshold = 3

while True:
    try:
        result = call_external_api()
        consecutive_failures = 0  # 리셋
    except Exception:
        consecutive_failures += 1
        if consecutive_failures >= max_threshold:
            break  # Circuit 열기
```

### 2. Retry with Exponential Backoff

**언제 사용?**

- 일시적 네트워크 오류
- 서버 과부하
- 타임아웃

**구현**:

```python
delay = 1.0
for attempt in range(max_retries):
    try:
        return call_api()
    except Exception:
        time.sleep(delay)
        delay *= 2.0  # 지수적 증가
```

### 3. Decorator for Cross-Cutting Concerns

**언제 사용?**

- 재시도 로직
- 로깅
- 성능 측정

**구현**:

```python
@retry_with_backoff(max_retries=3)
@log_performance()
def fetch_data():
    return api.get()
```

---

## ⚠️ 프로덕션 체크리스트

- [ ] 에러 로깅 설정
- [ ] 재시도 정책 결정
- [ ] Circuit breaker 임계값 설정
- [ ] 타임아웃 값 조정
- [ ] 로그 로테이션 설정
- [ ] 모니터링 대시보드 구축
- [ ] 알림 설정 (이메일, 슬랙 등)
- [ ] 재해 복구 계획

---

## 🔍 트러블슈팅

### 문제: "모든 재시도 실패"

**원인**:

- 네트워크 연결 끊김
- API 서버 다운
- 인증 정보 만료

**해결**:

```python
# 1. 네트워크 확인
ping api.server.com

# 2. 인증 정보 확인
cat configs/account_profiles.yaml

# 3. 로그 확인
tail -f trading.log

# 4. 재시도 정책 조정
@retry_with_backoff(max_retries=5, initial_delay=2.0)
```

### 문제: "Circuit breaker 계속 작동함"

**원인**:

- 재시도 대기 시간 불충분
- 근본 원인 미해결

**해결**:

```python
# 1. 재시도 간격 증가
delay *= 3.0  # 2.0 대신 3.0

# 2. 초기 지연 증가
initial_delay=5.0  # 1.0 대신

# 3. 수동 복구
# 근본 원인 해결 후 재시작
```

---

## 📊 성능 고려사항

### 메모리

```python
# ❌ 나쁜 예: 모든 거래 메모리 보관
trades = []
for i in range(1_000_000):
    trades.append(fetch_trade(i))  # OOM!

# ✅ 좋은 예: 배치 처리
batch_size = 1000
for i in range(0, 1_000_000, batch_size):
    batch = fetch_trades(i, i + batch_size)
    process_batch(batch)
```

### 네트워크

```python
# ❌ 나쁜 예: 순차 요청 (느림)
for symbol in symbols:
    price = fetch_price(symbol)  # 동기

# ✅ 좋은 예: 병렬 요청 (빠름)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    prices = executor.map(fetch_price, symbols)
```

---

## 📖 다음 단계

- VmKis 공식 문서: [링크 필요]
- 한국투자증권 API 가이드
- 고급 거래 전략 학습
- 머신러닝 기반 거래 시스템

---

## 🤝 기여

고급 예제를 개선하거나 새로운 패턴을 추가하고 싶으시면:

1. Fork 또는 Pull Request 제출
2. 엔터프라이즈급 코드 스타일 준수
3. 충분한 테스트 및 문서화

---

**마지막 업데이트**: 2025-12-19
