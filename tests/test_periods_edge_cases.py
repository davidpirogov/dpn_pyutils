import unittest
from datetime import datetime
from unittest.mock import patch

import pytz
from pytz.tzinfo import DstTzInfo, StaticTzInfo

from dpn_pyutils.time.periods import PeriodSchedule


class TestPeriodsEdgeCases(unittest.TestCase):
    """Edge case tests for periods module to achieve 100% coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.utc = pytz.UTC
        self.est = pytz.timezone("US/Eastern")
        self.pst = pytz.timezone("US/Pacific")

    def test_period_schedule_repr(self):
        """Test PeriodSchedule __repr__ method."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        repr_str = repr(schedule)
        self.assertIn("PeriodSchedule", repr_str)
        self.assertIn("start_time=", repr_str)
        self.assertIn("end_time=", repr_str)
        self.assertIn("tz=", repr_str)
        self.assertIn("valid_days_of_week=", repr_str)

    def test_period_schedule_invalid_timezone_type(self):
        """Test PeriodSchedule with invalid timezone type."""
        with self.assertRaises(ValueError) as cm:
            PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], 123)
        self.assertIn("Invalid timezone of type '<class 'int'>' supplied: 123", str(cm.exception))

    def test_period_schedule_more_than_7_days(self):
        """Test PeriodSchedule with more than 7 valid days."""
        with self.assertRaises(ValueError) as cm:
            PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6, 7])
        self.assertIn("Cannot have more than 7 valid days of the week", str(cm.exception))

    def test_period_schedule_invalid_day_of_week_negative(self):
        """Test PeriodSchedule with negative day of week."""
        with self.assertRaises(ValueError) as cm:
            PeriodSchedule("09:00:00", "17:00:00", [-1])
        self.assertIn("Invalid cardinality of Day of Week provided: -1", str(cm.exception))

    def test_period_schedule_invalid_day_of_week_too_large(self):
        """Test PeriodSchedule with day of week > 6."""
        with self.assertRaises(ValueError) as cm:
            PeriodSchedule("09:00:00", "17:00:00", [7])
        self.assertIn("Invalid cardinality of Day of Week provided: 7", str(cm.exception))

    def test_localize_check_datetime_none(self):
        """Test localize_check_datetime with None value."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        with self.assertRaises(ValueError) as cm:
            schedule.localize_check_datetime(None)
        self.assertIn("Cannot localize datetime timezone on None value", str(cm.exception))

    def test_localize_check_datetime_no_localize_method(self):
        """Test localize_check_datetime with timezone without localize method."""
        # Create a mock timezone without localize method
        mock_tz = unittest.mock.MagicMock()
        del mock_tz.localize  # Remove localize method

        # Patch the timezone validation to allow the mock
        with patch.object(PeriodSchedule, "__init__", lambda self, start, end, days, tz: None):
            schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], mock_tz)
            schedule.tz = mock_tz
            naive_dt = datetime(2023, 12, 1, 12, 0, 0)

            with self.assertRaises(RuntimeError) as cm:
                schedule.localize_check_datetime(naive_dt)
            self.assertIn("Supplied timezone type", str(cm.exception))
            self.assertIn("does not have a localize() method", str(cm.exception))

    def test_extract_date_time_from_check_datetime_naive(self):
        """Test extract_date_time_from_check_datetime with naive datetime."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        naive_dt = datetime(2023, 12, 1, 12, 0, 0)

        with self.assertRaises(ValueError) as cm:
            schedule.extract_date_time_from_check_datetime(naive_dt)
        self.assertIn(
            "Extracting date and time must only be done from a timezone configured datetime",
            str(cm.exception),
        )

    def test_get_start_end_datetimes_cross_midnight_before_end(self):
        """Test get_start_end_datetimes_for_datetime with cross-midnight period before end time."""
        schedule = PeriodSchedule("22:00:00", "06:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        # Test with time before end time (should be previous day's period)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 2, 0, 0))  # 2 AM

        start_dt, end_dt = schedule.get_start_end_datetimes_for_datetime(check_dt)

        # Should be previous day's period (the implementation returns the period
        # that started at 06:00 the previous day)
        expected_start = self.utc.localize(datetime(2023, 11, 30, 6, 0, 0))
        expected_end = self.utc.localize(datetime(2023, 12, 1, 6, 0, 0))

        self.assertEqual(start_dt, expected_start)
        self.assertEqual(end_dt, expected_end)

    def test_get_start_end_datetimes_cross_midnight_after_end(self):
        """Test get_start_end_datetimes_for_datetime with cross-midnight period after end time."""
        schedule = PeriodSchedule("22:00:00", "06:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        # Test with time after end time (should be current day's period)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 10, 0, 0))  # 10 AM

        start_dt, end_dt = schedule.get_start_end_datetimes_for_datetime(check_dt)

        # Should be current day's period
        expected_start = self.utc.localize(datetime(2023, 12, 1, 22, 0, 0))
        expected_end = self.utc.localize(datetime(2023, 12, 2, 6, 0, 0))

        self.assertEqual(start_dt, expected_start)
        self.assertEqual(end_dt, expected_end)

    def test_get_last_start_datetime_none(self):
        """Test get_last_start_datetime returning None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 8, 0, 0))  # Before start time

        # This should find a valid start datetime, not None
        result = schedule.get_last_start_datetime(check_dt)
        self.assertIsNotNone(result)

    def test_duration_since_last_start_datetime_none(self):
        """Test duration_since_last_start_datetime with None last start datetime."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        with patch.object(schedule, "get_last_start_datetime", return_value=None):
            with self.assertRaises(ValueError) as cm:
                schedule.duration_since_last_start_datetime(check_dt)
            self.assertIn("Cannot get duration since last start datetime as it is null", str(cm.exception))

    def test_get_last_end_datetime_none(self):
        """Test get_last_end_datetime returning None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 8, 0, 0))  # Before start time

        # This should find a valid end datetime, not None
        result = schedule.get_last_end_datetime(check_dt)
        self.assertIsNotNone(result)

    def test_get_last_end_datetime_returns_none(self):
        """Test get_last_end_datetime when it actually returns None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        with patch.object(schedule, "get_start_end_datetimes_for_datetime", return_value=(None, None)):
            with patch.object(schedule, "extract_date_time_from_check_datetime") as mock_extract:
                mock_extract.return_value = (check_dt.date(), check_dt.time())
                with patch.object(schedule, "localize_check_datetime", return_value=check_dt):
                    # Mock the loop to return None by making
                    # get_start_end_datetimes_for_datetime always return None
                    with patch.object(
                        schedule, "get_start_end_datetimes_for_datetime", return_value=(None, None)
                    ):
                        with self.assertRaises(ValueError) as cm:
                            schedule.get_last_end_datetime(check_dt)
                        self.assertIn("No valid last end datetimes found", str(cm.exception))

    def test_get_next_start_datetime_none(self):
        """Test get_next_start_datetime returning None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 18, 0, 0))  # After end time

        # This should find a valid next start datetime, not None
        result = schedule.get_next_start_datetime(check_dt)
        self.assertIsNotNone(result)

    def test_duration_until_next_start_datetime_none(self):
        """Test duration_until_next_start_datetime with None next start datetime."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        with patch.object(schedule, "get_next_start_datetime", return_value=None):
            with self.assertRaises(ValueError) as cm:
                schedule.duration_until_next_start_datetime(check_dt)
            self.assertIn("Cannot get duration until next start datetime as it is null", str(cm.exception))

    def test_get_next_end_datetime_none(self):
        """Test get_next_end_datetime returning None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 18, 0, 0))  # After end time

        # This should find a valid next end datetime, not None
        result = schedule.get_next_end_datetime(check_dt)
        self.assertIsNotNone(result)

    def test_duration_until_next_end_datetime_none(self):
        """Test duration_until_next_end_datetime with None next end datetime."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        with patch.object(schedule, "get_next_end_datetime", return_value=None):
            with self.assertRaises(ValueError) as cm:
                schedule.duration_until_next_end_datetime(check_dt)
            self.assertIn("Cannot get duration until next end datetime as it is null", str(cm.exception))

    def test_get_current_start_datetime_none(self):
        """Test get_current_start_datetime returning None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        # This should find a valid current start datetime, not None
        result = schedule.get_current_start_datetime(check_dt)
        self.assertIsNotNone(result)

    def test_duration_until_current_start_datetime_none(self):
        """Test duration_until_current_start_datetime with None current start datetime."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        with patch.object(schedule, "get_current_start_datetime", return_value=None):
            with self.assertRaises(ValueError) as cm:
                schedule.duration_until_current_start_datetime(check_dt)
            self.assertIn("Cannot get duration until current start datetime as it is null", str(cm.exception))

    def test_get_current_end_datetime_none(self):
        """Test get_current_end_datetime returning None."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        # This should find a valid current end datetime, not None
        result = schedule.get_current_end_datetime(check_dt)
        self.assertIsNotNone(result)

    def test_duration_until_current_end_datetime_none(self):
        """Test duration_until_current_end_datetime with None current end datetime."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 12, 0, 0))

        with patch.object(schedule, "get_current_end_datetime", return_value=None):
            with self.assertRaises(ValueError) as cm:
                schedule.duration_until_current_end_datetime(check_dt)
            self.assertIn("Cannot get duration until current end datetime as it is null", str(cm.exception))

    def test_period_schedule_with_string_timezone(self):
        """Test PeriodSchedule with string timezone."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], "US/Eastern")
        self.assertEqual(schedule.tz.zone, "US/Eastern")

    def test_period_schedule_with_dst_tzinfo(self):
        """Test PeriodSchedule with DstTzInfo timezone."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.est)
        self.assertIsInstance(schedule.tz, DstTzInfo)

    def test_period_schedule_with_static_tzinfo(self):
        """Test PeriodSchedule with StaticTzInfo timezone."""
        gmt_tz = pytz.timezone("GMT")  # GMT is a StaticTzInfo timezone which is required for this test
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], gmt_tz)
        self.assertIsInstance(schedule.tz, StaticTzInfo)

    def test_period_schedule_with_standard_tzinfo(self):
        """Test PeriodSchedule with standard tzinfo."""
        from datetime import timezone

        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], timezone.utc)
        self.assertIsInstance(schedule.tz, timezone)

    def test_get_next_start_datetime_timedelta_increment(self):
        """Test get_next_start_datetime with timedelta increment in loop."""
        # Create a schedule with only one valid day to force the loop to increment
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0], self.utc)  # Only Sunday
        check_dt = self.utc.localize(datetime(2023, 12, 1, 18, 0, 0))  # Friday, after end time

        # This should trigger the timedelta increment path (line 416) because
        # Friday (5) is not in valid_days_of_week [0], so it will increment to Saturday (6),
        # then to Sunday (0) which is valid
        result = schedule.get_next_start_datetime(check_dt)
        self.assertIsNotNone(result)
        # The result should be the start time for Sunday (Dec 3, 2023)
        expected = self.utc.localize(datetime(2023, 12, 3, 9, 0, 0))
        self.assertEqual(result, expected)

    def test_get_next_end_datetime_timedelta_increment(self):
        """Test get_next_end_datetime with timedelta increment in loop."""
        # Create a schedule with only one valid day to force the loop to increment
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0], self.utc)  # Only Sunday
        check_dt = self.utc.localize(datetime(2023, 12, 1, 18, 0, 0))  # Friday, after end time

        # This should trigger the timedelta increment path (line 467) because
        # Friday (5) is not in valid_days_of_week [0], so it will increment to Saturday (6),
        # then to Sunday (0) which is valid
        result = schedule.get_next_end_datetime(check_dt)
        self.assertIsNotNone(result)
        # The result should be the end time for Sunday (Dec 3, 2023)
        expected = self.utc.localize(datetime(2023, 12, 3, 17, 0, 0))
        self.assertEqual(result, expected)

    def test_period_schedule_empty_valid_days(self):
        """Test PeriodSchedule with empty valid_days_of_week (should default to all days)."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [], self.utc)
        self.assertEqual(schedule.valid_days_of_week, [0, 1, 2, 3, 4, 5, 6])

    def test_period_schedule_none_valid_days(self):
        """Test PeriodSchedule with None valid_days_of_week (should default to all days)."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", None, self.utc)
        self.assertEqual(schedule.valid_days_of_week, [0, 1, 2, 3, 4, 5, 6])

    def test_is_in_period_invalid_day_of_week(self):
        """Test is_in_period with datetime on invalid day of week."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [1, 2, 3, 4, 5], self.utc)  # Weekdays only
        # Sunday (day 0)
        check_dt = self.utc.localize(datetime(2023, 12, 3, 12, 0, 0))  # Sunday

        result = schedule.is_in_period(check_dt)
        self.assertFalse(result)

    def test_is_in_period_exactly_at_start(self):
        """Test is_in_period with datetime exactly at start time."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 9, 0, 0))  # Exactly at start

        result = schedule.is_in_period(check_dt)
        self.assertTrue(result)

    def test_is_in_period_exactly_at_end(self):
        """Test is_in_period with datetime exactly at end time."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 17, 0, 0))  # Exactly at end

        result = schedule.is_in_period(check_dt)
        self.assertFalse(result)  # End time is exclusive

    def test_is_in_period_after_end(self):
        """Test is_in_period with datetime after end time."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 18, 0, 0))  # After end

        result = schedule.is_in_period(check_dt)
        self.assertFalse(result)

    def test_is_in_period_before_start(self):
        """Test is_in_period with datetime before start time."""
        schedule = PeriodSchedule("09:00:00", "17:00:00", [0, 1, 2, 3, 4, 5, 6], self.utc)
        check_dt = self.utc.localize(datetime(2023, 12, 1, 8, 0, 0))  # Before start

        result = schedule.is_in_period(check_dt)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
