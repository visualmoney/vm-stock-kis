"""
고급 예제 01: VmKis 스코프 API를 사용한 심화 거래
VM-Stock-KIS 사용 예제

설명:
  - VmKis의 Scope 기반 API 사용
  - 주식 조회 및 거래 (스코프)
  - 고급 필터링 및 정렬
  - 복잡한 거래 로직

실행 조건:
  - config.yaml이 루트에 있어야 함
  - 모의투자 모드 권장 (paper=true)

사용 모듈:
  - VmKis: 한국투자증권 API (직접 사용)
"""

import argparse
import os

from vmkis import create_client


def advanced_trading_with_scope(config_path: str | None = None, account: str | None = None) -> None:
    """VmKis Scope API를 사용한 심화 거래"""

    config_path = config_path or os.path.join(os.getcwd(), "config.yaml")
    if not os.path.exists(config_path):
        print(f"❌ {config_path}를 찾을 수 없습니다.")
        return

    # 설정 파일에서 VmKis 클라이언트를 만듭니다. 계좌 이름은 --account 로 고릅니다.
    kis = create_client(config_path, account=account)

    print("=" * 80)
    print("VM-Stock-KIS 고급 예제 01: Scope API를 사용한 심화 거래")
    print("=" * 80)
    print()

    # 1단계: Stock Scope을 사용한 조회
    print("1️⃣ Stock Scope을 사용한 조회")
    print("-" * 80)

    symbol = "005930"  # 삼성전자

    try:
        # Stock Scope 객체 생성
        stock = kis.stock(symbol)

        # 시세 조회 (Scope API)
        quote = stock.quote()
        print(f"종목: {quote.name} ({symbol})")
        print(f"현재가: {quote.price:,}원")
        print(f"등락률: {quote.change_rate:+.2f}%")
        print(f"거래량: {quote.volume:,}주")
        print()

    except Exception as e:
        print(f"❌ 조회 실패: {e}")
        return

    # 2단계: Account Scope을 사용한 거래
    print("2️⃣ Account Scope을 사용한 거래")
    print("-" * 80)

    try:
        # Account Scope 객체 생성
        account = kis.account()

        # 잔고 조회
        balance = account.balance()
        print(f"예수금: {balance.deposits:,}원")
        print(f"총자산: {balance.total_assets:,}원")
        print(f"평가손익: {balance.revenue:,}원 ({balance.revenue_rate:+.2f}%)")
        print()

    except Exception as e:
        print(f"❌ 조회 실패: {e}")

    # 3단계: 복합 거래 시나리오
    print("3️⃣ 복합 거래 시나리오")
    print("-" * 80)

    try:
        # 시나리오: 여러 종목의 수익률 비교
        symbols_to_check = ["005930", "000660", "051910"]

        print(f"모니터링 종목: {', '.join(symbols_to_check)}")
        print()

        results = []
        for sym in symbols_to_check:
            try:
                stock = kis.stock(sym)
                quote = stock.quote()
                results.append(
                    {
                        "symbol": sym,
                        "name": quote.name,
                        "price": quote.price,
                        "change_rate": quote.change_rate,
                    }
                )
                print(f"✓ {sym}: {quote.name} ({quote.price:,}원)")
            except Exception as e:
                print(f"✗ {sym}: {e}")

        print()

        # 수익률 기준 정렬
        if results:
            sorted_results = sorted(results, key=lambda x: x["change_rate"], reverse=True)
            print("📊 수익률 순위:")
            for idx, r in enumerate(sorted_results, 1):
                arrow = "📈" if r["change_rate"] > 0 else "📉"
                print(f"{idx}. {r['symbol']} ({r['name']}): {arrow} {r['change_rate']:+.2f}%")

    except Exception as e:
        print(f"❌ 복합 시나리오 실패: {e}")

    print()
    print("✅ 고급 거래 예제 완료!")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--account", help="쓸 계좌 이름. 생략하면 default_account")
    args = parser.parse_args()

    try:
        advanced_trading_with_scope(config_path=args.config, account=args.account)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
