"""기본 시세 조회 예제.

이 예제는 config.yaml에서 인증 정보를 로드한 뒤
삼성전자(005930) 시세를 조회해 출력합니다.
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

    stock = kis.stock("005930")  # 삼성전자
    quote = stock.quote()
    print(quote)


if __name__ == "__main__":
    main()
