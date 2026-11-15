# 2026-11-16 - 일봉 날짜 커서

이슈: [#180](https://github.com/visualmoney/vm-stock-kis/issues/180). 결정은 A.

## 무엇을 옮겼나

`domestic_daily_chart` 와 `foreign_daily_chart` 의 `while` 이 같은 18줄이었다. 빈 봉, 커서가 마지막 봉보다 앞섬, `bars` 이어 붙이기, `timedelta` 시작을 첫 봉에서 날짜로, 시작에 닿으면 중단, 커서를 `last - step`.

그 골격만 `api/stock/daily_chart.py` 의 `_collect_dated_bars` 다. 파라미터와 `drop_after`, 해외 연봉 버킷은 호출부에 남겼다.

당일 차트(`day_chart.py`)와 해외 `NMIN` 루프는 날짜 커서가 아니라서 넣지 않았다. `fetch_pages` 도 쓰지 않았다. 종료가 `is_last` 가 아니다.

상한은 500페이지다. 일봉이 한 페이지에 100개면 약 500년분이고, 그 전에 커서가 뒤로 가지 않으면 루프가 멈춘다.

## 회귀

`cursor < last` 판정을 빼고 `test_discards_page_when_cursor_does_not_move_back` 를 돌렸다. 멈추지 않은 페이지가 합쳐져 `assert 4 == 2` 로 실패했다. 판정을 되돌린 뒤 같은 테스트는 통과했다.

## 함정

커서가 뒤로 가지 않으면 **그 페이지를 합치기 전에** 끊어야 한다. 합친 다음 끊으면 같은 봉이 한 번 더 붙는다. 테스트는 빈 페이지를 뒤에 두어, 판정이 없어도 `IndexError` 가 아니라 봉 개수로 실패하게 했다.
