# VM-Stock-KIS 예제 가이드

VM-Stock-KIS는 단계별 학습이 가능하도록 초급, 중급, 고급 예제를 제공합니다.

## 📁 폴더 구조

```text
examples/
├── 01_basic/          # 초급: 기본 사용법
├── 02_intermediate/   # 중급: 실전 거래
├── 03_advanced/       # 고급: 프로덕션 패턴
└── README.md          # 이 파일
```

## 🎯 학습 경로

### 1️⃣ 초급 (01_basic/)

**대상**: VM-Stock-KIS를 처음 사용하는 개발자

**시간**: 1-2시간

**예제**:

- `hello_world.py` - 첫 연결
- `get_quote.py` - 시세 조회
- `get_balance.py` - 잔고 조회
- `place_order.py` - 주문 (모의)
- `realtime_price.py` - 실시간 수가

**학습 목표**:

- 환경 설정 및 인증
- 기본 API 호출
- 데이터 조회
- 기본 거래

**참고**: [01_basic/README.md](01_basic/README.md)

---

### 2️⃣ 중급 (02_intermediate/)

**대상**: 기본 사용법을 익힌 개발자

**시간**: 3-5시간

**예제**:

- `01_multiple_symbols.py` - 여러 종목 분석
- `02_conditional_trading.py` - 자동 거래
- `03_portfolio_analysis.py` - 포트폴리오 분석
- `04_monitoring_dashboard.py` - 실시간 대시보드
- `05_advanced_order_types.py` - 고급 주문

**학습 목표**:

- 복잡한 거래 로직
- 포트폴리오 관리
- 실시간 모니터링
- 다양한 주문 전략

**참고**: [02_intermediate/README.md](02_intermediate/README.md)

---

### 3️⃣ 고급 (03_advanced/)

**대상**: 전문 거래자 및 시스템 개발자

**시간**: 5-8시간

**예제**:

- `01_scope_api_trading.py` - Scope API 활용
- `02_performance_analysis.py` - 성과 분석 및 리포팅
- `03_error_handling.py` - 에러 처리 및 복원력

**학습 목표**:

- VmKis 심화 API
- 성과 분석 및 리포팅
- 프로덕션급 에러 처리
- 엔터프라이즈 패턴

**참고**: [03_advanced/README.md](03_advanced/README.md)

---

## 🚀 시작하기

### 1단계: 환경 준비

```bash
# 저장소 클론
git clone https://github.com/visualmoney/vm-stock-kis.git
cd vm-stock-kis

# 환경 활성화
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 설정 파일 생성 — 템플릿을 복사합니다.
# 제자리에서 고치지 마세요. 템플릿은 추적 대상이라 채우면 시크릿이 커밋됩니다.
cp configs/template_account_profiles.yaml configs/account_profiles.yaml

nano configs/account_profiles.yaml
```

### 2단계: 초급 예제 실행

```bash
# hello_world.py부터 시작
python examples/01_basic/hello_world.py

# 출력:
# Hello from VM-Stock-KIS example!
```

### 3단계: 인증 확인

```bash
# get_quote.py 실행
python examples/01_basic/get_quote.py

# 출력:
# 삼성전자 (005930): 65,000원
```

### 4단계: 중급/고급 예제 진행

```bash
# 여러 종목 분석 (프로파일 선택 예시)
python examples/02_intermediate/01_multiple_symbols.py --profile virtual

# 포트폴리오 분석
python examples/02_intermediate/03_portfolio_analysis.py

# Scope API 사용 (환경변수로도 프로파일 선택 가능)
VMKIS_PROFILE=real python examples/03_advanced/01_scope_api_trading.py
# 또는
python examples/03_advanced/01_scope_api_trading.py --profile real
```

---

## 📋 모든 예제 목록

### 초급 (01_basic/) - 5개

| # | 파일 | 난이도 | 설명 | 시간 |
|---|------|-------|------|------|
| 1 | hello_world.py | ⭐ | 첫 연결 | 5분 |
| 2 | get_quote.py | ⭐ | 시세 조회 | 10분 |
| 3 | get_balance.py | ⭐ | 잔고 조회 | 10분 |
| 4 | place_order.py | ⭐ | 주문 | 15분 |
| 5 | realtime_price.py | ⭐⭐ | 실시간 수가 | 20분 |

**총 시간**: 1시간

### 중급 (02_intermediate/) - 5개

| # | 파일 | 난이도 | 설명 | 시간 |
|---|------|-------|------|------|
| 1 | 01_multiple_symbols.py | ⭐⭐ | 여러 종목 분석 | 30분 |
| 2 | 02_conditional_trading.py | ⭐⭐⭐ | 자동 거래 | 45분 |
| 3 | 03_portfolio_analysis.py | ⭐⭐ | 포트폴리오 분석 | 30분 |
| 4 | 04_monitoring_dashboard.py | ⭐⭐⭐ | 실시간 대시보드 | 45분 |
| 5 | 05_advanced_order_types.py | ⭐⭐⭐ | 고급 주문 | 45분 |

**총 시간**: 3.25시간

### 고급 (03_advanced/) - 3개

| # | 파일 | 난이도 | 설명 | 시간 |
|---|------|-------|------|------|
| 1 | 01_scope_api_trading.py | ⭐⭐⭐ | Scope API | 1시간 |
| 2 | 02_performance_analysis.py | ⭐⭐⭐ | 성과 분석 | 1.5시간 |
| 3 | 03_error_handling.py | ⭐⭐⭐⭐ | 에러 처리 | 2시간 |

**총 시간**: 4.5시간

---

## 💻 실행 방법

### 기본 실행

```bash
python examples/01_basic/hello_world.py
```

### 환경 변수 설정

```bash
# 실계좌 주문 활성화 (주의!)
export ALLOW_LIVE_TRADES=1
python examples/02_intermediate/02_conditional_trading.py

# 로깅 레벨 설정
export LOG_LEVEL=DEBUG
python examples/03_advanced/03_error_handling.py
```

### 모의투자 vs 실계좌

```yaml
# configs/account_profiles.yaml

apps:
  app_paper1:
    mode: "paper"    # ✅ 모의투자 (권장)
  app_live1:
    mode: "live"     # ⚠️ 실계좌 (주의!)
```

`mode` 는 **생략할 수 없습니다.** 빠뜨리면 실전으로 간주하지 않고 실패합니다.

---

## 🔍 트러블슈팅

### "설정 파일을 찾을 수 없습니다"

```bash
ls configs/account_profiles.yaml

# 없으면 템플릿에서 복사
cp configs/template_account_profiles.yaml configs/account_profiles.yaml
nano configs/account_profiles.yaml
```

### "`version` 이 없습니다"

0.0.x 형식 파일입니다. 하위 호환을 지원하지 않으므로 템플릿을 보고 다시 쓰세요.

### "한글이 깨집니다"

**Windows PowerShell**:

```powershell
chcp 65001
```

**Linux/Mac**:

```bash
export LANG=ko_KR.UTF-8
```

### "주문이 실패합니다"

1. 모의투자 모드인지 확인 (`virtual: true`)
2. 잔고 충분한지 확인
3. 거래 시간인지 확인 (평일 09:00-15:30)
4. 네트워크 연결 확인

### "프로그램이 중단됩니다"

```bash
# 로그 확인
tail -f trading.log

# 디버그 모드 실행
python -u examples/01_basic/hello_world.py
```

---

## 📚 추가 리소스

### 공식 문서

- [VM-Stock-KIS 문서](docs/)
- [QUICKSTART.md](../QUICKSTART.md)
- [SimpleKIS 가이드](../docs/SIMPLEKIS_GUIDE.md)

### 참고 자료

- [한국투자증권 API 문서](https://www.kis.co.kr/)
- [거래 시간 및 휴장일](https://finance.naver.com/)
- [Python 공식 문서](https://docs.python.org/)

### 커뮤니티

- GitHub Issues: 버그 보고 및 질문

---

## ✅ 진행 상황 추적

다음 체크리스트를 사용하여 학습 진행 상황을 추적하세요:

### 초급 완료

- [ ] hello_world.py 실행
- [ ] get_quote.py 이해
- [ ] get_balance.py 수정
- [ ] place_order.py (모의) 테스트
- [ ] realtime_price.py 실행

### 중급 완료

- [ ] 01_multiple_symbols.py 이해
- [ ] 02_conditional_trading.py 수정
- [ ] 03_portfolio_analysis.py 실행
- [ ] 04_monitoring_dashboard.py 확장
- [ ] 05_advanced_order_types.py 활용

### 고급 완료

- [ ] 01_scope_api_trading.py 마스터
- [ ] 02_performance_analysis.py 활용
- [ ] 03_error_handling.py 적용

---

## 🎓 다음 단계

1. **자신의 전략 개발**
   - 자신만의 거래 로직 작성
   - 백테스팅 수행
   - 모의투자 검증

2. **자동화 시스템 구축**
   - 스케줄 기반 실행 (cron/scheduler)
   - 알림 설정 (이메일/슬랙)
   - 로깅 및 모니터링

3. **고급 거래 전략**
   - 머신러닝 활용
   - 기술 분석
   - 포트폴리오 최적화

---

## 📝 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🤝 기여

예제를 개선하거나 새로운 예제를 추가하고 싶으시면:

1. Fork
2. 브랜치 생성 (`git checkout -b feature/new-example`)
3. 커밋 (`git commit -m 'Add new example'`)
4. Push (`git push origin feature/new-example`)
5. Pull Request

---

**마지막 업데이트**: 2025-12-19

**버전**: 1.0.0

**상태**: ✅ 모든 예제 작동 확인 완료
