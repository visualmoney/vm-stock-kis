import warnings


def test_public_types_and_core_imports():
    # core class
    from vmkis import KisAuth, VmKis

    assert VmKis is not None
    assert KisAuth is not None

    # public types
    from vmkis import Balance, Chart, Order, Orderbook, Quote

    assert Quote is not None
    assert Balance is not None
    assert Order is not None
    assert Chart is not None
    assert Orderbook is not None


def test_deprecated_import_warns():
    # importing a legacy symbol from package root should warn and still work
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            # 이 import 자체가 테스트 대상이다. 값을 쓰지 않는다고 지우면
            # 테스트가 아무것도 검증하지 않게 된다.
            from vmkis import KisObjectProtocol  # noqa: F401
        except Exception:
            # if types module missing, just ensure warning was raised
            pass

        assert any(isinstance(x.message, DeprecationWarning) or x.category is DeprecationWarning for x in w)
