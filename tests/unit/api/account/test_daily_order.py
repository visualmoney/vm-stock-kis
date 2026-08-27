import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from vmkis.api.account import daily_order as dord
from vmkis.client.page import KisPage


def test_domestic_exchange_code_map_basic():
    # verify some known mappings
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["01"][0] == "KR"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["51"][0] == "HK"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["61"][2] == "before"


def test_kis_daily_order_base_amounts_and_qtys():
    inst = object.__new__(dord.KisDailyOrderBase)
    inst.unit_price = Decimal("10")
    inst.price = Decimal("9")
    inst.quantity = Decimal("5")
    inst.executed_quantity = Decimal("3")
    inst.pending_quantity = Decimal("2")

    # order_price proxies unit_price
    assert inst.order_price == Decimal("10")
    # qty proxies quantity
    assert inst.qty == Decimal("5")
    # executed_qty proxies executed_quantity
    assert inst.executed_qty == Decimal("3")
    # executed_amount uses price (not unit_price)
    assert inst.executed_amount == Decimal("27")
    # pending_qty proxies pending_quantity
    assert inst.pending_qty == Decimal("2")


def test__domestic_daily_orders_calls_fetch_and_returns_result():
    # Create a fake 'self' with a fetch that returns a simple object
    calls = []

    class FakeSelf:
        def __init__(self):
            self.virtual = False

        def fetch(self, *args, **kwargs):
            calls.append((args, kwargs))
            # Return an object that mimics the API response used by the function
            return SimpleNamespace(is_last=True, orders=["A"], next_page=None)

    fake = FakeSelf()
    start = date.today() - timedelta(days=1)
    end = date.today()

    res = dord._domestic_daily_orders(fake, account="12345678", start=start, end=end)
    assert res.orders == ["A"]
    # verify fetch was called once and with expected kwargs including form
    assert len(calls) == 1
    _, kw = calls[0]
    assert "form" in kw


def test_domestic_daily_orders_swapped_dates_and_page_to():
    class FakeSelf:
        def __init__(self):
            self.virtual = False

        def fetch(self, *args, **kwargs):
            return SimpleNamespace(is_last=True, orders=[], next_page=None)

    fake = FakeSelf()
    # pass start > end and ensure no exception (function swaps)
    start = date(2020, 5, 1)
    end = date(2020, 1, 1)
    res = dord._domestic_daily_orders(fake, account="12345678", start=start, end=end)
    assert hasattr(res, "orders")


def test_kis_integration_daily_orders_merges_and_sorts():
    # create two small KisDailyOrders-like objects
    o1 = SimpleNamespace(orders=[SimpleNamespace(time_kst=datetime(2021, 1, 2)), SimpleNamespace(time_kst=datetime(2021, 1, 1))])
    o2 = SimpleNamespace(orders=[SimpleNamespace(time_kst=datetime(2021, 1, 3))])

    kd = dord.KisIntegrationDailyOrders(None, "ACC", o1, o2)
    # merged and sorted in descending order by time_kst
    times = [o.time_kst for o in kd.orders]
    assert times == sorted(times, reverse=True)


def test_kis_daily_orders_base_getitem_by_index():
    """Test __getitem__ with integer index."""
    orders_list = [
        SimpleNamespace(symbol="005930", order_number="1"),
        SimpleNamespace(symbol="AAPL", order_number="2")
    ]

    daily_orders = object.__new__(dord.KisDailyOrdersBase)
    daily_orders.orders = orders_list

    assert daily_orders[0].symbol == "005930"
    assert daily_orders[1].symbol == "AAPL"


def test_kis_daily_orders_base_getitem_by_symbol():
    """Test __getitem__ with symbol string."""
    orders_list = [
        SimpleNamespace(symbol="005930", order_number="1"),
        SimpleNamespace(symbol="AAPL", order_number="2")
    ]

    daily_orders = object.__new__(dord.KisDailyOrdersBase)
    daily_orders.orders = orders_list

    assert daily_orders["005930"].order_number == "1"
    assert daily_orders["AAPL"].order_number == "2"


def test_kis_daily_orders_base_getitem_keyerror():
    """Test __getitem__ raises KeyError for non-existent key."""
    orders_list = [SimpleNamespace(symbol="005930", order_number="1")]

    daily_orders = object.__new__(dord.KisDailyOrdersBase)
    daily_orders.orders = orders_list

    with pytest.raises(KeyError):
        _ = daily_orders["NONEXISTENT"]


def test_kis_daily_orders_base_order_by_symbol():
    """Test order() method with symbol."""
    orders_list = [
        SimpleNamespace(symbol="005930", order_number="1"),
        SimpleNamespace(symbol="AAPL", order_number="2")
    ]

    daily_orders = object.__new__(dord.KisDailyOrdersBase)
    daily_orders.orders = orders_list

    result = daily_orders.order("005930")
    assert result is not None
    assert result.order_number == "1"

    # Non-existent symbol returns None
    result = daily_orders.order("NONEXISTENT")
    assert result is None


def test_kis_daily_orders_base_len():
    """Test __len__ method."""
    orders_list = [
        SimpleNamespace(symbol="005930"),
        SimpleNamespace(symbol="AAPL"),
        SimpleNamespace(symbol="MSFT")
    ]

    daily_orders = object.__new__(dord.KisDailyOrdersBase)
    daily_orders.orders = orders_list

    assert len(daily_orders) == 3


def test_kis_daily_orders_base_iter():
    """Test __iter__ method."""
    orders_list = [
        SimpleNamespace(symbol="005930"),
        SimpleNamespace(symbol="AAPL")
    ]

    daily_orders = object.__new__(dord.KisDailyOrdersBase)
    daily_orders.orders = orders_list

    symbols = [order.symbol for order in daily_orders]
    assert symbols == ["005930", "AAPL"]


def test_domestic_exchange_code_map_coverage():
    """Test various exchange code mappings."""
    # Test KRX codes
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["02"][0] == "KR"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["03"][0] == "KR"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["04"][1] == "KRX"

    # Test foreign exchange codes
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["52"][0] == "CN"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["53"][1] == "SZSE"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["55"][0] == "US"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["56"][0] == "JP"

    # Test special condition codes
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["81"][2] == "extended"
    assert dord.DOMESTIC_EXCHANGE_CODE_MAP["64"][2] is None


# test_kis_daily_orders_base_getitem_by_order_number and
# test_kis_daily_orders_base_order_by_order_number are complex tests that require
# order equality to work properly, which is tested in test_order.py


def test_kis_domestic_daily_order_pre_init_with_market():
    """Test KisDomesticDailyOrder.__pre_init__ with market-specific exchange code."""
    from vmkis.utils.timezone import TIMEZONE
    from vmkis.api.stock.market import get_market_timezone

    order = object.__new__(dord.KisDomesticDailyOrder)

    # Test with US exchange code (55)
    data = {
        "ord_dt": "20240101",
        "ord_tmd": "153000",
        "excg_dvsn_cd": "55",  # US market
        "pdno": "AAPL",
        "sll_buy_dvsn_cd": "02",
        "avg_prvs": "150.00",
        "ord_unpr": "150.50",
        "ord_qty": "10",
        "tot_ccld_qty": "5",
        "rmn_qty": "5",
        "rjct_qty": "0",
        "ccld_yn": "N",
        "prdt_name": "Apple",
        "ord_gno_brno": "00001",
        "odno": "12345"
    }

    order.__pre_init__(data)

    # Should set country to US (market stays "KRX" as default for KisDomesticDailyOrder)
    assert order.country == "US"


def test_kis_domestic_daily_order_pre_init_with_cn_market():
    """Test KisDomesticDailyOrder.__pre_init__ with Chinese market."""
    order = object.__new__(dord.KisDomesticDailyOrder)

    data = {
        "ord_dt": "20240101",
        "ord_tmd": "153000",
        "excg_dvsn_cd": "52",  # SSE market
        "pdno": "600000",
        "sll_buy_dvsn_cd": "02",
        "avg_prvs": "10.00",
        "ord_unpr": "10.50",
        "ord_qty": "100",
        "tot_ccld_qty": "50",
        "rmn_qty": "50",
        "rjct_qty": "0",
        "ccld_yn": "N",
        "prdt_name": "SSE Stock",
        "ord_gno_brno": "00001",
        "odno": "12345"
    }

    order.__pre_init__(data)

    # Should set country to CN and market to SSE
    assert order.country == "CN"
    assert order.market == "SSE"
    # Should update timezone to SSE timezone
    from vmkis.api.stock.market import get_market_timezone
    assert order.timezone == get_market_timezone("SSE")


def test_kis_domestic_daily_order_pre_init_with_condition():
    """Test KisDomesticDailyOrder.__pre_init__ with order condition."""
    order = object.__new__(dord.KisDomesticDailyOrder)

    data = {
        "ord_dt": "20240101",
        "ord_tmd": "093000",
        "excg_dvsn_cd": "61",  # before market condition
        "pdno": "005930",
        "sll_buy_dvsn_cd": "02",
        "avg_prvs": "50000",
        "ord_unpr": "50000",
        "ord_qty": "10",
        "tot_ccld_qty": "5",
        "rmn_qty": "5",
        "rjct_qty": "0",
        "ccld_yn": "N",
        "prdt_name": "Samsung",
        "ord_gno_brno": "00001",
        "odno": "12345"
    }

    order.__pre_init__(data)

    # Should set condition to "before"
    assert order.condition == "before"


def test_kis_domestic_daily_order_post_init():
    """Test KisDomesticDailyOrder.__post_init__ converts timezone."""
    from vmkis.utils.timezone import TIMEZONE
    from zoneinfo import ZoneInfo

    order = object.__new__(dord.KisDomesticDailyOrder)
    order.time_kst = datetime.now(TIMEZONE)
    order.timezone = ZoneInfo("Asia/Shanghai")

    order.__post_init__()

    # Should have converted time to local timezone
    assert order.time.tzinfo == order.timezone


def test_kis_domestic_daily_orders_post_init():
    """Test KisDomesticDailyOrders.__post_init__ sets account_number on orders."""
    from vmkis.client.account import KisAccountNumber

    account = KisAccountNumber("12345678-01")

    orders_instance = object.__new__(dord.KisDomesticDailyOrders)
    orders_instance.account_number = account

    # Create mock orders that behave like KisDailyOrderBase
    order1 = object.__new__(dord.KisDailyOrderBase)
    order2 = object.__new__(dord.KisDailyOrderBase)
    orders_instance.orders = [order1, order2]

    orders_instance.__post_init__()

    # Should have set account_number on all orders
    assert order1.account_number == account
    assert order2.account_number == account


def test_kis_domestic_daily_orders_kis_post_init(monkeypatch):
    """Test KisDomesticDailyOrders.__kis_post_init__ spreads kis."""
    from vmkis.client.account import KisAccountNumber

    account = KisAccountNumber("12345678-01")

    orders_instance = object.__new__(dord.KisDomesticDailyOrders)
    orders_instance.account_number = account
    orders_instance.orders = [SimpleNamespace(), SimpleNamespace()]

    # Mock super().__kis_post_init__ and _kis_spread
    monkeypatch.setattr(dord.KisPaginationAPIResponse, "__kis_post_init__", lambda self: None)

    spread_called = []
    orders_instance._kis_spread = lambda orders: spread_called.append(orders)

    orders_instance.__kis_post_init__()

    # Should have called _kis_spread with orders
    assert len(spread_called) == 1


def test_kis_foreign_daily_order_post_init():
    """Test KisForeignDailyOrder.__post_init__ converts timezone."""
    from vmkis.utils.timezone import TIMEZONE
    from vmkis.api.stock.market import get_market_timezone

    order = object.__new__(dord.KisForeignDailyOrder)
    order.time_kst = datetime.now(TIMEZONE)
    order.timezone = get_market_timezone("NASDAQ")

    order.__post_init__()

    # Should have converted time to NASDAQ timezone
    assert order.time.tzinfo == order.timezone


def test_kis_foreign_daily_orders_post_init():
    """Test KisForeignDailyOrders.__post_init__ sets account_number on orders."""
    from vmkis.client.account import KisAccountNumber

    account = KisAccountNumber("12345678-01")

    orders_instance = object.__new__(dord.KisForeignDailyOrders)
    orders_instance.account_number = account

    # Create mock orders that behave like KisDailyOrderBase
    order1 = object.__new__(dord.KisDailyOrderBase)
    order2 = object.__new__(dord.KisDailyOrderBase)
    orders_instance.orders = [order1, order2]

    orders_instance.__post_init__()

    # Should have set account_number on all orders
    assert order1.account_number == account
    assert order2.account_number == account


def test_kis_foreign_daily_orders_kis_post_init(monkeypatch):
    """Test KisForeignDailyOrders.__kis_post_init__ spreads kis."""
    from vmkis.client.account import KisAccountNumber

    account = KisAccountNumber("12345678-01")

    orders_instance = object.__new__(dord.KisForeignDailyOrders)
    orders_instance.account_number = account
    orders_instance.orders = [SimpleNamespace(), SimpleNamespace()]

    # Mock super().__kis_post_init__ and _kis_spread
    monkeypatch.setattr(dord.KisPaginationAPIResponse, "__kis_post_init__", lambda self: None)

    spread_called = []
    orders_instance._kis_spread = lambda orders: spread_called.append(orders)

    orders_instance.__kis_post_init__()

    # Should have called _kis_spread with orders
    assert len(spread_called) == 1


def test_domestic_daily_orders_api_codes():
    """Test DOMESTIC_DAILY_ORDERS_API_CODES mappings."""
    # Real mode, recent (within 3 months)
    assert (True, True) in dord.DOMESTIC_DAILY_ORDERS_API_CODES
    assert dord.DOMESTIC_DAILY_ORDERS_API_CODES[(True, True)] == "TTTC8001R"

    # Real mode, old (more than 3 months)
    assert (True, False) in dord.DOMESTIC_DAILY_ORDERS_API_CODES
    assert dord.DOMESTIC_DAILY_ORDERS_API_CODES[(True, False)] == "CTSC9115R"

    # Virtual mode, recent
    assert (False, True) in dord.DOMESTIC_DAILY_ORDERS_API_CODES
    assert dord.DOMESTIC_DAILY_ORDERS_API_CODES[(False, True)] == "VTTC8001R"

    # Virtual mode, old
    assert (False, False) in dord.DOMESTIC_DAILY_ORDERS_API_CODES
    assert dord.DOMESTIC_DAILY_ORDERS_API_CODES[(False, False)] == "VTSC9115R"


def test_foreign_country_market_map():
    """Test FOREIGN_COUNTRY_MARKET_MAP contains expected mappings."""
    assert None in dord.FOREIGN_COUNTRY_MARKET_MAP
    assert "US" in dord.FOREIGN_COUNTRY_MARKET_MAP
    assert "HK" in dord.FOREIGN_COUNTRY_MARKET_MAP
    assert "CN" in dord.FOREIGN_COUNTRY_MARKET_MAP
    assert "JP" in dord.FOREIGN_COUNTRY_MARKET_MAP
    assert "VN" in dord.FOREIGN_COUNTRY_MARKET_MAP

    # US maps to NASDAQ
    assert dord.FOREIGN_COUNTRY_MARKET_MAP["US"] == ["NASDAQ"]

    # CN maps to both SSE and SZSE
    assert "SSE" in dord.FOREIGN_COUNTRY_MARKET_MAP["CN"]
    assert "SZSE" in dord.FOREIGN_COUNTRY_MARKET_MAP["CN"]

    # VN maps to both HSX and HNX
    assert "HSX" in dord.FOREIGN_COUNTRY_MARKET_MAP["VN"]
    assert "HNX" in dord.FOREIGN_COUNTRY_MARKET_MAP["VN"]


def test_kis_integration_daily_orders_initialization():
    """Test KisIntegrationDailyOrders initialization and sorting."""
    from vmkis.client.account import KisAccountNumber

    mock_kis = SimpleNamespace()
    account = KisAccountNumber("12345678-01")

    # Create mock daily orders
    order1 = SimpleNamespace(time_kst=datetime(2021, 1, 1))
    order2 = SimpleNamespace(time_kst=datetime(2021, 1, 3))
    order3 = SimpleNamespace(time_kst=datetime(2021, 1, 2))

    orders1 = SimpleNamespace(orders=[order1])
    orders2 = SimpleNamespace(orders=[order2, order3])

    # Create integration orders
    integ = dord.KisIntegrationDailyOrders(mock_kis, account, orders1, orders2)

    # Should merge all orders and sort by time_kst descending
    assert len(integ.orders) == 3
    assert integ.orders[0].time_kst == datetime(2021, 1, 3)
    assert integ.orders[1].time_kst == datetime(2021, 1, 2)
    assert integ.orders[2].time_kst == datetime(2021, 1, 1)
