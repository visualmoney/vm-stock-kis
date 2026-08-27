"""기본 시세 조회 예제.

이 예제는 config.yaml에서 인증 정보를 로드한 뒤
삼성전자(005930) 시세를 조회해 출력합니다.
"""
import yaml
from vmkis import VmKis, KisAuth


def load_config(path: str = "config.yaml", profile: str | None = None) -> dict:
    """Load configuration.

    Supports two formats:
      - legacy flat config (id, account, ...)
      - multi-profile config with top-level `configs` mapping and `default` key

    Profile selection order:
      1. explicit `profile` argument
      2. environment `VMKIS_PROFILE`
      3. `default` key in multi-config
      4. fallback to 'virtual'
    """
    import os

    profile = profile or os.environ.get("VMKIS_PROFILE")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if isinstance(cfg, dict) and "configs" in cfg:
        sel = profile or cfg.get("default") or "virtual"
        selected = cfg["configs"].get(sel)
        if not selected:
            raise ValueError(f"Profile '{sel}' not found in {path}")
        return selected

    return cfg


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--profile", help="config profile name (virtual|real)")
    args = parser.parse_args()

    cfg = load_config(path=args.config, profile=args.profile)

    auth = KisAuth(
        id=cfg["id"],
        account=cfg["account"],
        appkey=cfg["appkey"],
        secretkey=cfg["secretkey"],
        virtual=cfg.get("virtual", False),
    )

    kis = VmKis(auth, keep_token=True)

    stock = kis.stock("005930")  # 삼성전자
    quote = stock.quote()
    print(quote)


if __name__ == "__main__":
    main()
