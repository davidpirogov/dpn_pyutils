import logging
from datetime import datetime as dt
from datetime import time, timedelta

import pytest
import pytz

from src.dpn_pyutils.time.periods import PeriodSchedule

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


TZ_AUS_SYD = "Australia/Sydney"


@pytest.fixture()
def period_schedule_params() -> dict:
    yield {
        "period_start_time_of_day": "09:00:00",
        "period_end_time_of_day": "17:30:00",
        "valid_days_of_week": [1, 2, 3],
    }


@pytest.fixture()
def period_schedule(period_schedule_params) -> PeriodSchedule:
    yield PeriodSchedule(
        period_schedule_params["period_start_time_of_day"],
        period_schedule_params["period_end_time_of_day"],
    )


@pytest.fixture()
def period_schedule_across_days(period_schedule_params) -> PeriodSchedule:
    """
    Create a period of time overnight between 1930 -> 0715
    """
    yield PeriodSchedule(
        "19:30:00",
        "07:15:00",
    )


@pytest.fixture()
def period_schedule_week_valid_invalid_dates() -> dict:
    """
    Returns set of valid_dates, invalid_dates and valid_days_of_week based
    on the next 7 days
    """

    test_dates = [
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=1),
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=2),
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=3),
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=4),
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=5),
        dt.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=6),
    ]

    valid_days_of_week = [3, 4, 5]  # Wednesday  # Thursday  # Friday

    valid_dates = []
    invalid_dates = []

    for d in test_dates:
        if int(d.strftime("%w")) in valid_days_of_week:
            valid_dates.append(d)
        else:
            invalid_dates.append(d)

    return {
        "valid_dates": valid_dates,
        "invalid_dates": invalid_dates,
        "valid_days_of_week": valid_days_of_week,
    }


@pytest.fixture
def period_schedule_valid_invalid_days_next_week(
    period_schedule_week_valid_invalid_dates, period_schedule_params
):
    """
    Creates a period schedule for the next week based on a select number of valid/invalid days
    """

    yield PeriodSchedule(
        period_schedule_params["period_start_time_of_day"],
        period_schedule_params["period_end_time_of_day"],
        period_schedule_week_valid_invalid_dates["valid_days_of_week"],
    )


@pytest.fixture
def period_schedule_valid_invalid_days_next_week_across_days(
    period_schedule_week_valid_invalid_dates,
):
    """
    Creates a period schedule for the next week based on a select number of valid/invalid days
    """

    yield PeriodSchedule(
        "19:15:00",
        "09:49:00",
        period_schedule_week_valid_invalid_dates["valid_days_of_week"],
    )


class TestPeriods:
    """
    https://docs.python.org/3.8/library/unittest.html#basic-example
    """

    #
    # Module tests: time.periods
    #

    def test_period_schedule_init(self, period_schedule_params):
        """
        Tests that the period schedule can be established correctly
        """

        ps = PeriodSchedule(
            period_schedule_params["period_start_time_of_day"],
            period_schedule_params["period_end_time_of_day"],
        )

        assert (
            ps.period_start_time_of_day
            == period_schedule_params["period_start_time_of_day"]
        )
        assert (
            ps.period_end_time_of_day
            == period_schedule_params["period_end_time_of_day"]
        )

        assert type(ps.start_time) is time
        assert type(ps.end_time) is time

    def test_period_schedule_init_valid_days(self, period_schedule_params):
        """
        Tests that the number of valid days is set correctly
        """

        ps = PeriodSchedule(
            period_schedule_params["period_start_time_of_day"],
            period_schedule_params["period_end_time_of_day"],
            period_schedule_params["valid_days_of_week"],
        )

        assert set(period_schedule_params["valid_days_of_week"]).issuperset(
            set(ps.valid_days_of_week)
        )

    def test_period_schedule_init_invalid_num_days(self, period_schedule_params):
        """
        Tests that the number of valid days is set incorrectly and raises an error
        """

        with pytest.raises(ValueError):
            PeriodSchedule(
                period_schedule_params["period_start_time_of_day"],
                period_schedule_params["period_end_time_of_day"],
                [0, 1, 2, 3, 4, 5, 6, 7],  # Should fail due to >7 days
            )

    def test_period_schedule_init_valid_num_days_cardinality(
        self, period_schedule_params
    ):
        """
        Tests that the valid days have correct cardinality (0 - 6)
        """

        ps = PeriodSchedule(
            period_schedule_params["period_start_time_of_day"],
            period_schedule_params["period_end_time_of_day"],
            period_schedule_params["valid_days_of_week"],
        )

        assert set(period_schedule_params["valid_days_of_week"]).issuperset(
            set(ps.valid_days_of_week)
        )

    def test_period_schedule_init_invalid_num_days_cardinality(
        self, period_schedule_params
    ):
        """
        Tests that the invalid days throw an exception with cardinality (0 - 6)
        """

        with pytest.raises(ValueError):
            PeriodSchedule(
                period_schedule_params["period_start_time_of_day"],
                period_schedule_params["period_end_time_of_day"],
                [-1, 0, 1, 2],  # Should fail due to value < 0
            )

        with pytest.raises(ValueError):
            PeriodSchedule(
                period_schedule_params["period_start_time_of_day"],
                period_schedule_params["period_end_time_of_day"],
                [4, 5, 6, 7],  # Should fail due to value > 6
            )

    def test_period_schedule_before_period(self, period_schedule):
        """
        Tests that today's date with times before the period are marked as such
        """

        assert not period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("00:00:00", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("08:59:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_inside_period(self, period_schedule):
        """
        Tests that today's date with times inside the period are marked as such
        """

        assert period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("09:00:00", "%H:%M:%S").time(),
            )
        )

        assert period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("09:00:01", "%H:%M:%S").time(),
            )
        )

        assert period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("13:45:00", "%H:%M:%S").time(),
            )
        )

        assert period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("17:29:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_after_period(self, period_schedule):
        """
        Tests that today's date with times after the period are marked as such
        """

        assert not period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("17:30:00", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("17:30:01", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("23:59:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_next_day_before_period(self, period_schedule_across_days):
        """
        Tests that today's date with times before the period are marked as such
        """

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("07:15:00", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("07:15:01", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("08:59:59", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("19:29:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_next_day_inside_period(self, period_schedule_across_days):
        """
        Tests that today's date and tomorrow's date with times during the period are marked as such
        """

        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("19:30:00", "%H:%M:%S").time(),
            )
        )

        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("19:30:01", "%H:%M:%S").time(),
            )
        )

        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date(),
                dt.strptime("23:59:59", "%H:%M:%S").time(),
            )
        )

        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("00:00:00", "%H:%M:%S").time(),
            )
        )

        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("00:00:01", "%H:%M:%S").time(),
            )
        )

        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("07:14:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_next_day_after_period(self, period_schedule_across_days):
        """
        Tests that today's date and tomorrow's date with times after the period are marked as such
        """

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("07:15:00", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("07:15:01", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("09:30:59", "%H:%M:%S").time(),
            )
        )

        assert not period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("19:29:59", "%H:%M:%S").time(),
            )
        )

        # Note: This is inside the next day's period schedule
        assert period_schedule_across_days.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)).date() + timedelta(days=1),
                dt.strptime("19:30:00", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_valid_days_period(
        self,
        period_schedule_week_valid_invalid_dates,
        period_schedule_valid_invalid_days_next_week,
    ):
        """
        Tests the next week's time period for valid days
        """

        for d in period_schedule_week_valid_invalid_dates["valid_dates"]:
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("00:00:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("08:59:59", "%H:%M:%S").time(),
                )
            )
            assert period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:00:00", "%H:%M:%S").time(),
                )
            )
            assert period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:00:01", "%H:%M:%S").time(),
                )
            )
            assert period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:29:59", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:30:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:30:01", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("23:59:59", "%H:%M:%S").time(),
                )
            )

    def test_period_schedule_invalid_days_period(
        self,
        period_schedule_week_valid_invalid_dates,
        period_schedule_valid_invalid_days_next_week,
    ):
        """
        Tests the next week's time period for valid days -- all should be not valid
        """

        for d in period_schedule_week_valid_invalid_dates["invalid_dates"]:
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("00:00:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("08:59:59", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:00:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:00:01", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:29:59", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:30:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:30:01", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("23:59:59", "%H:%M:%S").time(),
                )
            )

    def test_period_schedule_valid_days_period_across_days(
        self,
        period_schedule_week_valid_invalid_dates,
        period_schedule_valid_invalid_days_next_week_across_days,
    ):
        """
        Tests the next week's time period for valid days
        """

        #   "19:15:00",
        #   "09:49:00",

        for d in period_schedule_week_valid_invalid_dates["valid_dates"]:
            assert (
                period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                    dt.combine(
                        d.date(),
                        dt.strptime("00:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            assert (
                period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                    dt.combine(
                        d.date(),
                        dt.strptime("09:48:59", "%H:%M:%S").time(),
                    )
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:49:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:49:01", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("19:14:59", "%H:%M:%S").time(),
                )
            )
            assert (
                period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                    dt.combine(
                        d.date(),
                        dt.strptime("19:15:00", "%H:%M:%S").time(),
                    )
                )
            )
            assert (
                period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                    dt.combine(
                        d.date(),
                        dt.strptime("19:15:01", "%H:%M:%S").time(),
                    )
                )
            )
            assert (
                period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                    dt.combine(
                        d.date(),
                        dt.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )

    def test_period_schedule_invalid_days_period_across_days(
        self,
        period_schedule_week_valid_invalid_dates,
        period_schedule_valid_invalid_days_next_week_across_days,
    ):
        """
        Tests the next week's time period for valid days -- all should be not valid
        """

        for d in period_schedule_week_valid_invalid_dates["invalid_dates"]:
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("00:00:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("08:59:59", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:00:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("09:00:01", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:29:59", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:30:00", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("17:30:01", "%H:%M:%S").time(),
                )
            )
            assert not period_schedule_valid_invalid_days_next_week_across_days.is_in_period(
                dt.combine(
                    d.date(),
                    dt.strptime("23:59:59", "%H:%M:%S").time(),
                )
            )

    def test_period_schedule_tz_valid_str(self, period_schedule_params):
        """
        Tests that the period schedule can be established correctly with timezone support
        """

        timezone_name = "Australia/Sydney"

        ps = PeriodSchedule(
            period_schedule_params["period_start_time_of_day"],
            period_schedule_params["period_end_time_of_day"],
            tz=timezone_name,
        )

        assert type(ps.start_time) is time
        assert (
            ps.period_start_time_of_day
            == period_schedule_params["period_start_time_of_day"]
        )

        assert type(ps.end_time) is time
        assert (
            ps.period_end_time_of_day
            == period_schedule_params["period_end_time_of_day"]
        )

        assert type(ps.tz) is not str
        assert ps.tz.zone == timezone_name

    def test_period_schedule_tz_valid_time_period_day(self, period_schedule_params):
        """
        Tests that the period schedule can be established correctly with timezone support
        """

        timezone_name = "Australia/Sydney"

        ps = PeriodSchedule(
            period_schedule_params["period_start_time_of_day"],
            period_schedule_params["period_end_time_of_day"],
            tz=timezone_name,
        )

        assert not ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("08:59:59", "%H:%M:%S").time(),
            )
        )
        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("09:00:00", "%H:%M:%S").time(),
            )
        )
        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("09:00:01", "%H:%M:%S").time(),
            )
        )
        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("17:29:59", "%H:%M:%S").time(),
            )
        )
        assert not ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("17:30:00", "%H:%M:%S").time(),
            )
        )
        assert not ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("23:59:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_tz_valid_time_period_across_day(self):
        """
        Tests that the period schedule can be established correctly with timezone support
        """

        timezone_name = "Australia/Sydney"

        ps = PeriodSchedule(
            "20:00:00",
            "04:00:00",
            tz=timezone_name,
        )

        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("23:59:59", "%H:%M:%S").time(),
            )
        )
        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("00:00:00", "%H:%M:%S").time(),
            )
        )
        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("00:00:01", "%H:%M:%S").time(),
            )
        )
        assert ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("03:59:59", "%H:%M:%S").time(),
            )
        )
        assert not ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("04:00:00", "%H:%M:%S").time(),
            )
        )
        assert not ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("12:00:00", "%H:%M:%S").time(),
            )
        )
        assert not ps.is_in_period(
            dt.combine(
                dt.now(tz=pytz.timezone(TZ_AUS_SYD)),
                dt.strptime("19:59:59", "%H:%M:%S").time(),
            )
        )

    def test_period_schedule_duration_past(self):
        """
        Tests the period schedule for calculating duration in the past
        """

        ps = PeriodSchedule(
            "19:30:00",
            "07:00:00",
            tz="Australia/Sydney",
        )

        duration_since_last_start = ps.duration_since_last_start_datetime(
            dt.now(tz=pytz.timezone("Australia/Sydney"))
        )

        duration_since_last_end = ps.duration_since_last_end_datetime(
            dt.now(tz=pytz.timezone("Australia/Sydney"))
        )

        assert duration_since_last_start.total_seconds() >= 0
        assert duration_since_last_end.total_seconds() >= 0
        assert duration_since_last_start > duration_since_last_end

    def test_period_schedule_duration_future(self):
        """
        Tests the period schedule for calculating duration in the future
        """

        ps = PeriodSchedule(
            "19:30:00",
            "07:00:00",
            tz="Australia/Sydney",
        )

        duration_until_next_start = ps.duration_until_next_start_datetime(
            dt.now(tz=pytz.timezone("Australia/Sydney"))
        )
        duration_until_next_end = ps.duration_until_next_end_datetime(
            dt.now(tz=pytz.timezone("Australia/Sydney"))
        )

        assert duration_until_next_start.total_seconds() >= 0
        assert duration_until_next_end.total_seconds() >= 0
        assert duration_until_next_end > duration_until_next_start
