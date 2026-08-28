# 마이그레이션 가이드 (Migration Guide)

`python-kis` 2.x → `vm-stock-kis` 0.0.1 마이그레이션 가이드입니다.

> **먼저 읽으세요**: **배포명·모듈명·클래스명이 모두 바뀌었습니다.**
> `python-kis`를 쓰고 계셨다면 [1. 이름 변경](#1-이름-변경)이 필수입니다.

---

## 목차

1. [이름 변경](#1-이름-변경)
2. [버전 번호가 낮아지는 이유](#2-버전-번호가-낮아지는-이유)
3. [공개 API 축소](#3-공개-api-축소)
4. [1.0.0 예정 Breaking Changes](#4-100-예정-breaking-changes)
5. [FAQ](#5-faq)

---

## 1. 이름 변경

이 라이브러리는 [Soju06/python-kis](https://github.com/Soju06/python-kis) 2.1.6의
포크입니다. 첫 릴리스에서 포크 고유의 이름 체계로 전환했습니다.

| | `python-kis` 2.x | `vm-stock-kis` 0.0.1 |
|---|---|---|
| PyPI 배포판 | `python-kis` | **`vm-stock-kis`** |
| import 모듈 | `pykis` | **`vmkis`** |
| 공개 클래스 | `PyKis` | **`VmKis`** |
| 환경변수 | `PYKIS_PROFILE`, `PYKIS_CONFIRM_SKIP` | **`VMKIS_PROFILE`, `VMKIS_CONFIRM_SKIP`** |
| 작업공간 | `~/.pykis` | **`~/.vmkis`** |
| User-Agent | `PyKis/x.y.z` | **`VmKis/x.y.z`** |

**배포명과 import 이름이 다릅니다.** 설치는 `vm-stock-kis`, import는 `vmkis`입니다.

### 설치

**`python-kis`를 먼저 제거하세요.** 둘 다 설치된 상태가 가장 흔한 실패 모드입니다.

```bash
pip uninstall python-kis
pip install vm-stock-kis
```

### 코드 변경

```python
# python-kis 2.x
from pykis import PyKis
kis = PyKis("config.yaml")

# vm-stock-kis 0.0.1
from vmkis import VmKis
kis = VmKis("config.yaml")
```

일괄 치환:

```bash
git ls-files '*.py' | xargs sed -i -e 's/PyKis/VmKis/g' -e 's/\bpykis\b/vmkis/g' -e 's/PYKIS_/VMKIS_/g'
```

> Windows PowerShell의 `-replace`는 **대소문자를 무시**하므로 `PyKis`와 `pykis`를
> 구분하지 못합니다. Git Bash의 GNU sed를 쓰세요.

### 하위 호환 폴백 (1.0.0까지)

당장 고치지 않아도 아래 셋은 `DeprecationWarning`과 함께 동작합니다.

| 대상 | 동작 |
|---|---|
| `vmkis.PyKis` | `VmKis`와 **동일 객체**를 반환합니다. `isinstance` 검사도 그대로 동작합니다. |
| `~/.pykis` | `~/.vmkis`가 없고 예전 경로만 있으면 계속 사용합니다 (토큰 캐시 보존). |
| `PYKIS_*` | `VMKIS_*`가 없으면 폴백합니다. |

```python
from vmkis import PyKis   # ❌ 동작하지 않습니다 (__all__에 없음)

import vmkis
kis = vmkis.PyKis(...)    # ✅ 동작합니다 (DeprecationWarning)
```

`from vmkis import PyKis` 형태가 안 되는 것은 의도된 것입니다. `__all__`에 넣으면
`from vmkis import *`가 옛 이름을 계속 퍼뜨립니다.

### `pykis` 호환 패키지는 제공하지 않습니다

`vm-stock-kis` 휠 안에 `pykis/`를 넣으면 업스트림 `python-kis` 배포판과 디스크에서
**파일이 충돌**합니다. 둘 다 설치한 사용자가 한쪽을 uninstall하면 다른 쪽 파일이
지워집니다. Python 패키징에는 `Conflicts:`가 없어 패키지 매니저가 해결할 수 없습니다.

업스트림을 계속 쓰실 분들을 조용히 깨뜨리지 않기 위한 선택입니다.

---

## 2. 버전 번호가 낮아지는 이유

`python-kis` 2.1.6에서 왔는데 `vm-stock-kis` 0.0.1로 갑니다. **다운그레이드가
아닙니다.**

배포명이 다르므로 pip은 두 배포판의 버전을 **비교하지 않습니다.** 서로 다른
패키지이고, 이 이름으로는 이번이 첫 릴리스입니다. 업스트림 번호를 이어받아
3.0.0으로 시작할 수도 있었지만, 그러면 한 번도 게시된 적 없는 배포판이 실제보다
성숙해 보입니다.

```text
python-kis 2.1.6        업스트림. 이 포크의 기점
      │
      │  포크 · 이름 변경 · 버전 재시작
      ▼
vm-stock-kis 0.0.1      이 배포명의 첫 릴리스
      ▼
vm-stock-kis 1.0.0      호환 폴백 완전 제거 + 안정 선언
```

`0.x` 구간에서는 **minor도 Breaking Change 자리**입니다(SemVer 0.y.z).
의존성을 고정할 때 상한을 두세요.

```text
vm-stock-kis>=0.0.1,<1.0.0
```

자세한 내용은 [API_STABILITY_POLICY.md](./guidelines/API_STABILITY_POLICY.md)를
보세요.

---

## 3. 공개 API 축소

포크 이후 루트 `__all__`을 **12개**로 줄였습니다. 내부 Protocol/Mixin은 명시적
경로에서 import합니다.

```python
from vmkis import (
    VmKis, KisAuth,
    Quote, Balance, Order, Chart, Orderbook, MarketInfo, TradingHours,
    SimpleKIS, create_client, save_config_interactive,
)
```

루트에서 사라진 이름은 `DeprecationWarning`과 함께 `vmkis.types`로 위임됩니다.

```python
# ⚠️ 동작하지만 경고 (1.0.0에서 제거)
from vmkis import KisObjectProtocol

# ✅ 권장
from vmkis.types import KisObjectProtocol
from vmkis.adapter.product.quote import KisQuotableProductMixin
```

### 짧은 타입 별칭

`vmkis.public_types`가 긴 내부 이름에 짧은 별칭을 붙입니다. 루트에서도 그대로
import할 수 있습니다.

| 별칭 | 실제 타입 |
|---|---|
| `Quote` | `KisQuoteResponse` |
| `Balance` | `KisIntegrationBalance` |
| `Order` | `KisOrder` |
| `Chart` | `KisChart` |
| `Orderbook` | `KisOrderbook` |
| `MarketInfo` / `MarketType` | `KisMarketType` |
| `TradingHours` | `KisTradingHours` |

```python
from vmkis import Quote, Balance

def analyze(quote: Quote, balance: Balance) -> None:
    print(f"{quote.name}: {quote.price:,}원")
    print(f"예수금: {balance.deposits:,}원")
```

### 초보자용 도구

`create_client`는 설정 파일에서 `VmKis`를 만들어 줍니다.

```python
from vmkis import create_client, save_config_interactive

kis = create_client("config.yaml")
save_config_interactive("config.yaml")   # 대화형 설정 저장
```

`SimpleKIS`는 `VmKis` **인스턴스를 받는** 얇은 파사드입니다. 설정 경로를 직접
받지 않습니다.

```python
from vmkis import SimpleKIS, create_client

simple = SimpleKIS(create_client("config.yaml"))

quote = simple.get_price("005930")
balance = simple.get_balance()
order = simple.place_order("005930", qty=10, price=60000)   # price 생략 시 시장가
```

`SimpleKIS`는 선택 사항입니다. `VmKis`를 그대로 써도 됩니다.

---

## 4. 1.0.0 예정 Breaking Changes

> 아래는 **1.0.0 예정** 사항입니다. 0.0.x에서는 경고만 나옵니다.

### 4.1 이름 호환 폴백 제거

`vmkis.PyKis`, `~/.pykis` 작업공간 폴백, `PYKIS_*` 환경변수 폴백이 제거됩니다.

### 4.2 루트 deprecated import 경로 제거

```python
# ❌ AttributeError
from vmkis import KisObjectProtocol

# ✅
from vmkis.types import KisObjectProtocol
```

### 4.3 `types.py` 역할 정리

`vmkis.types`는 내부 Protocol/고급 타입만 담습니다. 공개 타입은
`vmkis.public_types` 또는 루트에서 가져오세요.

### 지금 확인하는 방법

```bash
python -W error::DeprecationWarning your_script.py
```

경고가 하나도 없으면 1.0.0 대비가 끝난 것입니다.

---

## 5. FAQ

### Q1: 버전이 2.1.6에서 0.0.1로 낮아졌는데 기능이 줄어든 건가요?

**아니요.** 코드베이스는 업스트림 2.1.6에서 이어집니다. 번호는 배포명이 바뀌면서
새로 시작한 것뿐입니다. [2절](#2-버전-번호가-낮아지는-이유)을 보세요.

### Q2: `python-kis`와 `vm-stock-kis`를 같이 설치해도 되나요?

**할 수 있지만 권장하지 않습니다.** 두 배포판은 서로 다른 모듈(`pykis`, `vmkis`)을
설치하므로 파일이 충돌하지는 않습니다. 다만 어느 쪽을 쓰고 있는지 헷갈리기 쉽고,
설정 파일과 토큰 캐시를 공유하지 않습니다.

### Q3: 언제까지 옛 이름을 쓸 수 있나요?

**1.0.0 전까지**입니다. 날짜는 정해져 있지 않습니다. `DeprecationWarning`이 보이면
그때 고쳐 두세요.

### Q4: 업스트림은 계속 유지되나요?

[Soju06/python-kis](https://github.com/Soju06/python-kis)는 별개 프로젝트로
계속됩니다. 이 포크의 이름 변경은 업스트림에 영향을 주지 않습니다. 업스트림
사용자를 깨뜨리지 않으려고 호환 `pykis` 패키지를 배포하지 않는 것도 같은
이유입니다.

### Q5: 테스트 코드도 고쳐야 하나요?

네. 1절의 일괄 치환 명령을 테스트에도 그대로 적용하면 됩니다.

### Q6: 자동 마이그레이션 스크립트가 있나요?

1절의 `sed` 한 줄이 이름 변경 전체를 처리합니다. 별도 스크립트는 제공하지
않습니다. 치환 후 `python -W error::DeprecationWarning`으로 남은 경고를
확인하세요.

---

## 추가 도움

- [GitHub Issues](https://github.com/visualmoney/vm-stock-kis/issues)
- [GitHub Discussions](https://github.com/visualmoney/vm-stock-kis/discussions)
- [문서 홈](./INDEX.md)
- [CHANGELOG](../CHANGELOG.md)

업스트림 프로젝트: [Soju06/python-kis](https://github.com/Soju06/python-kis)

---

**마지막 업데이트**: 2026-08-28
