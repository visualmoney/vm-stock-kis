import pathlib

# Ensure examples package path is importable
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_example_module(module_rel_path: str):
    import importlib.util

    fn = REPO_ROOT / module_rel_path
    spec = importlib.util.spec_from_file_location("example_mod", str(fn))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


load_mod = _load_example_module("examples/01_basic/get_quote.py")
load_config_example = load_mod.load_config


def test_load_config_single_virtual():
    path = REPO_ROOT / "config.example.virtual.yaml"
    cfg = load_config_example(path=str(path))
    assert isinstance(cfg, dict)
    assert cfg.get("id") == "YOUR_VIRTUAL_ID"
    assert cfg.get("virtual") is True


def test_load_config_single_real():
    path = REPO_ROOT / "config.example.real.yaml"
    cfg = load_config_example(path=str(path))
    assert isinstance(cfg, dict)
    assert cfg.get("id") == "YOUR_REAL_ID"
    assert cfg.get("virtual") is False


def test_load_config_multi_default():
    path = REPO_ROOT / "config.example.yaml"
    cfg = load_config_example(path=str(path))
    # default in example is 'virtual'
    assert isinstance(cfg, dict)
    assert cfg.get("id") == "YOUR_VIRTUAL_ID"
    assert cfg.get("virtual") is True


def test_load_config_multi_select_real():
    path = REPO_ROOT / "config.example.yaml"
    cfg = load_config_example(path=str(path), profile="real")
    assert isinstance(cfg, dict)
    assert cfg.get("id") == "YOUR_REAL_ID"
    assert cfg.get("virtual") is False
