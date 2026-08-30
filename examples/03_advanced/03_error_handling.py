"""
고급 예제 03: 에러 처리 및 재시도 로직
VM-Stock-KIS 사용 예제

설명:
  - 네트워크 오류 처리
  - 재시도 로직 (exponential backoff)
  - 타임아웃 처리
  - 로깅 및 모니터링

실행 조건:
  - configs/account_profiles.yaml 이 있어야 함 (configs/template_account_profiles.yaml 을 복사해 채우세요)

사용 모듈:
  - VmKis: 한국투자증권 API
  - time: 재시도 간격
  - logging: 로깅
"""

import argparse
import logging
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from vmkis import create_client
from vmkis.simple import SimpleKIS

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("trading.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
):
    """
    재시도 데코레이터 (exponential backoff)

    Args:
        max_retries: 최대 재시도 횟수
        initial_delay: 초기 지연 (초)
        backoff_factor: 지수적 증가 인수
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    logger.info(f"시도 {attempt + 1}/{max_retries + 1}: {func.__name__}()")
                    result = func(*args, **kwargs)
                    logger.info(f"성공: {func.__name__}()")
                    return result

                except Exception as e:
                    last_exception = e
                    logger.warning(f"시도 {attempt + 1} 실패: {e}")

                    if attempt < max_retries:
                        logger.info(f"{delay:.1f}초 후 재시도...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"모든 재시도 실패: {e}")

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class ResilientTradingClient:
    """재시도 로직을 포함한 거래 클라이언트"""

    def __init__(self, simple_kis: SimpleKIS):
        self.simple = simple_kis
        self.logger = logger

    @retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
    def fetch_price(self, symbol: str, timeout: float = 10.0) -> Any:
        """
        재시도 로직이 포함된 가격 조회

        Args:
            symbol: 종목 코드
            timeout: 타임아웃 (초)

        Returns:
            가격 정보
        """
        start_time = time.time()

        try:
            # 실제로는 timeout 설정이 필요하지만, SimpleKIS는 기본 제공 안함
            price = self.simple.get_price(symbol)

            elapsed = time.time() - start_time
            self.logger.info(f"가격 조회 완료: {symbol} ({elapsed:.2f}초)")

            return price

        except TimeoutError:
            self.logger.error(f"타임아웃: {symbol} (>{timeout}초)")
            raise

        except ConnectionError as e:
            self.logger.error(f"연결 오류: {e}")
            raise

        except Exception as e:
            self.logger.error(f"예상치 못한 오류: {e}")
            raise

    def place_order_safe(
        self,
        symbol: str,
        side: str,
        qty: int,
        price: int | None = None,
        max_retries: int = 3,
    ) -> bool:
        """
        안전한 주문 (재시도 + 로깅)

        Args:
            symbol: 종목 코드
            side: 'buy' 또는 'sell'
            qty: 수량
            price: 가격 (None이면 시장가)
            max_retries: 최대 재시도 횟수

        Returns:
            성공 여부
        """

        delay = 1.0

        for attempt in range(max_retries + 1):
            try:
                self.logger.info(
                    f"주문 시도 {attempt + 1}/{max_retries + 1}: {side} {symbol} {qty}주 @ {price or '시장가'}"
                )

                order = self.simple.place_order(
                    symbol=symbol,
                    side=side,
                    qty=qty,
                    price=price,
                )

                self.logger.info(f"✅ 주문 성공: {order.order_id}")
                return True

            except Exception as e:
                self.logger.warning(f"주문 실패 (시도 {attempt + 1}): {e}")

                if attempt < max_retries:
                    self.logger.info(f"{delay:.1f}초 후 재시도...")
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    self.logger.error("주문 최종 실패")
                    return False

        return False

    def monitor_with_circuit_breaker(
        self,
        symbol: str,
        max_consecutive_failures: int = 3,
        check_interval: float = 5.0,
    ) -> None:
        """
        Circuit breaker 패턴을 사용한 모니터링

        연속 실패가 임계값을 초과하면 모니터링을 중단합니다.

        Args:
            symbol: 종목 코드
            max_consecutive_failures: 최대 연속 실패 횟수
            check_interval: 확인 간격 (초)
        """

        consecutive_failures = 0

        self.logger.info(f"모니터링 시작: {symbol} (최대 {max_consecutive_failures}회 연속 실패 시 중단)")

        while True:
            try:
                price = self.fetch_price(symbol)
                self.logger.info(f"가격: {symbol} = {price.price:,}원")

                # 성공하면 failure counter 리셋
                consecutive_failures = 0

            except Exception as e:
                consecutive_failures += 1
                self.logger.error(f"조회 실패 ({consecutive_failures}/{max_consecutive_failures}): {e}")

                # Circuit breaker 트리거
                if consecutive_failures >= max_consecutive_failures:
                    self.logger.critical(f"Circuit breaker 작동! 모니터링 중단 ({consecutive_failures} 연속 실패)")
                    break

            time.sleep(check_interval)


def main(config_path: str | None = None, account: str | None = None) -> None:
    """메인 함수"""

    config_path = config_path or os.path.join(os.getcwd(), "configs", "account_profiles.yaml")
    if not os.path.exists(config_path):
        logger.error(f"{config_path}를 찾을 수 없습니다.")
        return

    kis = create_client(config_path, account=account)
    simple = SimpleKIS(kis)

    client = ResilientTradingClient(simple)

    logger.info("=" * 80)
    logger.info("VM-Stock-KIS 고급 예제 03: 에러 처리 및 재시도 로직")
    logger.info("=" * 80)
    logger.info("")

    # 1단계: 재시도 로직 테스트
    logger.info("1️⃣ 재시도 로직 테스트")
    logger.info("-" * 80)

    try:
        price = client.fetch_price("005930")
        logger.info(f"최종 결과: {price.name} = {price.price:,}원")
    except Exception as e:
        logger.error(f"최종 실패: {e}")

    logger.info("")

    # 2단계: 안전한 주문
    logger.info("2️⃣ 안전한 주문 실행")
    logger.info("-" * 80)

    success = client.place_order_safe(
        symbol="005930",
        side="buy",
        qty=1,
        price=65000,
        max_retries=2,
    )

    logger.info(f"주문 결과: {'성공' if success else '실패'}")
    logger.info("")

    # 3단계: Circuit breaker 패턴 (짧은 테스트)
    logger.info("3️⃣ Circuit breaker 패턴 (10초 모니터링)")
    logger.info("-" * 80)

    # 짧은 모니터링 (테스트용)
    import threading

    def monitor_with_timeout():
        client.monitor_with_circuit_breaker(
            symbol="005930",
            max_consecutive_failures=5,
            check_interval=2.0,
        )

    monitor_thread = threading.Thread(target=monitor_with_timeout, daemon=True)
    monitor_thread.start()

    time.sleep(10)  # 10초 후 종료
    logger.info("모니터링 중단")
    logger.info("")

    logger.info("✅ 고급 에러 처리 예제 완료!")
    logger.info("")
    logger.info("📝 로그 파일: trading.log")
    logger.info("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/account_profiles.yaml", help="path to config file")
    parser.add_argument("--account", help="쓸 계좌 이름. 생략하면 default_account")
    args = parser.parse_args()

    try:
        main(config_path=args.config, account=args.account)
    except Exception as e:
        logger.exception(f"❌ 치명적 오류: {e}")
