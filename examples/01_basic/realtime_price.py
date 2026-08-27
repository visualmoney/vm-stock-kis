"""실시간 체결가 구독 예제.

- 삼성전자(005930) 실시간 체결가를 구독합니다.
- 종료하려면 Enter를 누르세요.
"""

import yaml

from vmkis import KisAuth, VmKis


def load_config(path: str = "config.yaml", profile: str | None = None) -> dict:
    import os

    profile = profile or os.environ.get("VMKIS_PROFILE")
    with open(path, encoding="utf-8") as f:
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

    def on_price(sender, e):
        print(e.response)

    ticket = stock.on("price", on_price)
    try:
        input("Press Enter to stop streaming...\n")
    finally:
        ticket.unsubscribe()


if __name__ == "__main__":
    main()
