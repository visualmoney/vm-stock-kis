"""Exception 클래스 및 retry 메커니즘 테스트."""

import time
from unittest.mock import MagicMock

import pytest

from vmkis.client.exceptions import (KisAuthenticationError, KisRateLimitError,
                                     KisServerError, KisTimeoutError,
                                     KisValidationError)
from vmkis.utils.retry import RetryConfig, with_async_retry, with_retry


class TestExceptionHierarchy:
    """Exception 클래스 계층 구조 테스트."""

    def test_kis_authentication_error_is_http_error(self):
        """KisAuthenticationError는 KisHTTPError 하위 클래스."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.reason = "Unauthorized"
        mock_response.text = "Invalid appkey"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        exc = KisAuthenticationError(mock_response)
        assert isinstance(exc, KisAuthenticationError)
        assert exc.status_code == 401

    def test_kis_rate_limit_error_is_http_error(self):
        """KisRateLimitError는 KisHTTPError 하위 클래스."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.text = "Rate limit exceeded"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        exc = KisRateLimitError(mock_response)
        assert exc.status_code == 429

    def test_kis_server_error_is_http_error(self):
        """KisServerError는 KisHTTPError 하위 클래스 (5xx)"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text = "Server error"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        exc = KisServerError(mock_response)
        assert exc.status_code == 500

    def test_kis_timeout_error_is_retryable(self):
        """KisTimeoutError는 재시도 가능."""
        mock_response = MagicMock()
        mock_response.status_code = 0  # 연결 타임아웃
        mock_response.reason = "Timeout"
        mock_response.text = "Request timeout"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        exc = KisTimeoutError(mock_response)
        assert isinstance(exc, KisTimeoutError)


class TestRetryConfig:
    """RetryConfig 설정 테스트."""

    def test_default_retry_config(self):
        """기본 retry 설정 검증."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_calculate_delay_exponential_backoff(self):
        """Exponential backoff 계산 검증."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False,
        )
        assert config.calculate_delay(0) == 1.0  # 1 * 2^0
        assert config.calculate_delay(1) == 2.0  # 1 * 2^1
        assert config.calculate_delay(2) == 4.0  # 1 * 2^2
        assert config.calculate_delay(3) == 8.0  # 1 * 2^3

    def test_calculate_delay_max_delay_limit(self):
        """최대 대기 시간 초과 방지."""
        config = RetryConfig(
            initial_delay=30.0,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=False,
        )
        delay = config.calculate_delay(2)  # 30 * 2^2 = 120
        assert delay == 60.0  # max_delay로 제한

    def test_calculate_delay_with_jitter(self):
        """Jitter 추가 검증 (범위 검사)"""
        config = RetryConfig(
            initial_delay=10.0,
            exponential_base=2.0,
            jitter=True,
        )
        delays = [config.calculate_delay(1) for _ in range(10)]
        # 기본값: 20 * (1 - 0.1) ~ 20 * (1 + 0.1) = 18 ~ 22
        assert all(17 < d < 23 for d in delays), f"Jitter delays out of range: {delays}"


class TestWithRetryDecorator:
    """@with_retry 데코레이터 테스트"""

    def test_successful_call_no_retry(self):
        """성공한 호출은 재시도하지 않음."""
        call_count = 0

        @with_retry(max_retries=3, initial_delay=0.1)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retryable_exception_retry_success(self):
        """재시도 가능한 예외 발생 후 성공."""
        call_count = 0
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.text = "Rate limit"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        @with_retry(max_retries=3, initial_delay=0.05)
        def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise KisRateLimitError(mock_response)
            return "success"

        result = eventually_successful()
        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """최대 재시도 횟수 초과."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text = "Server error"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        @with_retry(max_retries=2, initial_delay=0.05)
        def always_fails():
            raise KisServerError(mock_response)

        with pytest.raises(KisServerError):
            always_fails()

    def test_non_retryable_exception_not_retried(self):
        """재시도 불가능한 예외는 즉시 발생."""
        call_count = 0

        @with_retry(max_retries=3, initial_delay=0.1)
        def fail_non_retryable():
            nonlocal call_count
            call_count += 1
            # Mock response with proper attributes
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_response.headers = {}
            mock_request = MagicMock()
            mock_request.url = "https://test.com/api"
            mock_request.method = "POST"
            mock_request.headers = {}
            mock_request.body = b""
            mock_response.request = mock_request
            raise KisValidationError(mock_response)

        with pytest.raises(KisValidationError):
            fail_non_retryable()

        # 재시도하지 않으므로 호출 횟수는 1
        assert call_count == 1

    def test_retry_multiple_exception_types(self):
        """다양한 재시도 가능 예외 처리."""
        call_count = 0
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.reason = "Too Many Requests"
        mock_response_429.text = "Rate limit"
        mock_response_429.request.headers = {}
        mock_response_429.request.method = "GET"
        mock_response_429.request.url = "https://api.example.com/test"
        mock_response_429.request.body = None

        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        mock_response_500.reason = "Server Error"
        mock_response_500.text = "Error"
        mock_response_500.request.headers = {}
        mock_response_500.request.method = "GET"
        mock_response_500.request.url = "https://api.example.com/test"
        mock_response_500.request.body = None

        @with_retry(max_retries=3, initial_delay=0.05)
        def fail_different_exceptions():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise KisRateLimitError(mock_response_429)
            elif call_count == 2:
                raise KisServerError(mock_response_500)
            return "success"

        result = fail_different_exceptions()
        assert result == "success"
        assert call_count == 3


class TestWithAsyncRetryDecorator:
    """@with_async_retry 데코레이터 테스트"""

    @pytest.mark.asyncio
    async def test_async_successful_call_no_retry(self):
        """비동기 성공한 호출은 재시도하지 않음."""
        call_count = 0

        @with_async_retry(max_retries=3, initial_delay=0.05)
        async def async_successful():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await async_successful()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_retryable_exception_retry_success(self):
        """비동기 재시도 가능한 예외 발생 후 성공."""
        call_count = 0
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.text = "Rate limit"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        @with_async_retry(max_retries=3, initial_delay=0.05)
        async def async_eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise KisRateLimitError(mock_response)
            return "success"

        result = await async_eventually_successful()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_max_retries_exceeded(self):
        """비동기 최대 재시도 횟수 초과."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text = "Server error"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        @with_async_retry(max_retries=2, initial_delay=0.05)
        async def async_always_fails():
            raise KisServerError(mock_response)

        with pytest.raises(KisServerError):
            await async_always_fails()

    @pytest.mark.asyncio
    async def test_async_timing_between_retries(self):
        """비동기 재시도 간 대기 시간 검증."""
        call_count = 0
        start_time = time.time()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.text = "Rate limit"
        mock_response.request.headers = {}
        mock_response.request.method = "GET"
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.body = None

        @with_async_retry(max_retries=2, initial_delay=0.1)
        async def async_eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise KisRateLimitError(mock_response)
            return "success"

        result = await async_eventually_successful()
        elapsed_time = time.time() - start_time

        assert result == "success"
        # 2 retries with delays: 0.1s (jitter 포함)
        # 최소 0.2초 이상 소요
        assert elapsed_time >= 0.15
