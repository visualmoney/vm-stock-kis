"""기본 주문 예제 (안전 장치 포함).

- 실계좌 주문 시 ALLOW_LIVE_TRADES=1 환경 변수를 설정해야 합니다.
- 모의투자 계정으로 먼저 검증하고, config.yaml 설정 후 주문을 수행합니다.
"""
import os
import yaml
from vmkis import VmKis, KisAuth


def load_config(path: str = "config.yaml", profile: str | None = None) -> dict:
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
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--profile", help="config profile name (virtual|real)")
    args = parser.parse_args()

    cfg = load_config(path=args.config, profile=args.profile)

    allow_live = os.environ.get("ALLOW_LIVE_TRADES") == "1"

    auth = KisAuth(
        id=cfg["id"],
        account=cfg["account"],
        appkey=cfg["appkey"],
        secretkey=cfg["secretkey"],
        virtual=cfg.get("virtual", False),
    )

    kis = VmKis(auth, keep_token=True)

    stock = kis.stock("005930")  # 삼성전자

    # 예시: 시장가 매수 1주 (실계좌/모의투자 설정에 따라 실행)
    order = stock.buy(qty=1)
    print(order)


if __name__ == "__main__":
    main()
