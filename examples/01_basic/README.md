# Basic Examples

이 폴더는 빠른 시작을 위한 최소 예제들을 제공합니다. 모두 `config.yaml` (루트)에서 인증 정보를 로드합니다.

## ⚠️ 준비 (중요)

1. 예제용 설정을 복사하세요. 선택지:
   - 전체 멀티프로파일 예제 사용:

     ```bash
     cp config.example.yaml config.yaml
     ```

   - 가상/실계좌 전용 예제 사용:

     ```bash
     cp config.example.virtual.yaml config.yaml
     # 또는
     cp config.example.real.yaml config.yaml
     ```

2. `config.yaml`에 실제 인증 정보 입력 (각 프로파일 내부에 위치)
   - `id`: HTS 로그인 ID
   - `account`: 계좌번호 (XXXXXXXX-XX)
   - `appkey`: AppKey (36자)
   - `secretkey`: SecretKey (180자)
   - `virtual`: true (모의투자) / false (실계좌)

3. 프로파일 선택 (멀티프로파일 사용 시)
   - 환경변수: `VMKIS_PROFILE=real` 또는 `VMKIS_PROFILE=virtual`
   - 또는 스크립트 인자: `--profile real`
   - 기본값: `virtual` (설정에서 `default`가 있으면 해당 값 사용)

4. **민감정보 보호**: `config.yaml`을 .gitignore에 추가하고 커밋하지 마세요.

   ```bash
   echo "config.yaml" >> .gitignore
   ```

## 예제 목록

- `hello_world.py` — 기본 초기화 및 `stock("005930").quote()` 출력
- `get_quote.py` — 시세 조회 예제 (삼성전자)
- `get_balance.py` — 잔고 조회 예제
- `place_order.py` — 시장가 매수 예제 (안전 장치 포함)
- `realtime_price.py` — 실시간 체결가 구독 예제

## 실행 방법

```bash
# 모의투자 계정에서 먼저 검증 (권장)
python examples/01_basic/get_quote.py
python examples/01_basic/get_balance.py
python examples/01_basic/place_order.py

# 실시간 예제 (Enter를 눌러 종료)
python examples/01_basic/realtime_price.py
```

## 주의사항

- **실계좌 주문**: `ALLOW_LIVE_TRADES=1` 환경변수 필요
- **모의투자 권장**: `config.yaml`에서 `virtual: true` 설정하고 모의투자로 먼저 검증
- **config.yaml 보관**: 절대 GitHub에 커밋하지 마세요
- **실시간 예제**: 종료 시 Enter를 눌러 구독을 해제하세요
