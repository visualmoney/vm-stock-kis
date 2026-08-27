# QUICKSTART

1. 설치

```bash
pip install vm-stock-kis
```

2. 인증 정보 준비 (권장: 외부 파일 사용, 리포지토리에 커밋 금지)

`config.yaml` 예시:

```yaml
id: "YOUR_HTS_ID"
account: "00000000-01"
appkey: "YOUR_APPKEY"
secretkey: "YOUR_SECRET"
virtual: false
```

3. 코드 예시 (config.yaml 사용)

```python
import yaml
from vmkis import VmKis

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

kis = VmKis(id=cfg["id"], account=cfg["account"], appkey=cfg["appkey"], secretkey=cfg["secretkey"])
print(kis.stock("005930").quote())
```

4. 테스트 팁

- 테스트에서는 `tmp_path`에 임시 `config.yaml`을 생성하거나 `monkeypatch.setenv`를 사용하세요.

---

5. 다음 단계

- 예제 실행: `examples/01_basic/` 폴더의 스크립트를 그대로 실행해보세요.
- README 살펴보기: 루트 `README.md`에 설치/주문/실시간 예제가 더 있습니다.
- 설정 분리: 실계좌 주문 전 `virtual: true`로 모의투자에서 먼저 검증하세요.

6. 트러블슈팅

- `FileNotFoundError: config.yaml`: 루트에 `config.yaml`이 있는지 확인하고, 작업 디렉터리를 루트로 맞추세요.
- 한글 깨짐: PowerShell/터미널 인코딩을 UTF-8로 설정 (`chcp 65001`).
- 실계좌 주문 차단: `ALLOW_LIVE_TRADES=1` 환경 변수를 설정하지 않으면 `place_order.py` 예제가 실계좌에서 중단됩니다.

7. FAQ

- Q: 환경변수로도 설정 가능한가요?
    A: 가능합니다. `os.environ`에서 불러와 `VmKis`에 전달하면 됩니다.
- Q: 예제 실행 순서는?
    A: `hello_world.py` → `get_quote.py` → `get_balance.py` → `place_order.py`(모의) → `realtime_price.py` 순으로 권장합니다.
