"""기본 잔고 조회 예제.

config.yaml의 인증 정보를 사용해 계좌 잔고를 조회합니다.
"""

from vmkis import KisAuth, VmKis, load_config


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
        virtual=cfg["virtual"],
    )

    kis = VmKis(auth, keep_token=True)

    account = kis.account()
    balance = account.balance()
    print(balance)


if __name__ == "__main__":
    main()
