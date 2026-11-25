# 잔고 반환

호출자가 받는 타입은 프로토콜 `KisBalance` 입니다. 국내·해외·통합 구현이 무엇을 상속하는지는 클래스 선언에 있고, 상속 그림은 [BALANCE_CLASS_DIAGRAM.md](BALANCE_CLASS_DIAGRAM.md) 에 있습니다.

## 누가 무엇을 반환하나

| 함수 | 조건 | 반환 |
|---|---|---|
| `balance` | `country` 생략 | `KisIntegrationBalance` (국내 + `foreign_balance`) |
| `balance` | `country="KR"` | `KisDomesticBalance` |
| `balance` | 그 외 국가 | `KisForeignPresentBalance` |
| `domestic_balance` | | `KisDomesticBalance` |
| `foreign_balance` | | `KisForeignPresentBalance` |
| `_foreign_balance` | | `KisForeignBalance` |

모의투자에서 `foreign_balance` 는 체결기준현재잔고를 받은 뒤, `stocks` 만 `_foreign_balance()` 의 종목(`KisForeignBalanceStock`)으로 바꿉니다. 예수금은 `KisForeignPresentDeposit` 그대로입니다.
