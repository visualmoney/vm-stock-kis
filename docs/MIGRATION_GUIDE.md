# 마이그레이션 가이드 (Migration Guide)

VM-Stock-KIS v2.x → v3.0 마이그레이션 가이드입니다.

---

## 목차

1. [개요](#개요)
2. [v2.2.0 변경사항](#v220-변경사항-202512)
3. [v3.0.0 Breaking Changes](#v300-breaking-changes-예정-20266)
4. [단계별 마이그레이션](#단계별-마이그레이션)
5. [FAQ](#faq)

---

## 개요

### 마이그레이션 타임라인

```
v2.1.7 (현재)
    ↓
v2.2.0 (2025-12) ← Phase 1 완료 ✅
    ↓ (하위 호환성 유지)
v2.3.0 ~ v2.9.x (2026-01 ~ 2026-06)
    ↓ (Deprecation 경고)
v3.0.0 (2026-06+) ← Breaking Changes
```

### 주요 변경사항 요약

| 버전 | 변경 | 영향 | 대응 |
|------|------|------|------|
| v2.2.0 | 공개 API 축소 (154 → 20) | ⚠️ 경고만 | 선택적 업데이트 |
| v2.3.0~v2.9.x | Deprecation 유지 | ⚠️ 경고만 | 권장 업데이트 |
| v3.0.0 | Deprecated 경로 제거 | 🔴 Breaking | 필수 업데이트 |

---

## v2.2.0 변경사항 (2025-12)

### 1. 공개 API 축소

**이전 (v2.1.7)**:
```python
from vmkis import (
    VmKis, KisAuth,
    KisObjectProtocol,
    KisQuotableProductMixin,
    KisOrderableAccountProductMixin,
    # ... 154개 항목
)
```

**현재 (v2.2.0+)**:
```python
# 권장: 일반 사용자
from vmkis import (
    VmKis, KisAuth,
    Quote, Balance, Order, Chart, Orderbook,
    SimpleKIS, create_client,
)

# 고급 사용자 (내부 구조 접근)
from vmkis.types import KisObjectProtocol
from vmkis.adapter.product.quote import KisQuotableProductMixin
```

**변경사항**:
- `src/vmkis/__init__.py`의 `__all__`이 20개로 축소
- 내부 Protocol/Mixin은 `vmkis.types` 및 하위 모듈에서 import
- 기존 import 경로는 `DeprecationWarning`과 함께 동작 (v3.0.0까지 유지)

### 2. 새로운 공개 타입 모듈

**추가된 모듈**: `src/vmkis/public_types.py`

```python
from vmkis.public_types import Quote, Balance, Order

def analyze(quote: Quote, balance: Balance) -> None:
    print(f"{quote.name}: {quote.price:,}원")
    print(f"예수금: {balance.deposits:,}원")
```

**타입 별칭**:
| 별칭 | 실제 타입 | 설명 |
|------|----------|------|
| `Quote` | `KisQuoteResponse` | 시세 정보 |
| `Balance` | `KisIntegrationBalance` | 잔고 정보 |
| `Order` | `KisOrder` | 주문 정보 |
| `Chart` | `KisChart` | 차트 데이터 |
| `Orderbook` | `KisOrderbook` | 호가 정보 |
| `MarketInfo` | `KisMarketInfo` | 시장 정보 |
| `TradingHours` | `KisTradingHours` | 장 시간 정보 |

### 3. 초보자용 도구 추가

**SimpleKIS** (간소화된 API):
```python
from vmkis import SimpleKIS

# Before (기존)
auth = KisAuth(...)
kis = VmKis(auth)
quote = kis.stock("005930").quote()

# After (신규)
simple = SimpleKIS(config_path="config.yaml")
quote = simple.get_price("005930")
balance = simple.get_balance()
```

**헬퍼 함수**:
```python
from vmkis import create_client, save_config_interactive

# 자동 클라이언트 생성
kis = create_client("config.yaml")

# 대화형 설정 저장
save_config_interactive("config.yaml")
```

---

## v3.0.0 Breaking Changes (예정: 2026-06+)

### 1. Deprecated Import 경로 제거

**작동하지 않는 코드 (v3.0.0부터)**:
```python
# ❌ AttributeError 발생
from vmkis import KisObjectProtocol
from vmkis import KisQuotableProductMixin
```

**올바른 코드 (v3.0.0에서 동작)**:
```python
# ✅ 공개 타입 (일반 사용자)
from vmkis import Quote, Balance, Order

# ✅ 내부 구조 (고급 사용자)
from vmkis.types import KisObjectProtocol
from vmkis.adapter.product.quote import KisQuotableProductMixin
```

### 2. `types.py` 역할 변경

**v2.x**:
- `vmkis.types`는 모든 타입을 포함 (공개 + 내부)

**v3.0.0+**:
- `vmkis.types`는 내부 Protocol/고급 타입만 포함
- 공개 타입은 `vmkis.public_types` 또는 `vmkis.__init__`에서 import

---

## 단계별 마이그레이션

### Step 1: v2.2.0으로 업그레이드 (즉시 가능)

```bash
pip install --upgrade vm-stock-kis
```

**확인**:
```python
import vmkis
print(vmkis.__version__)  # 2.2.0 이상
```

### Step 2: Deprecation 경고 확인

**테스트 실행**:
```bash
python -W all your_script.py
```

**경고 예시**:
```
DeprecationWarning: from vmkis import KisObjectProtocol은(는)
deprecated되었습니다. 대신 'from vmkis.types import KisObjectProtocol'을
사용하세요. 이 기능은 v3.0.0에서 제거될 예정입니다.
```

### Step 3: 코드 업데이트

**일반 사용자 (Type Hint만 사용)**:

```python
# Before (v2.1.7)
from vmkis import VmKis, KisAuth, KisQuoteResponse, KisIntegrationBalance

# After (v2.2.0+)
from vmkis import VmKis, KisAuth, Quote, Balance
```

**고급 사용자 (내부 구조 확장)**:

```python
# Before (v2.1.7)
from vmkis import KisObjectProtocol, KisQuotableProductMixin

# After (v2.2.0+)
from vmkis.types import KisObjectProtocol
from vmkis.adapter.product.quote import KisQuotableProductMixin
```

### Step 4: 테스트 및 검증

```bash
# 단위 테스트
pytest tests/

# 타입 체크
mypy your_script.py
```

### Step 5: v3.0.0 대비

**체크리스트**:
- [ ] Deprecation 경고 모두 해결
- [ ] 공개 API (`vmkis.__init__.__all__`)만 사용
- [ ] 내부 모듈은 명시적 경로 사용 (`vmkis.types`, `vmkis.adapter.*`)
- [ ] 테스트 통과 확인

---

## 변경 사항 비교표

### Import 경로 변경

| v2.1.7 | v2.2.0+ | v3.0.0+ | 비고 |
|--------|---------|---------|------|
| `from vmkis import VmKis` | `from vmkis import VmKis` | `from vmkis import VmKis` | 변경 없음 |
| `from vmkis import KisAuth` | `from vmkis import KisAuth` | `from vmkis import KisAuth` | 변경 없음 |
| `from vmkis import KisQuoteResponse` | `from vmkis import Quote` | `from vmkis import Quote` | **별칭 사용** |
| `from vmkis import KisObjectProtocol` | `from vmkis.types import KisObjectProtocol` | `from vmkis.types import KisObjectProtocol` | **경로 변경** |
| `from vmkis import KisQuotableProductMixin` | `from vmkis.adapter.product.quote import KisQuotableProductMixin` | `from vmkis.adapter.product.quote import KisQuotableProductMixin` | **경로 변경** |

### 타입 이름 변경

| v2.1.7 (긴 이름) | v2.2.0+ (짧은 별칭) |
|-----------------|-------------------|
| `KisQuoteResponse` | `Quote` |
| `KisIntegrationBalance` | `Balance` |
| `KisOrder` | `Order` |
| `KisChart` | `Chart` |
| `KisOrderbook` | `Orderbook` |
| `KisMarketInfo` | `MarketInfo` |
| `KisTradingHours` | `TradingHours` |

---

## 자동 마이그레이션 스크립트

### 간단한 치환 스크립트

```python
# scripts/migrate_imports.py
import re
from pathlib import Path

REPLACEMENTS = {
    "from vmkis import KisQuoteResponse": "from vmkis import Quote",
    "from vmkis import KisIntegrationBalance": "from vmkis import Balance",
    "from vmkis import KisOrder": "from vmkis import Order",
    "from vmkis import KisObjectProtocol": "from vmkis.types import KisObjectProtocol",
    # ... 추가
}

def migrate_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")

    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)

    file_path.write_text(content, encoding="utf-8")
    print(f"✅ Migrated: {file_path}")

if __name__ == "__main__":
    for py_file in Path(".").rglob("*.py"):
        migrate_file(py_file)
```

**사용법**:
```bash
python scripts/migrate_imports.py
```

---

## FAQ

### Q1: v2.2.0으로 업그레이드하면 기존 코드가 깨지나요?

**A**: 아니요. v2.2.0은 하위 호환성을 100% 유지합니다. 기존 import 경로는 `DeprecationWarning`과 함께 계속 동작합니다.

### Q2: 언제까지 기존 import 경로를 사용할 수 있나요?

**A**: v2.9.x까지 사용 가능합니다 (약 6개월). v3.0.0부터는 작동하지 않습니다.

### Q3: v3.0.0이 언제 출시되나요?

**A**: 2026년 6월 이후 예정입니다. 충분한 전환 기간이 제공됩니다.

### Q4: 왜 공개 API를 축소했나요?

**A**:
- 초보자가 어떤 것을 import해야 할지 명확하게 하기 위함
- IDE 자동완성 목록이 너무 길었음 (154개 → 20개)
- 내부 구현과 공개 API의 경계를 명확히 하기 위함

### Q5: 고급 사용자도 영향을 받나요?

**A**: 네. 내부 Protocol/Mixin을 사용하는 경우 import 경로를 명시적으로 변경해야 합니다.

```python
# Before
from vmkis import KisObjectProtocol

# After
from vmkis.types import KisObjectProtocol
```

### Q6: 테스트 코드도 업데이트해야 하나요?

**A**: 네. 테스트 코드에서도 동일한 import 경로 변경이 필요합니다.

### Q7: 기존 타입 이름 (`KisQuoteResponse`)을 계속 사용할 수 있나요?

**A**: 가능하지만 권장하지 않습니다. 짧은 별칭 (`Quote`)을 사용하는 것이 더 간결합니다.

```python
# 둘 다 동작 (v2.2.0+)
from vmkis.api.stock.quote import KisQuoteResponse  # 긴 이름
from vmkis import Quote                              # 짧은 별칭 (권장)
```

### Q8: `SimpleKIS`는 필수인가요?

**A**: 아니요. 선택 사항입니다. 기존 `VmKis`를 계속 사용할 수 있습니다. `SimpleKIS`는 초보자를 위한 간소화된 인터페이스입니다.

---

## 추가 도움

- [GitHub Issues](https://github.com/Soju06/python-kis/issues)
- [GitHub Discussions](https://github.com/Soju06/python-kis/discussions)
- [문서 홈](../INDEX.md)

---

**마지막 업데이트**: 2025-12-19
