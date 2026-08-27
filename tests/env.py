import os
from typing import Literal

import vmkis.logging
from vmkis import VmKis

try:
    import dotenv

    dotenv.load_dotenv()
except ImportError:
    pass


def load_vmkis(
    domain: Literal["real", "virtual"] = "real",
    use_websocket: bool = True,
) -> VmKis:
    vmkis.logging.setLevel("DEBUG")

    if domain == "real":
        kis = VmKis(
            id=os.getenv("VMKIS_HTS_ID"),
            account=os.getenv("VMKIS_ACCOUNT_NUMBER"),
            appkey=os.getenv("VMKIS_APPKEY"),
            secretkey=os.getenv("VMKIS_SECRETKEY"),
            use_websocket=use_websocket,
            keep_token=os.getenv("VMKIS_KEEP_TOKEN", "false").lower() == "true",
        )
    else:
        kis = VmKis(
            id=os.getenv("VMKIS_HTS_ID"),
            account=os.getenv("VMKIS_VIRTUAL_ACCOUNT_NUMBER"),
            appkey=os.getenv("VMKIS_APPKEY"),
            secretkey=os.getenv("VMKIS_SECRETKEY"),
            virtual_id=os.getenv("VMKIS_VIRTUAL_HTS_ID"),
            virtual_appkey=os.getenv("VMKIS_VIRTUAL_APPKEY"),
            virtual_secretkey=os.getenv("VMKIS_VIRTUAL_SECRETKEY"),
            use_websocket=use_websocket,
            keep_token=os.getenv("VMKIS_KEEP_TOKEN", "false").lower() == "true",
        )

    return kis
