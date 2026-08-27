import pytest

from vmkis.client.page import KisPage, to_page_status


def test_to_page_status_begin_and_end_and_invalid():
    assert to_page_status("F") == "begin"
    assert to_page_status("M") == "begin"
    assert to_page_status("D") == "end"
    assert to_page_status("E") == "end"

    with pytest.raises(ValueError):
        to_page_status("X")


def test_kispage_init_defaults_and_first():
    p = KisPage()
    assert p.size is None
    assert p.search == ""
    assert p.key == ""

    p2 = KisPage.first(50)
    assert isinstance(p2, KisPage)
    assert p2.size == 50


def test_pre_init_parses_100_and_200_and_raises():
    p = KisPage()
    data100 = {"ctx_area_fk100": "S100", "ctx_area_nk100": "K100"}
    p.__pre_init__(data100)
    assert p.search == "S100"
    assert p.key == "K100"
    assert p.size == 100

    p2 = KisPage()
    data200 = {"ctx_area_fk200": "S200", "ctx_area_nk200": "K200"}
    p2.__pre_init__(data200)
    assert p2.search == "S200"
    assert p2.key == "K200"
    assert p2.size == 200

    p3 = KisPage()
    with pytest.raises(ValueError):
        p3.__pre_init__({"other": 1})


def test_is_empty_is_first_and_size_checks():
    p = KisPage()
    assert p.is_empty
    assert p.is_first

    p.search = " "
    p.key = " "
    assert p.is_empty

    p.size = 100
    assert p.is_100
    assert not p.is_200

    p.size = 200
    assert p.is_200
    assert not p.is_100


def test_to_changes_size_or_raises_when_too_small():
    p = KisPage(size=50, search="ab", key="cd")
    new = p.to(100)
    assert isinstance(new, KisPage)
    assert new.size == 100
    assert new.search == "ab"

    p2 = KisPage(size=10, search="longsearch", key="k")
    with pytest.raises(ValueError):
        p2.to(5)


def test_build_requires_size_and_builds_keys():
    p = KisPage(size=100, search="s", key="k")
    d = p.build()
    assert d["ctx_area_fk100"] == "s"
    assert d["ctx_area_nk100"] == "k"

    p2 = KisPage()
    with pytest.raises(ValueError):
        p2.build()
