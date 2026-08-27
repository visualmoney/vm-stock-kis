"""
중급 예제 01: 여러 종목 동시 조회 및 비교 분석
VM-Stock-KIS 사용 예제

설명:
  - 여러 종목의 시세를 동시에 조회
  - 수익률 비교 및 정렬
  - 상승/하락 종목 필터링

실행 조건:
  - config.yaml이 루트에 있어야 함
  - 모의투자 모드 권장 (virtual=true)

사용 모듈:
  - VmKis: 한국투자증권 API
  - SimpleKIS: 초보자 친화 인터페이스
"""

import argparse
import os

from vmkis import create_client
from vmkis.simple import SimpleKIS


def analyze_multiple_stocks(config_path: str | None = None, profile: str | None = None) -> None:
    """여러 종목을 조회하고 성과를 분석합니다."""

    # config.yaml에서 설정 로드 및 클라이언트 생성
    config_path = config_path or os.path.join(os.getcwd(), "config.yaml")
    if not os.path.exists(config_path):
        print(f"❌ {config_path}를 찾을 수 없습니다.")
        print("   루트 디렉터리에서 실행하거나 config.yaml을 생성하세요.")
        return

    kis = create_client(config_path, profile=profile)
    simple = SimpleKIS(kis)

    # 분석할 종목 목록
    symbols = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "051910",  # LG화학
        "012330",  # 현대모비스
        "028260",  # 삼성물산
    ]

    print("=" * 70)
    print("VM-Stock-KIS 중급 예제 01: 여러 종목 동시 조회 및 분석")
    print("=" * 70)
    print()

    # 1단계: 여러 종목 정보 조회
    print("📊 단계 1: 종목 정보 조회 중...")
    stocks_data: list[dict] = []

    for symbol in symbols:
        try:
            price = simple.get_price(symbol)
            stocks_data.append(
                {
                    "symbol": symbol,
                    "name": price.name,
                    "price": price.price,
                    "change": price.change,
                    "change_rate": price.change_rate,
                    "volume": price.volume,
                }
            )
            print(f"   ✓ {symbol}: {price.name}")
        except Exception as e:
            print(f"   ✗ {symbol}: {e}")

    print()

    # 2단계: 성과 기반 정렬
    print("📈 단계 2: 성과별 정렬 (수익률)")
    print("-" * 70)

    # 내림차순 정렬 (최고 수익률 먼저)
    sorted_by_rate = sorted(stocks_data, key=lambda x: x["change_rate"], reverse=True)

    for idx, stock in enumerate(sorted_by_rate, 1):
        arrow = "📈" if stock["change_rate"] > 0 else "📉" if stock["change_rate"] < 0 else "➡️"
        print(
            f"{idx}. {stock['symbol']} ({stock['name']:10s}) | "
            f"가격: {stock['price']:>8,}원 | "
            f"변화: {stock['change']:>6,}원 | "
            f"수익률: {arrow} {stock['change_rate']:>6.2f}%"
        )

    print()

    # 3단계: 상승/하락 필터링
    print("🎯 단계 3: 상승/하락 종목 필터링")
    print("-" * 70)

    gainers = [s for s in stocks_data if s["change_rate"] > 0]
    losers = [s for s in stocks_data if s["change_rate"] < 0]

    print(f"📈 상승 종목 ({len(gainers)}개):")
    for stock in sorted(gainers, key=lambda x: x["change_rate"], reverse=True):
        print(f"   • {stock['symbol']}: {stock['change_rate']:+.2f}%")

    print()
    print(f"📉 하락 종목 ({len(losers)}개):")
    for stock in sorted(losers, key=lambda x: x["change_rate"]):
        print(f"   • {stock['symbol']}: {stock['change_rate']:+.2f}%")

    print()

    # 4단계: 통계 계산
    print("📊 단계 4: 통계")
    print("-" * 70)

    if stocks_data:
        avg_rate = sum(s["change_rate"] for s in stocks_data) / len(stocks_data)
        max_rate = max(stocks_data, key=lambda x: x["change_rate"])
        min_rate = min(stocks_data, key=lambda x: x["change_rate"])
        total_volume = sum(s["volume"] for s in stocks_data)

        print(f"평균 수익률: {avg_rate:+.2f}%")
        print(f"최고 수익률: {max_rate['symbol']} ({max_rate['change_rate']:+.2f}%)")
        print(f"최저 수익률: {min_rate['symbol']} ({min_rate['change_rate']:+.2f}%)")
        print(f"총 거래량: {total_volume:,}주")

    print()
    print("✅ 분석 완료!")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--profile", help="config profile name (virtual|real)")
    args = parser.parse_args()

    try:
        analyze_multiple_stocks(config_path=args.config, profile=args.profile)
    except KeyboardInterrupt:
        print("\n🛑 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
