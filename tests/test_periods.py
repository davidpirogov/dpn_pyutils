import unittest
from datetime import datetime, time, timedelta

import pytz

from src.dpn_pyutils.time.periods import TIME_FORMAT, PeriodSchedule

TZ_AUS_SYD = "Australia/Sydney"


class TestPeriodSchedule(unittest.TestCase):
    period_schedule_params = {
        "period_start_time_of_day": "09:00:00",
        "period_end_time_of_day": "17:30:00",
        "valid_days_of_week": [1, 2, 3],
    }

    def setUp(self):
        self.period = PeriodSchedule(
            "08:00:00",
            "17:00:00",
            valid_days_of_week=[0, 1, 2, 3, 4, 5, 6],
            tz="America/New_York",
        )

    def get_period_schedule(self) -> PeriodSchedule:
        return PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
        )

    def get_period_schedule_across_days(self) -> PeriodSchedule:
        """
        Create a period of time overnight between 1930 -> 0715
        """
        return PeriodSchedule(
            "19:30:00",
            "07:15:00",
        )

    def get_period_schedule_week_valid_invalid_dates(self) -> dict:
        """
        Returns set of valid_dates, invalid_dates and valid_days_of_week based
        on the next 7 days
        """

        test_dates = [
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)),
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=1),
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=2),
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=3),
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=4),
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=5),
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD)) + timedelta(days=6),
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

    def period_schedule_valid_invalid_days_next_week(self):
        """
        Creates a period schedule for the next week based on a select number of valid/invalid days
        """

        return PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
            self.get_period_schedule_week_valid_invalid_dates()["valid_days_of_week"],
            tz=TZ_AUS_SYD,
        )

    def get_period_schedule_valid_invalid_days_next_week_across_days(self):
        """
        Creates a period schedule for the next week based on a select number of valid/invalid days
        """

        return PeriodSchedule(
            "19:15:00",
            "09:49:00",
            self.get_period_schedule_week_valid_invalid_dates()["valid_days_of_week"],
        )

    # def test_is_in_period(self):
    #     # Test a datetime within the period
    #     test_dt = datetime(2022, 1, 1, 10, 0, 0)
    #     self.assertTrue(self.period.is_in_period(test_dt))

    #     # Test a datetime outside the period
    #     test_dt = datetime(2022, 1, 1, 18, 0, 0)
    #     self.assertFalse(self.period.is_in_period(test_dt))

    # def test_get_last_start_datetime(self):
    #     # Test getting the last start datetime
    #     test_dt = datetime(2022, 1, 1, 10, 0, 0)
    #     last_start_dt = self.period.get_last_start_datetime(test_dt)
    #     expected_dt = datetime(2021, 12, 31, 8, 0, 0)
    #     self.assertEqual(last_start_dt, expected_dt)

    # def test_duration_since_last_start_datetime(self):
    #     # Test getting the duration since the last start datetime
    #     test_dt = datetime(2022, 1, 1, 10, 0, 0)
    #     duration = self.period.duration_since_last_start_datetime(test_dt)
    #     expected_duration = timedelta(days=2, hours=2)
    #     self.assertEqual(duration, expected_duration)

    # def test_get_last_end_datetime(self):
    #     # Test getting the last end datetime
    #     test_dt = datetime(2022, 1, 1, 10, 0, 0)
    #     last_end_dt = self.period.get_last_end_datetime(test_dt)
    #     expected_dt = datetime(
    #         2021, 12, 31, 17, 0, 0, tzinfo=pytz.timezone("America/New_York")
    #     )
    #     print(last_end_dt)
    #     print(expected_dt)
    #     self.assertEqual(last_end_dt, expected_dt)

    def test_duration_since_last_end_datetime(self):
        # Test getting the duration since the last end datetime
        test_dt = datetime(2022, 1, 1, 10, 0, 0)
        duration = self.period.duration_since_last_end_datetime(test_dt)
        expected_duration = timedelta(days=-1, hours=17)
        self.assertEqual(duration, expected_duration)

    def test_period_schedule_init(self):
        """
        Tests that the period schedule can be established correctly
        """

        ps = PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
        )

        self.assertEqual(
            ps.period_start_time_of_day,
            self.period_schedule_params["period_start_time_of_day"],
        )
        self.assertEqual(
            ps.period_end_time_of_day,
            self.period_schedule_params["period_end_time_of_day"],
        )

        self.assertTrue(isinstance(ps.start_time, time))
        self.assertTrue(isinstance(ps.end_time, time))

    def test_period_schedule_init_valid_days(self):
        """
        Tests that the number of valid days is set correctly
        """

        ps = PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
            self.period_schedule_params["valid_days_of_week"],
        )

        self.assertTrue(
            set(self.period_schedule_params["valid_days_of_week"]).issuperset(
                set(ps.valid_days_of_week)
            )
        )

    def test_period_schedule_init_invalid_num_days(self):
        """
        Tests that the number of valid days is set incorrectly and raises an error
        """

        with self.assertRaises(ValueError):
            PeriodSchedule(
                self.period_schedule_params["period_start_time_of_day"],
                self.period_schedule_params["period_end_time_of_day"],
                [0, 1, 2, 3, 4, 5, 6, 7],  # Should fail due to >7 days
            )

    def test_period_schedule_init_valid_num_days_cardinality(self):
        """
        Tests that the valid days have correct cardinality (0 - 6)
        """

        ps = PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
            self.period_schedule_params["valid_days_of_week"],
        )

        self.assertTrue(
            set(self.period_schedule_params["valid_days_of_week"]).issuperset(
                set(ps.valid_days_of_week)
            )
        )

    def test_period_schedule_init_invalid_num_days_cardinality(self):
        """
        Tests that the invalid days throw an exception with cardinality (0 - 6)
        """

        with self.assertRaises(ValueError):
            PeriodSchedule(
                self.period_schedule_params["period_start_time_of_day"],
                self.period_schedule_params["period_end_time_of_day"],
                [-1, 0, 1, 2],  # Should fail due to value < 0
            )

        with self.assertRaises(ValueError):
            PeriodSchedule(
                self.period_schedule_params["period_start_time_of_day"],
                self.period_schedule_params["period_end_time_of_day"],
                [4, 5, 6, 7],  # Should fail due to value > 6
            )

    def test_period_schedule_before_period(self):
        """
        Tests that today's date with times before the period are marked as such
        """

        self.assertFalse(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("00:00:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("08:59:59", "%H:%M:%S").time(),
                )
            )
        )

    def test_period_schedule_inside_period(self):
        """
        Tests that today's date with times inside the period are marked as such
        """

        self.assertTrue(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("09:00:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("09:00:01", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("13:45:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("17:29:59", "%H:%M:%S").time(),
                )
            )
        )

    def test_period_schedule_after_period(self):
        """
        Tests that today's date with times after the period are marked as such
        """

        self.assertFalse(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("17:30:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("17:30:01", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("23:59:59", "%H:%M:%S").time(),
                )
            )
        )

    def test_period_schedule_next_day_before_period(self):
        """
        Tests that today's date with times before the period are marked as such
        """

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("07:15:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("07:15:01", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("08:59:59", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("19:29:59", "%H:%M:%S").time(),
                )
            )
        )

    def test_period_schedule_next_day_inside_period(self):
        """
        Tests that today's date and tomorrow's date with times during the period are marked as such
        """

        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("19:30:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("19:30:01", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date(),
                    datetime.strptime("23:59:59", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("00:00:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("00:00:01", "%H:%M:%S").time(),
                )
            )
        )

        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("07:14:59", "%H:%M:%S").time(),
                )
            )
        )

    def test_period_schedule_next_day_after_period(self):
        """
        Tests that today's date and tomorrow's date with times after the period are marked as such
        """

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("07:15:00", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("07:15:01", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("09:30:59", "%H:%M:%S").time(),
                )
            )
        )

        self.assertFalse(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("19:29:59", "%H:%M:%S").time(),
                )
            )
        )

        # Note: This is inside the next day's period schedule
        self.assertTrue(
            self.get_period_schedule_across_days().is_in_period(
                datetime.combine(
                    datetime.now().date() + timedelta(days=1),
                    datetime.strptime("19:30:00", "%H:%M:%S").time(),
                )
            )
        )

    def test_period_schedule_valid_days_period(
        self,
    ):
        """
        Tests the next week's time period for valid days
        """

        for d in self.get_period_schedule_week_valid_invalid_dates()["valid_dates"]:
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("00:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("08:59:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:00:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:29:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:30:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:30:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )

    def test_period_schedule_invalid_days_period(self):
        """
        Tests the next week's time period for valid days -- all should be not valid
        """

        for d in self.get_period_schedule_week_valid_invalid_dates()["invalid_dates"]:
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("00:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("08:59:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:00:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:29:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:30:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:30:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.period_schedule_valid_invalid_days_next_week().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )

    def test_period_schedule_valid_days_period_across_days(
        self,
    ):
        """
        Tests the next week's time period for valid days
        """

        for d in self.get_period_schedule_week_valid_invalid_dates()["valid_dates"]:
            self.assertTrue(
                self.get_period_schedule_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("00:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:48:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:49:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:49:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("19:14:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("19:15:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("19:15:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertTrue(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )

    def test_period_schedule_invalid_days_period_across_days(
        self,
    ):
        """
        Tests the next week's time period for valid days -- all should be not valid
        """

        for d in self.get_period_schedule_week_valid_invalid_dates()["invalid_dates"]:
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("00:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("08:59:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:00:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("09:00:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:29:59", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:30:00", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("17:30:01", "%H:%M:%S").time(),
                    )
                )
            )
            self.assertFalse(
                self.get_period_schedule_valid_invalid_days_next_week_across_days().is_in_period(
                    datetime.combine(
                        d.date(),
                        datetime.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )

    def test_period_schedule_tz_valid_str(self):
        """
        Tests that the period schedule can be established correctly with timezone support
        """

        ps = PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
            tz=TZ_AUS_SYD,
        )

        self.assertTrue(isinstance(ps.start_time, time))
        self.assertEqual(
            ps.period_start_time_of_day,
            self.period_schedule_params["period_start_time_of_day"],
        )

        self.assertTrue(isinstance(ps.end_time, time))
        self.assertEqual(
            ps.period_end_time_of_day,
            self.period_schedule_params["period_end_time_of_day"],
        )

        self.assertFalse(isinstance(ps.tz, str))
        self.assertTrue(ps.tz.zone, TZ_AUS_SYD)  # type: ignore

    def test_period_schedule_tz_valid_time_period_day(self):
        """
        Tests that the period schedule can be established correctly with timezone support
        """

        ps = PeriodSchedule(
            self.period_schedule_params["period_start_time_of_day"],
            self.period_schedule_params["period_end_time_of_day"],
            tz=TZ_AUS_SYD,
        )

        self.assertFalse(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("08:59:59", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("09:00:00", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("09:00:01", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("17:29:59", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertFalse(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("17:30:00", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertFalse(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )
        )

    def test_period_schedule_tz_valid_time_period_across_day(self):
        """
        Tests that the period schedule can be established correctly with timezone support
        """
        ps = PeriodSchedule(
            "20:00:00",
            "04:00:00",
            tz=TZ_AUS_SYD,
        )

        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("23:59:59", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("00:00:00", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("00:00:01", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertTrue(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("03:59:59", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertFalse(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("04:00:00", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertFalse(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("12:00:00", "%H:%M:%S").time(),
                    )
                )
            )
        )
        self.assertFalse(
            ps.is_in_period(
                pytz.timezone(TZ_AUS_SYD).localize(
                    datetime.combine(
                        datetime.now(),
                        datetime.strptime("19:59:59", "%H:%M:%S").time(),
                    )
                )
            )
        )

    def test_period_schedule_duration_past(self):
        """
        Tests the period schedule for calculating duration in the past
        """

        current_time = datetime.now()
        ps_start = (current_time - timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps_end = (current_time - timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_since_last_start = ps.duration_since_last_start_datetime(
            datetime.now()
        )

        duration_since_last_end = ps.duration_since_last_end_datetime(datetime.now())

        self.assertGreaterEqual(duration_since_last_start.total_seconds(), 0)
        self.assertGreaterEqual(duration_since_last_end.total_seconds(), 0)
        self.assertGreater(duration_since_last_start, duration_since_last_end)

    def test_period_schedule_duration_future(self):
        """
        Tests the period schedule for calculating duration in the future
        """

        current_time = datetime.now()
        ps_start = (current_time + timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps_end = (current_time + timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_until_next_start = ps.duration_until_next_start_datetime(
            datetime.now()
        )
        duration_until_next_end = ps.duration_until_next_end_datetime(datetime.now())

        self.assertGreaterEqual(duration_until_next_start.total_seconds(), 0)
        self.assertGreaterEqual(duration_until_next_end.total_seconds(), 0)
        self.assertGreater(duration_until_next_end, duration_until_next_start)

    def test_period_schedule_tz_aware_duration_past(self):
        """
        Tests the period schedule for calculating duration in the past
        """

        current_time = datetime.now()
        ps_start = (current_time - timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps_end = (current_time - timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_since_last_start = ps.duration_since_last_start_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )

        duration_since_last_end = ps.duration_since_last_end_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )

        self.assertGreaterEqual(duration_since_last_start.total_seconds(), 0)
        self.assertGreaterEqual(duration_since_last_end.total_seconds(), 0)
        self.assertGreater(duration_since_last_start, duration_since_last_end)

    def test_period_schedule_tz_aware_duration_future(self):
        """
        Tests the period schedule for calculating duration in the future
        """

        current_time = datetime.now()
        ps_start = (current_time + timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps_end = (current_time + timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_until_next_start = ps.duration_until_next_start_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )
        duration_until_next_end = ps.duration_until_next_end_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )

        self.assertGreaterEqual(duration_until_next_start.total_seconds(), 0)
        self.assertGreaterEqual(duration_until_next_end.total_seconds(), 0)
        self.assertGreater(duration_until_next_end, duration_until_next_start)

    def test_period_schedule_duration_current_past(self):
        """
        Tests the period schedule for calculating duration currently
        """

        current_time = datetime.now()
        ps_start = (current_time - timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps_end = (current_time - timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_current_start = ps.duration_until_current_start_datetime(
            datetime.now()
        )
        duration_current_end = ps.duration_until_current_end_datetime(datetime.now())

        # Since the duration is in the past, it has negative duration values
        self.assertLess(duration_current_start.total_seconds(), 0)
        self.assertLess(duration_current_end.total_seconds(), 0)
        self.assertGreater(duration_current_end, duration_current_start)

    def test_period_schedule_duration_current_between_start_end(self):
        """
        Tests the period schedule for calculating duration currently
        """

        current_time = datetime.now()
        ps_start = (current_time - timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps_end = (current_time + timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_current_start = ps.duration_until_current_start_datetime(
            datetime.now()
        )
        duration_current_end = ps.duration_until_current_end_datetime(datetime.now())

        # Since the current_start duration is in the past, it has negative duration values
        # Since the current_start duration is in the future, it has positive duration values
        self.assertLess(duration_current_start.total_seconds(), 0)
        self.assertGreater(duration_current_end.total_seconds(), 0)
        self.assertGreater(duration_current_end, duration_current_start)

    def test_period_schedule_duration_current_future(self):
        """
        Tests the period schedule for calculating duration currently
        """

        current_time = datetime.now()
        ps_start = (current_time + timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps_end = (current_time + timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_current_start = ps.duration_until_current_start_datetime(
            datetime.now()
        )
        duration_current_end = ps.duration_until_current_end_datetime(datetime.now())

        # Since the duration is in the future, it has positive duration values
        self.assertGreater(duration_current_start.total_seconds(), 0)
        self.assertGreater(duration_current_end.total_seconds(), 0)
        self.assertGreater(duration_current_end, duration_current_start)

    def test_period_schedule_tz_aware_duration_current_past(self):
        """
        Tests the period schedule for calculating duration currently
        """

        current_time = datetime.now(pytz.timezone(TZ_AUS_SYD))
        ps_start = (current_time - timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps_end = (current_time - timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_current_start = ps.duration_until_current_start_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )
        duration_current_end = ps.duration_until_current_end_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )

        # Since the duration is in the past, it has negative duration values
        self.assertLess(duration_current_start.total_seconds(), 0)
        self.assertLess(duration_current_end.total_seconds(), 0)
        self.assertLess(duration_current_start, duration_current_end)

    def test_period_schedule_tz_aware_duration_current_between_start_end(self):
        """
        Tests the period schedule for calculating duration currently
        """

        current_time = datetime.now(pytz.timezone(TZ_AUS_SYD))
        ps_start = (current_time - timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps_end = (current_time + timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_current_start = ps.duration_until_current_start_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )
        duration_current_end = ps.duration_until_current_end_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )

        # Since the current_start duration is in the past, it has negative duration values
        # Since the current_start duration is in the future, it has positive duration values
        self.assertLess(duration_current_start.total_seconds(), 0)
        self.assertLess(0, duration_current_end.total_seconds())
        self.assertLess(duration_current_start, duration_current_end)

    def test_period_schedule_tz_aware_duration_current_future(self):
        """
        Tests the period schedule for calculating duration currently
        """

        current_time = datetime.now(pytz.timezone(TZ_AUS_SYD))
        ps_start = (current_time + timedelta(hours=1)).time().strftime(TIME_FORMAT)
        ps_end = (current_time + timedelta(hours=2)).time().strftime(TIME_FORMAT)
        ps = PeriodSchedule(ps_start, ps_end, tz=TZ_AUS_SYD)

        duration_current_start = ps.duration_until_current_start_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )
        duration_current_end = ps.duration_until_current_end_datetime(
            datetime.now(tz=pytz.timezone(TZ_AUS_SYD))
        )

        # Since the duration is in the future, it has positive duration values
        self.assertGreater(duration_current_start.total_seconds(), 0)
        self.assertGreater(duration_current_end.total_seconds(), 0)
        self.assertGreater(duration_current_end, duration_current_start)


if __name__ == "__main__":
    unittest.main()
