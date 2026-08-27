"""
통합 테스트 - Rate Limit 준수 확인

대량 요청 시 Rate Limiting이 올바르게 작동하는지 확인합니다.
"""

import time
from datetime import datetime, timedelta

import pytest
import requests_mock

from vmkis import KisAuth, VmKis
from vmkis.__env__ import VIRTUAL_API_REQUEST_PER_SECOND
from vmkis.utils.rate_limit import RateLimiter
from vmkis.utils.timezone import TIMEZONE


@pytest.fixture
def mock_auth():
    """테스트용 인증 정보 (실전 도메인)"""
    return KisAuth(
        id="test_user",
        account="50000000-01",
        appkey="P" + "A" * 35,
        secretkey="S" * 180,
        virtual=False,
    )


@pytest.fixture
def mock_virtual_auth():
    """테스트용 모의 인증 정보."""
    return KisAuth(
        id="test_user",
        account="50000000-01",
        appkey="P" + "A" * 35,
        secretkey="S" * 180,
        virtual=True,
    )


@pytest.fixture
def mock_token_response():
    """토큰 발급 응답.

    만료 시각은 **반드시 현재 시각 기준 상대값**이어야 한다. 고정 날짜를 쓰면
    그 날짜가 지나는 순간 토큰이 항상 만료 상태가 되고, `VmKis.primary_token`이
    `remaining < 10분` 조건에 걸려 **매 요청마다 토큰을 재발급**한다.
    토큰 발급도 `VmKis.request()`를 타므로 같은 rate limiter 쿼터를 소비해,
    유량 제한 테스트의 소요 시간이 조용히 2배가 된다.

    실제로 이 픽스처는 `"2025-12-31 23:59:59"`로 고정되어 있었고 그 날짜가 지난 뒤
    `test_concurrent_requests_respect_limit`이 5초 대신 9.47초를 기록하며 실패했다.
    https://github.com/visualmoney/vm-stock-kis/issues/3
    """
    validity_period = 86400
    expired_at = datetime.now(TIMEZONE) + timedelta(seconds=validity_period)

    return {
        "access_token": "test_token_12345",
        "access_token_token_expired": expired_at.strftime("%Y-%m-%d %H:%M:%S"),
        "token_type": "Bearer",
        "expires_in": validity_period,
    }


# https://apiportal.koreainvestment.com/community/10000000-0000-0011-0000-000000000001/post/eb3e2dcb-3d52-4ff1-9eb2-c09b1c880fb2
# appkey 당 REST 20건/초, WebSocket 41건 구독


class TestRateLimitCompliance:
    """Rate Limit 준수 확인 통합 테스트."""

    def test_rate_limit_enforced_on_api_calls(self, mock_auth, mock_virtual_auth, mock_token_response):
        """전체 테스트를 실제로 돌리지 않고 기본 구조만 확인."""
        # 실제로 호출하지 않으므로 기본적인 VmKis 초기화만 테스트
        with requests_mock.Mocker() as m:
            # 토큰 발급 - real 도메인
            m.post("https://openapi.koreainvestment.com:9443/oauth2/tokenP", json=mock_token_response)

            # 토큰 발급 - virtual 도메인
            m.post("https://openapivts.koreainvestment.com:29443/oauth2/tokenP", json=mock_token_response)

            # API 응답
            m.get(requests_mock.ANY, json={"rt_cd": "0", "output": {}})

            kis = VmKis(mock_auth, mock_virtual_auth, use_websocket=False)

            # Rate limiter가 설정되어 있는지 확인
            assert kis._rate_limiters is not None
            assert "virtual" in kis._rate_limiters
            assert kis._rate_limiters["virtual"].rate == 2  # 모의투자: 초당 2개

    def test_rate_limit_real_vs_virtual(self):
        """실전과 모의투자 Rate Limit 차이."""
        # 실전: 초당 19개 (rate=19, period=1.0)
        real_limiter = RateLimiter(rate=19, period=1.0)

        # 모의: 초당 1개 (rate=1, period=1.0)
        virtual_limiter = RateLimiter(rate=1, period=1.0)

        # 실전은 빠름
        start = time.time()
        for _ in range(19):
            real_limiter.acquire()
        real_elapsed = time.time() - start

        assert real_elapsed < 1.0

        # 모의는 느림
        start = time.time()
        for _ in range(5):
            virtual_limiter.acquire()
        virtual_elapsed = time.time() - start

        assert virtual_elapsed >= 4.0

    def test_concurrent_requests_respect_limit(self, mock_auth, mock_virtual_auth, mock_token_response):
        """동시 요청도 Rate Limit 준수."""
        from threading import Thread

        with requests_mock.Mocker() as m:
            m.post("https://openapi.koreainvestment.com:9443/oauth2/tokenP", json=mock_token_response)
            m.post("https://openapivts.koreainvestment.com:29443/oauth2/tokenP", json=mock_token_response)

            m.get(requests_mock.ANY, json={"rt_cd": "0", "output": {}})

            kis = VmKis(mock_auth, mock_virtual_auth, use_websocket=False)

            request_count = 10
            errors = []

            def make_request(index):
                try:
                    kis.request(
                        f"/test/api/{index}",
                        method="GET",
                        domain="virtual",
                    )
                except Exception as error:  # noqa: BLE001 - 스레드 밖으로 전달해 단언한다
                    errors.append(error)

            start_time = time.time()

            threads = [Thread(target=make_request, args=(i,)) for i in range(request_count)]

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            elapsed = time.time() - start_time

            assert not errors, f"요청 중 예외가 발생했습니다: {errors}"

            # 토큰 발급도 VmKis.request()를 타므로 동일한 rate limiter 쿼터를 쓴다.
            # 따라서 유량을 획득한 횟수는 (토큰 발급 + API 요청)이다.
            token_issues = sum(1 for r in m.request_history if "token" in r.path)
            acquisitions = len(m.request_history)

            # 토큰이 매 요청마다 재발급되면 쿼터 소비가 2배가 되어 소요 시간도 2배가 된다.
            # 시간 단언보다 이쪽이 원인을 훨씬 정확히 짚는다.
            assert token_issues == 1, f"토큰은 1회만 발급되어야 합니다. 실제 {token_issues}회"
            assert acquisitions == request_count + 1

            # RateLimiter(rate, period=1)는 rate회까지 즉시 통과시키고 그 다음 획득마다
            # 한 주기를 대기한다. 즉 N회 획득 시 대기 횟수는 (N - 1) // rate 이다.
            expected_waits = (acquisitions - 1) // VIRTUAL_API_REQUEST_PER_SECOND
            minimum_elapsed = expected_waits * 1.0

            # 하한만 엄격하게 본다. 유량 제한이 없으면 이 구간은 사실상 0초로 끝나므로
            # 하한이 곧 "제한이 실제로 걸렸는가"에 대한 검증이다.
            assert elapsed >= minimum_elapsed, (
                f"유량 제한이 걸리지 않았습니다. {acquisitions}회 획득 시 "
                f"최소 {minimum_elapsed:.1f}초가 기대되나 {elapsed:.2f}초 소요"
            )

            # 상한은 느린 머신을 감안해 넉넉히 둔다. 쿼터가 새는 회귀는 위의
            # acquisitions 단언이 시간과 무관하게 잡아낸다.
            assert elapsed <= minimum_elapsed + 5.0, f"과도하게 오래 걸렸습니다: {elapsed:.2f}초"

    def test_rate_limit_error_handling(self):
        """에러 발생 시 Rate Limit 처리 - 기본 동작 확인"""
        limiter = RateLimiter(rate=5, period=1.0)

        # 성공 5번
        for _ in range(5):
            limiter.acquire()

        # 5번 더 호출하면 대기해야 함
        start = time.time()
        for _ in range(5):
            limiter.acquire()
        elapsed = time.time() - start

        # 대기 시간이 있어야 함 (약 1초)
        assert elapsed >= 0.9

    def test_rate_limit_burst_then_throttle(self):
        """초기 버스트 후 throttle."""
        limiter = RateLimiter(rate=10, period=1.0)

        start_time = time.time()
        request_times = []

        # 30개 요청
        for _ in range(30):
            limiter.acquire()
            request_times.append(time.time() - start_time)

        # 처음 10개는 빠름 (<0.5초)
        assert all(t < 0.5 for t in request_times[:10])

        # 그 다음부터는 throttle
        # 11-20번째: 1초 ~ 2초 사이
        assert all(1.0 <= t < 2.5 for t in request_times[10:20])

        # 21-30번째: 2초 ~ 3초 사이
        assert all(2.0 <= t < 3.5 for t in request_times[20:30])

    def test_rate_limit_with_variable_intervals(self):
        """가변 간격으로 요청."""
        limiter = RateLimiter(rate=5, period=1.0)

        timestamps = []

        # 요청 사이사이 0.3초 대기
        for i in range(10):
            limiter.acquire()
            timestamps.append(time.time())

            if i < 9:  # 마지막은 대기 안 함
                time.sleep(0.3)

        # 전체 시간 계산
        total_time = timestamps[-1] - timestamps[0]

        # 10개 요청, 초당 5개 = 2초 + 대기시간(0.3 * 9 = 2.7초) = 약 4.7초
        # 하지만 대기 중에 시간이 지나가므로 실제로는 더 짧을 수 있음
        assert 2.5 <= total_time <= 5.0


class TestRateLimitMonitoring:
    """Rate Limit 모니터링 테스트."""

    def test_rate_limit_count_tracking(self):
        """카운트 추적."""
        limiter = RateLimiter(rate=10, period=1.0)

        # 5번 성공
        for _ in range(5):
            limiter.acquire()

        assert limiter.count == 5

    def test_rate_limit_remaining_capacity(self):
        """남은 용량 확인."""
        limiter = RateLimiter(rate=10, period=1.0)

        # 7번 요청
        for _ in range(7):
            limiter.acquire()

        assert limiter.count == 7

        # 3개 더 즉시 가능해야 함
        start = time.time()
        for _ in range(3):
            limiter.acquire()
        elapsed = time.time() - start

        assert elapsed < 0.1  # 거의 즉시

    def test_rate_limit_blocking_callback(self):
        """블로킹 콜백 호출 확인."""
        callback_calls = []

        def callback():
            callback_calls.append(time.time())

        limiter = RateLimiter(rate=2, period=1.0)

        # 3번 요청
        for _ in range(3):
            limiter.acquire(blocking=True, blocking_callback=callback)

        # 3번째 요청에서 콜백 호출되어야 함
        assert len(callback_calls) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
