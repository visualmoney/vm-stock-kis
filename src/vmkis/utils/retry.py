"""Exponential backoff retry 메커니즘

VmKis API 호출 시 일시적 오류(429, 5xx)에 대한 자동 재시도 기능을 제공합니다.
"""

import asyncio
import logging
import random
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from vmkis.client.exceptions import (
    KisConnectionError,
    KisRateLimitError,
    KisServerError,
    KisTimeoutError,
)

__all__ = [
    "with_retry",
    "with_async_retry",
    "retry_config",
]

_logger = logging.getLogger(__name__)

T = TypeVar("T")
P = TypeVar("P")


class RetryConfig:
    """재시도 설정"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """재시도 설정 초기화

        Args:
            max_retries: 최대 재시도 횟수 (기본값: 3)
            initial_delay: 초기 대기 시간(초) (기본값: 1.0)
            max_delay: 최대 대기 시간(초) (기본값: 60.0)
            exponential_base: 지수 기반값 (기본값: 2.0, 1초 → 2초 → 4초 → 8초)
            jitter: 대기 시간에 무작위 값 추가 여부 (기본값: True)
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """재시도 대기 시간 계산

        Args:
            attempt: 현재 시도 횟수 (0부터 시작)

        Returns:
            대기 시간(초)
        """
        # exponential backoff: initial_delay * (base ^ attempt)
        delay = self.initial_delay * (self.exponential_base**attempt)
        delay = min(delay, self.max_delay)

        # jitter: 대기 시간에 ±10% 무작위 값 추가
        if self.jitter:
            jitter_amount = delay * 0.1
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)


# 기본 재시도 설정
retry_config = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
)

# 재시도 가능한 예외
RETRYABLE_EXCEPTIONS = (
    KisRateLimitError,  # 429
    KisServerError,  # 5xx
    KisTimeoutError,  # 타임아웃
    KisConnectionError,  # 연결 오류 (일부)
)


def with_retry(
    max_retries: int | None = None,
    initial_delay: float | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """동기 함수에 재시도 메커니즘을 추가하는 데코레이터

    Args:
        max_retries: 최대 재시도 횟수 (None이면 기본값 사용)
        initial_delay: 초기 대기 시간(초) (None이면 기본값 사용)

    Returns:
        데코레이터 함수

    Example:
        ```python
        @with_retry(max_retries=5, initial_delay=2.0)
        def fetch_data(symbol: str) -> Quote:
            return kis_client.get_quote(symbol)

        # 호출 시 429/5xx 에러 발생 시 자동 재시도
        data = fetch_data("005930")
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            config = retry_config
            if max_retries is not None:
                config.max_retries = max_retries
            if initial_delay is not None:
                config.initial_delay = initial_delay

            last_exception = None
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RETRYABLE_EXCEPTIONS as e:
                    last_exception = e
                    if attempt < config.max_retries:
                        delay = config.calculate_delay(attempt)
                        _logger.warning(
                            f"재시도 가능한 오류 발생: {type(e).__name__}. "
                            f"{delay:.1f}초 후 재시도 ({attempt + 1}/{config.max_retries})"
                        )
                        time.sleep(delay)
                    else:
                        _logger.error(f"최대 재시도 횟수 초과: {type(e).__name__}")

            raise last_exception or RuntimeError("Unknown error")

        return wrapper

    return decorator


def with_async_retry(
    max_retries: int | None = None,
    initial_delay: float | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """비동기 함수에 재시도 메커니즘을 추가하는 데코레이터

    Args:
        max_retries: 최대 재시도 횟수 (None이면 기본값 사용)
        initial_delay: 초기 대기 시간(초) (None이면 기본값 사용)

    Returns:
        데코레이터 함수

    Example:
        ```python
        @with_async_retry(max_retries=5, initial_delay=2.0)
        async def fetch_data(symbol: str) -> Quote:
            return await kis_client.get_quote_async(symbol)

        # 호출 시 429/5xx 에러 발생 시 자동 재시도
        data = await fetch_data("005930")
        ```
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            config = retry_config
            if max_retries is not None:
                config.max_retries = max_retries
            if initial_delay is not None:
                config.initial_delay = initial_delay

            last_exception = None
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except RETRYABLE_EXCEPTIONS as e:
                    last_exception = e
                    if attempt < config.max_retries:
                        delay = config.calculate_delay(attempt)
                        _logger.warning(
                            f"재시도 가능한 오류 발생: {type(e).__name__}. "
                            f"{delay:.1f}초 후 재시도 ({attempt + 1}/{config.max_retries})"
                        )
                        await asyncio.sleep(delay)
                    else:
                        _logger.error(f"최대 재시도 횟수 초과: {type(e).__name__}")

            raise last_exception or RuntimeError("Unknown error")

        return wrapper

    return decorator
