"""`pykis.helpers` 테스트.

이 모듈은 오랫동안 커버리지 27%에 머물러 있었다. 원인은 테스트 부족이 아니라
`save_config_interactive()` 본문에 모듈 전체 복사본이 통째로 중첩되어 있었기
때문이다. 바깥 함수는 그 중첩 정의들을 호출하지도 반환하지도 않아
`None`을 반환했고, 선언된 반환 타입 `dict[str, Any]`와 어긋나 있었다.
https://github.com/visualmoney/vm-stock-kis/issues/3
"""

import getpass

import pytest
import yaml
from pykis import helpers


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """프로필/확인 관련 환경변수가 테스트 사이로 새지 않게 합니다."""
    monkeypatch.delenv("PYKIS_PROFILE", raising=False)
    monkeypatch.delenv("PYKIS_CONFIRM_SKIP", raising=False)


def write_yaml(path, data):
    path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return str(path)


FLAT_CONFIG = {
    "id": "testid",
    "account": "00000000-01",
    "appkey": "appkey",
    "secretkey": "secret",
    "virtual": True,
}

MULTI_CONFIG = {
    "default": "virtual",
    "configs": {
        "virtual": dict(FLAT_CONFIG, id="virtual-id"),
        "real": dict(FLAT_CONFIG, id="real-id", virtual=False),
    },
}


class TestLoadConfig:
    """`load_config` 테스트."""

    def test_flat_config(self, tmp_path):
        """구형 단일 설정은 그대로 반환한다."""
        path = write_yaml(tmp_path / "config.yaml", FLAT_CONFIG)

        assert helpers.load_config(path) == FLAT_CONFIG

    def test_multi_config_uses_default_key(self, tmp_path):
        """프로필을 지정하지 않으면 `default` 키를 따른다."""
        path = write_yaml(tmp_path / "config.yaml", MULTI_CONFIG)

        assert helpers.load_config(path)["id"] == "virtual-id"

    def test_multi_config_explicit_profile(self, tmp_path):
        """명시한 프로필이 `default`보다 우선한다."""
        path = write_yaml(tmp_path / "config.yaml", MULTI_CONFIG)

        assert helpers.load_config(path, profile="real")["id"] == "real-id"

    def test_multi_config_profile_from_env(self, tmp_path, monkeypatch):
        """환경변수 `PYKIS_PROFILE`을 읽는다."""
        path = write_yaml(tmp_path / "config.yaml", MULTI_CONFIG)
        monkeypatch.setenv("PYKIS_PROFILE", "real")

        assert helpers.load_config(path)["id"] == "real-id"

    def test_explicit_profile_beats_env(self, tmp_path, monkeypatch):
        """인자가 환경변수보다 우선한다."""
        path = write_yaml(tmp_path / "config.yaml", MULTI_CONFIG)
        monkeypatch.setenv("PYKIS_PROFILE", "real")

        assert helpers.load_config(path, profile="virtual")["id"] == "virtual-id"

    def test_multi_config_falls_back_to_virtual(self, tmp_path):
        """`default`가 없으면 'virtual'로 폴백한다."""
        config = {"configs": MULTI_CONFIG["configs"]}
        path = write_yaml(tmp_path / "config.yaml", config)

        assert helpers.load_config(path)["id"] == "virtual-id"

    def test_unknown_profile_raises(self, tmp_path):
        """없는 프로필은 ValueError."""
        path = write_yaml(tmp_path / "config.yaml", MULTI_CONFIG)

        with pytest.raises(ValueError, match="Profile 'nope' not found"):
            helpers.load_config(path, profile="nope")


class TestCreateClient:
    """`create_client` 테스트."""

    @pytest.fixture
    def dummy_pykis(self, monkeypatch):
        """네트워크 호출을 피하기 위해 `PyKis`를 대체합니다."""
        calls = []

        class DummyPyKis:
            def __init__(self, *args, **kwargs):
                calls.append((args, kwargs))

        monkeypatch.setattr(helpers, "PyKis", DummyPyKis)
        return calls

    def test_virtual_config_passed_as_virtual_auth(self, tmp_path, dummy_pykis):
        """모의 자격증명은 첫 인자가 None이고 두 번째로 전달되어야 한다."""
        path = write_yaml(tmp_path / "config.yaml", FLAT_CONFIG)

        helpers.create_client(path)

        (args, kwargs) = dummy_pykis[0]
        assert args[0] is None
        assert args[1].virtual is True
        assert kwargs["keep_token"] is True

    def test_real_config_passed_as_positional_auth(self, tmp_path, dummy_pykis):
        """실전 자격증명은 첫 인자로 전달된다."""
        path = write_yaml(tmp_path / "config.yaml", dict(FLAT_CONFIG, virtual=False))

        helpers.create_client(path, keep_token=False)

        (args, kwargs) = dummy_pykis[0]
        assert args[0].virtual is False
        assert kwargs["keep_token"] is False

    def test_virtual_key_defaults_to_false(self, tmp_path, dummy_pykis):
        """`virtual` 키가 없으면 실전으로 간주한다."""
        config = {k: v for k, v in FLAT_CONFIG.items() if k != "virtual"}
        path = write_yaml(tmp_path / "config.yaml", config)

        helpers.create_client(path)

        (args, _) = dummy_pykis[0]
        assert args[0].virtual is False

    def test_profile_is_forwarded(self, tmp_path, dummy_pykis):
        """`profile` 인자가 load_config로 전달된다."""
        path = write_yaml(tmp_path / "config.yaml", MULTI_CONFIG)

        helpers.create_client(path, profile="real")

        (args, _) = dummy_pykis[0]
        assert args[0].id == "real-id"


class TestSaveConfigInteractive:
    """`save_config_interactive` 테스트."""

    @pytest.fixture
    def answers(self, monkeypatch):
        """`input`/`getpass`를 대본으로 대체합니다."""
        script = []

        def fake_input(prompt=""):
            assert script, f"입력 대본이 소진되었습니다. 프롬프트: {prompt!r}"
            return script.pop(0)

        monkeypatch.setattr("builtins.input", fake_input)
        monkeypatch.setattr(getpass, "getpass", lambda prompt="": "s" * 180)
        return script

    def test_writes_yaml_and_returns_data(self, tmp_path, answers, monkeypatch):
        """확인을 건너뛰면 파일을 쓰고 저장한 값을 반환한다."""
        monkeypatch.setenv("PYKIS_CONFIRM_SKIP", "1")
        answers.extend(["myid", "00000000-01", "myappkey", "y"])
        path = tmp_path / "config.yaml"

        result = helpers.save_config_interactive(str(path))

        assert result["id"] == "myid"
        assert result["account"] == "00000000-01"
        assert result["appkey"] == "myappkey"
        assert result["secretkey"] == "s" * 180
        assert result["virtual"] is True

        # 반환값이 실제로 파일에 쓰인 내용과 일치해야 한다.
        assert yaml.safe_load(path.read_text(encoding="utf-8")) == result

    @pytest.mark.parametrize(
        ("answer", "expected"),
        [("y", True), ("yes", True), ("true", True), ("1", True), ("n", False), ("", False), ("N0", False)],
    )
    def test_virtual_answer_parsing(self, tmp_path, answers, monkeypatch, answer, expected):
        """Virtual 응답 해석."""
        monkeypatch.setenv("PYKIS_CONFIRM_SKIP", "1")
        answers.extend(["myid", "00000000-01", "myappkey", answer])

        result = helpers.save_config_interactive(str(tmp_path / "config.yaml"))

        assert result["virtual"] is expected

    def test_confirm_prompt_accepts_write(self, tmp_path, answers):
        """확인 프롬프트에 y로 답하면 기록한다."""
        answers.extend(["myid", "00000000-01", "myappkey", "n", "y"])
        path = tmp_path / "config.yaml"

        helpers.save_config_interactive(str(path))

        assert path.exists()

    def test_declining_aborts_without_writing(self, tmp_path, answers):
        """확인 프롬프트를 거절하면 파일을 쓰지 않고 SystemExit."""
        answers.extend(["myid", "00000000-01", "myappkey", "n", "N"])
        path = tmp_path / "config.yaml"

        with pytest.raises(SystemExit, match="Aborted by user"):
            helpers.save_config_interactive(str(path))

        assert not path.exists()

    def test_secret_is_masked_in_preview(self, tmp_path, answers, monkeypatch, capsys):
        """미리보기에 비밀키 전체가 노출되지 않는다."""
        monkeypatch.setenv("PYKIS_CONFIRM_SKIP", "1")
        answers.extend(["myid", "00000000-01", "myappkey", "y"])

        helpers.save_config_interactive(str(tmp_path / "config.yaml"))

        out = capsys.readouterr().out
        assert "s" * 180 not in out
        assert "ssss..." in out
