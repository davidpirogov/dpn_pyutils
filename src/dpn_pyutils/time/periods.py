"""
Defines timezone-aware periods
"""
from datetime import datetime as dt
from datetime import time, timedelta, tzinfo
from typing import List, Union

import pytz
from pytz.tzinfo import DstTzInfo, StaticTzInfo

from dpn_pyutils.common import get_logger

log = get_logger(__name__)


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

class PeriodSchedule:
    """
    Defines a schedule to manage a period of time that is inclusive of start time and exclusive of
    end time as well as being timezone aware.
    """

    period_start_time_of_day: str = None
    period_end_time_of_day: str = None
    valid_days_of_week: List[int] = [0, 1, 2, 3, 4, 5, 6]
    tz: Union[tzinfo, DstTzInfo, StaticTzInfo] = None

    start_time: time = None
    end_time: time = None

    def __repr__(self) -> str:
        return (
            f"<PeriodSchedule start_time={self.start_time} "
            f"end_time={self.end_time} "
            f"tz={self.tz} "
            f"valid_days_of_week={self.valid_days_of_week} />"
        )

    def __init__(
        self,
        period_start_time_of_day: str,
        period_end_time_of_day: str,
        valid_days_of_week: List[int] = None,
        tz: Union[tzinfo, DstTzInfo, StaticTzInfo, str] = None,
    ) -> None:
        """
        Create a period schedule with a start time of day, end time of day, and days of the week
        that this period schedule is applicable to, inclusive of start time and until, excluding
        end time

        :param period_start_time_of_day String in the form of "HH:MM:SS" in 24-hour time
        :param period_end_time_of_day   String in the form of "HH:MM:SS" in 24-hour time
        :param valid_days_of_week       List of days where Sunday=0 ... Saturday=6. If the list is
                                        empty or None, every day is considered a valid day
        """

        # Ensure that supplied strings are valid
        self.start_time = dt.strptime(period_start_time_of_day, TIME_FORMAT).time()
        self.period_start_time_of_day = period_start_time_of_day

        self.end_time = dt.strptime(period_end_time_of_day, TIME_FORMAT).time()
        self.period_end_time_of_day = period_end_time_of_day

        if valid_days_of_week is not None and len(valid_days_of_week) > 0:
            if len(valid_days_of_week) > 7:
                raise ValueError(
                    "Cannot have more than 7 valid days of the week and "
                    f"{len(valid_days_of_week)} valid days provided. They are: "
                    f"{valid_days_of_week}"
                )

            for vd in valid_days_of_week:
                if vd < 0 or vd > 6:
                    raise ValueError(
                        f"Invalid cardinality of Day of Week provided: {vd}. Must "
                        "be between 0 (Sunday) through to 6 (Saturday)."
                    )

            self.valid_days_of_week = valid_days_of_week

        if tz is None:
            self.tz = pytz.timezone("UTC")
        elif type(tz) is str:
            self.tz = pytz.timezone(tz)
        elif type(tz) is tzinfo or type(tz) is StaticTzInfo or type(tz) is DstTzInfo:
            self.tz = tz
        else:
            raise ValueError(f"Invalid timezone of type '{type(tz)}' supplied: {tz}")

    def is_in_period(self, check_datetime: dt) -> bool:
        """
        Checks if the supplied datetime is in the configured period
        """

        check_date = self.tz.localize(check_datetime).date()
        if int(check_date.strftime("%w")) not in self.valid_days_of_week:
            return False

        check_time = self.tz.localize(check_datetime).time()
        if self.end_time < self.start_time and check_time < self.end_time:
            check_start_datetime = self.tz.localize(
                dt.combine(check_date - timedelta(days=1), self.end_time)
            )
            check_end_datetime = self.tz.localize(dt.combine(check_date, self.end_time))

        elif self.end_time < self.start_time and check_time > self.end_time:
            check_start_datetime = self.tz.localize(
                dt.combine(check_date, self.start_time)
            )
            check_end_datetime = self.tz.localize(
                dt.combine(check_date + timedelta(days=1), self.end_time)
            )
        else:
            check_start_datetime = self.tz.localize(
                dt.combine(check_date, self.start_time)
            )
            check_end_datetime = self.tz.localize(dt.combine(check_date, self.end_time))

        if check_start_datetime <= self.tz.localize(
            check_datetime
        ) and check_end_datetime > self.tz.localize(check_datetime):
            return True

        return False
