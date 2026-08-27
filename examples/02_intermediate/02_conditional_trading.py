"""
중급 예제 02: 조건 기반 자동 거래 (실시간 가격 모니터링)
VM-Stock-KIS 사용 예제

설명:
  - 설정한 목표가에 도달하면 자동 매수/매도
  - 실시간 가격 모니터링 (폴링 방식)
  - 거래 조건 및 제약사항 관리

실행 조건:
  - config.yaml이 루트에 있어야 함
  - 모의투자 모드 권장 (virtual=true)
  - 실계좌 주문 시: ALLOW_LIVE_TRADES=1 환경변수 필수

사용 모듈:
  - VmKis: 한국투자증권 API
  - SimpleKIS: 초보자 친화 인터페이스
  - time: 폴링 간격 제어
"""

from vmkis import create_client
from vmkis.simple import SimpleKIS
import time
import os
from datetime import datetime


def monitor_and_trade(config_path: str | None = None, profile: str | None = None) -> None:
    """목표가 도달 시 자동 거래를 수행합니다."""

    # 설정
    config_path = config_path or os.path.join(os.getcwd(), "config.yaml")
    if not os.path.exists(config_path):
        print(f"❌ {config_path}를 찾을 수 없습니다.")
        return

    kis = create_client(config_path, profile=profile)
    simple = SimpleKIS(kis)

    # 거래 설정
    SYMBOL = "005930"  # 삼성전자
    TARGET_BUY_PRICE = 65000  # 목표 매수가
    TARGET_SELL_PRICE = 70000  # 목표 매도가
    ORDER_QTY = 1  # 거래 수량
    POLL_INTERVAL = 5  # 폴링 간격 (초)
    MAX_DURATION = 300  # 최대 모니터링 시간 (초)

    print("=" * 70)
    print("VM-Stock-KIS 중급 예제 02: 조건 기반 자동 거래")
    print("=" * 70)
    print()
    print(f"📋 거래 설정:")
    print(f"   종목: {SYMBOL}")
    print(f"   매수 목표가: {TARGET_BUY_PRICE:,}원")
    print(f"   매도 목표가: {TARGET_SELL_PRICE:,}원")
    print(f"   거래량: {ORDER_QTY}주")
    print(f"   폴링 간격: {POLL_INTERVAL}초")
    print()

    start_time = time.time()
    buy_order_id = None
    buy_price = None
    monitoring = True

    try:
        while monitoring:
            elapsed = time.time() - start_time
            if elapsed > MAX_DURATION:
                print(f"⏱️ {MAX_DURATION}초 모니터링 시간 만료")
                break

            # 현재 가격 조회
            try:
                price = simple.get_price(SYMBOL)
                current_price = price.price
                timestamp = datetime.now().strftime("%H:%M:%S")

                # 상태 표시
                arrow = "📈" if price.change_rate > 0 else "📉" if price.change_rate < 0 else "➡️"
                print(
                    f"[{timestamp}] {arrow} 현재가: {current_price:,}원 "
                    f"(변화: {price.change_rate:+.2f}%) | 거래량: {price.volume:,}"
                )

            except Exception as e:
                print(f"[ERROR] 가격 조회 실패: {e}")
                time.sleep(POLL_INTERVAL)
                continue

            # 매수 조건 확인 (보유 주식 없을 때)
            if buy_order_id is None and current_price <= TARGET_BUY_PRICE:
                print()
                print(f"🤖 매수 조건 만족! (현재가 {current_price:,}원 <= 목표가 {TARGET_BUY_PRICE:,}원)")

                # 실계좌 거래 시 환경변수 확인
                allow_trade = os.environ.get("ALLOW_LIVE_TRADES") == "1"
                if not allow_trade:
                    print(f"⚠️ 모의투자 모드 또는 안전 모드 (ALLOW_LIVE_TRADES 미설정)")

                try:
                    order = simple.place_order(
                        symbol=SYMBOL,
                        side="buy",
                        qty=ORDER_QTY,
                        price=current_price
                    )
                    buy_order_id = order.order_id
                    buy_price = current_price
                    print(f"✅ 매수 주문 완료: {buy_order_id} ({current_price:,}원 x {ORDER_QTY}주)")
                    print()
                except Exception as e:
                    print(f"❌ 매수 주문 실패: {e}")
                    print()

            # 매도 조건 확인 (매수 후)
            if buy_order_id is not None and current_price >= TARGET_SELL_PRICE:
                profit = (current_price - buy_price) * ORDER_QTY
                profit_rate = ((current_price - buy_price) / buy_price) * 100

                print()
                print(f"🤖 매도 조건 만족! (현재가 {current_price:,}원 >= 목표가 {TARGET_SELL_PRICE:,}원)")
                print(f"   수익: {profit:+,}원 ({profit_rate:+.2f}%)")

                try:
                    order = simple.place_order(
                        symbol=SYMBOL,
                        side="sell",
                        qty=ORDER_QTY,
                        price=current_price
                    )
                    print(f"✅ 매도 주문 완료: {order.order_id} ({current_price:,}원 x {ORDER_QTY}주)")
                    print(f"✨ 거래 완료!")
                    monitoring = False
                except Exception as e:
                    print(f"❌ 매도 주문 실패: {e}")
                print()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print()
        print("🛑 사용자가 중단했습니다.")
        if buy_order_id is not None:
            print(f"   미체결 매수 주문: {buy_order_id}")

    print()
    print("✅ 모니터링 종료")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--profile", help="config profile name (virtual|real)")
    args = parser.parse_args()

    try:
        monitor_and_trade(config_path=args.config, profile=args.profile)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
