"""Tests de vault.dates — lógica pura de fechas, sin reloj real."""

from datetime import datetime

from vault import dates


class TestDayId:
    def test_formats_date_as_yyyymmdd(self):
        assert dates.day_id(datetime(2026, 6, 25, 10, 14)) == "20260625"

    def test_pads_single_digit_month_and_day(self):
        assert dates.day_id(datetime(2026, 1, 5)) == "20260105"


class TestTimeOfDay:
    def test_formats_time_as_hh_mm(self):
        assert dates.time_of_day(datetime(2026, 6, 25, 10, 14)) == "10:14"

    def test_pads_single_digit_hour_and_minute(self):
        assert dates.time_of_day(datetime(2026, 6, 25, 9, 5)) == "09:05"

    def test_midnight(self):
        assert dates.time_of_day(datetime(2026, 6, 25, 0, 0)) == "00:00"


class TestWeekday:
    def test_returns_lowercase_english_weekday(self):
        # 2026-06-25 is a Thursday
        assert dates.weekday(datetime(2026, 6, 25)) == "thursday"

    def test_friday(self):
        # 2026-06-26 is a Friday
        assert dates.weekday(datetime(2026, 6, 26)) == "friday"


class TestIsoWeek:
    def test_returns_iso_week_label(self):
        # 2026-06-25 is in ISO week 26
        assert dates.iso_week(datetime(2026, 6, 25)) == "2026-W26"

    def test_pads_single_digit_week(self):
        # 2026-01-05 is in ISO week 2
        assert dates.iso_week(datetime(2026, 1, 5)) == "2026-W02"

    def test_iso_year_can_differ_from_calendar_year(self):
        # 2026-12-31 is a Thursday in ISO week 53 of 2026
        assert dates.iso_week(datetime(2026, 12, 31)) == "2026-W53"


class TestIsFriday:
    def test_true_on_friday(self):
        assert dates.is_friday(datetime(2026, 6, 26)) is True

    def test_false_on_other_days(self):
        assert dates.is_friday(datetime(2026, 6, 25)) is False


class TestWeekLabel:
    def test_short_week_label_for_filename(self):
        # Used for the weekly summary note name: W-26
        assert dates.week_label(datetime(2026, 6, 25)) == "W-26"


class TestWeekRange:
    def test_monday_to_friday_of_the_week(self):
        # Thursday 2026-06-25 -> Mon 22 .. Fri 26
        monday, friday = dates.week_range_mon_fri(datetime(2026, 6, 25, 15, 0))
        assert monday == datetime(2026, 6, 22)
        assert friday == datetime(2026, 6, 26)

    def test_when_given_a_friday(self):
        monday, friday = dates.week_range_mon_fri(datetime(2026, 6, 26))
        assert monday == datetime(2026, 6, 22)
        assert friday == datetime(2026, 6, 26)
