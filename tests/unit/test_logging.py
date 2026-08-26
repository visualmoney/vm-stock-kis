"""로깅 시스템 테스트"""

import json
import logging
from io import StringIO

import pytest

from pykis import logging as pykis_logging
from pykis.logging import (
    JsonFormatter,
    disable_json_logging,
    enable_json_logging,
    get_logger,
    logger,
    setLevel,
)


class TestLoggingLevel:
    """로깅 레벨 설정 테스트"""

    def test_set_level_with_string(self):
        """문자열 로그 레벨 설정"""
        setLevel("DEBUG")
        assert logger.level == logging.DEBUG

        setLevel("INFO")
        assert logger.level == logging.INFO

        setLevel("WARNING")
        assert logger.level == logging.WARNING

        setLevel("ERROR")
        assert logger.level == logging.ERROR

        setLevel("CRITICAL")
        assert logger.level == logging.CRITICAL

    def test_set_level_with_int(self):
        """정수 로그 레벨 설정"""
        setLevel(logging.DEBUG)
        assert logger.level == logging.DEBUG

        setLevel(logging.INFO)
        assert logger.level == logging.INFO

    def test_set_level_invalid_string(self):
        """유효하지 않은 로그 레벨 문자열"""
        with pytest.raises(ValueError):
            setLevel("INVALID")  # type: ignore


class TestJsonFormatter:
    """JSON 포매터 테스트"""

    def test_format_basic_record(self):
        """기본 로그 레코드 JSON 포매팅"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="pykis.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "INFO"
        assert data["logger"] == "pykis.test"
        assert data["message"] == "Test message"
        assert data["line"] == 42
        assert "timestamp" in data
        assert "module" in data

    def test_format_record_with_exception(self):
        """예외 정보를 포함한 로그 레코드"""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            record = logging.LogRecord(
                name="pykis.test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=50,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info(),
            )

            result = formatter.format(record)
            data = json.loads(result)

            assert data["level"] == "ERROR"
            assert "exception" in data
            assert data["exception"]["type"] == "ValueError"
            assert "Test error" in data["exception"]["message"]

    def test_format_record_with_context(self):
        """추가 컨텍스트 데이터를 포함한 로그 레코드"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="pykis.api",
            level=logging.WARNING,
            pathname="api.py",
            lineno=100,
            msg="Rate limit warning",
            args=(),
            exc_info=None,
        )
        record.context = {  # type: ignore
            "transaction_id": "TR123456",
            "retry_count": 2,
        }

        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "WARNING"
        assert data["context"]["transaction_id"] == "TR123456"
        assert data["context"]["retry_count"] == 2


class TestGetLogger:
    """서브 로거 획득 테스트"""

    def test_get_child_logger(self):
        """자식 로거 획득"""
        child_logger = get_logger("pykis.api")
        assert child_logger.name == "pykis.api"

    def test_get_multiple_child_loggers(self):
        """여러 자식 로거 획득"""
        api_logger = get_logger("pykis.api")
        client_logger = get_logger("pykis.client")

        assert api_logger.name == "pykis.api"
        assert client_logger.name == "pykis.client"
        assert api_logger is not client_logger


class TestJsonLoggingToggle:
    """JSON 로깅 활성화/비활성화 테스트"""

    def test_enable_json_logging(self):
        """JSON 로깅 활성화"""
        enable_json_logging()

        # 핸들러가 JsonFormatter를 사용하는지 확인
        assert len(logger.handlers) > 0
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, JsonFormatter)

    def test_disable_json_logging(self):
        """JSON 로깅 비활성화"""
        enable_json_logging()
        disable_json_logging()

        # 핸들러가 ColoredFormatter를 사용하는지 확인
        assert len(logger.handlers) > 0
        handler = logger.handlers[0]
        # ColoredFormatter는 logging.Formatter의 서브클래스
        assert handler.formatter is not None

    def test_toggle_json_logging_multiple_times(self):
        """JSON 로깅 활성화/비활성화 반복"""
        for _ in range(3):
            enable_json_logging()
            assert isinstance(logger.handlers[0].formatter, JsonFormatter)

            disable_json_logging()
            assert logger.handlers[0].formatter is not None


class TestLoggingIntegration:
    """로깅 통합 테스트"""

    def test_logger_output_format(self, capsys):
        """로거 출력 형식 검증"""
        setLevel("INFO")

        logger.info("Test info message")
        captured = capsys.readouterr()

        assert "Test info message" in captured.out
        assert "INFO" in captured.out

    def test_json_logger_output_format(self, capsys):
        """JSON 로거 출력 형식 검증"""
        enable_json_logging()
        setLevel("INFO")

        logger.info("Test JSON message")
        captured = capsys.readouterr()

        try:
            data = json.loads(captured.out.strip())
            assert data["message"] == "Test JSON message"
            assert data["level"] == "INFO"
        finally:
            disable_json_logging()

    def test_logger_filtering_by_level(self, capsys):
        """로깅 레벨에 따른 필터링"""
        setLevel("WARNING")

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        captured = capsys.readouterr()

        assert "Debug message" not in captured.out
        assert "Info message" not in captured.out
        assert "Warning message" in captured.out


@pytest.mark.parametrize(
    ("level_input", "expected_level"),
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
        (logging.DEBUG, logging.DEBUG),
        (logging.INFO, logging.INFO),
        (logging.WARNING, logging.WARNING),
        (logging.ERROR, logging.ERROR),
        (logging.CRITICAL, logging.CRITICAL),
    ],
)
def test_set_level(level_input, expected_level):
    """setLevel 함수가 로거 레벨을 올바르게 설정하는지 테스트합니다."""
    initial_level = pykis_logging.logger.level

    try:
        pykis_logging.setLevel(level_input)
        assert pykis_logging.logger.level == expected_level
    finally:
        # 테스트 후 원래 레벨로 복원
        pykis_logging.logger.setLevel(initial_level)

