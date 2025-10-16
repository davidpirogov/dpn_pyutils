# Time Package Documentation

## About

The `dpn_pyutils.time` package provides sophisticated timezone-aware time period management and scheduling utilities. This package enables applications to work with recurring time periods, handle timezone conversions, and perform temporal calculations with full awareness of daylight saving time and timezone differences.

The package is designed for applications that need to manage scheduled operations, handle time-based business logic, work with recurring events, or perform timezone-aware temporal calculations. It's particularly useful for scheduling systems, calendar applications, trading platforms, and any system that operates across multiple timezones.

## Examples

### Basic Period Schedule

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

# Create a period schedule for business hours (9 AM - 5 PM, weekdays only)
business_hours = PeriodSchedule(
    period_start_time_of_day="09:00:00",
    period_end_time_of_day="17:00:00",
    valid_days_of_week=[1, 2, 3, 4, 5],  # Monday to Friday
    tz="America/New_York"
)

# Check if current time is within business hours
now = datetime.now(pytz.timezone("America/New_York"))
is_business_hours = business_hours.is_in_period(now)
print(f"Is it business hours? {is_business_hours}")
```

### Trading Hours Schedule

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

# NYSE trading hours (9:30 AM - 4:00 PM ET, weekdays)
nyse_hours = PeriodSchedule(
    period_start_time_of_day="09:30:00",
    period_end_time_of_day="16:00:00",
    valid_days_of_week=[1, 2, 3, 4, 5],  # Monday to Friday
    tz="America/New_York"
)

# Check if market is open
current_time = datetime.now(pytz.timezone("America/New_York"))
market_open = nyse_hours.is_in_period(current_time)
print(f"NYSE Open: {market_open}")
```

### Overnight Period (spans midnight)

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

# Night shift (11 PM - 7 AM)
night_shift = PeriodSchedule(
    period_start_time_of_day="23:00:00",
    period_end_time_of_day="07:00:00",
    valid_days_of_week=[0, 1, 2, 3, 4, 5, 6],  # Every day
    tz="UTC"
)

# Check if it's night shift time
utc_now = datetime.now(pytz.UTC)
on_night_shift = night_shift.is_in_period(utc_now)
print(f"Night shift active: {on_night_shift}")
```

### Multi-Timezone Support

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

# Global support hours (8 AM - 8 PM Pacific Time)
support_hours = PeriodSchedule(
    period_start_time_of_day="08:00:00",
    period_end_time_of_day="20:00:00",
    valid_days_of_week=[1, 2, 3, 4, 5, 6],  # Monday to Saturday
    tz="America/Los_Angeles"
)

# Check from different timezones
pacific_time = datetime.now(pytz.timezone("America/Los_Angeles"))
eastern_time = datetime.now(pytz.timezone("America/New_York"))
london_time = datetime.now(pytz.timezone("Europe/London"))

print(f"Support available in Pacific: {support_hours.is_in_period(pacific_time)}")
print(f"Support available in Eastern: {support_hours.is_in_period(eastern_time)}")
print(f"Support available in London: {support_hours.is_in_period(london_time)}")
```

### Time Until Next Period

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

# Maintenance window (Sunday 2-4 AM UTC)
maintenance_window = PeriodSchedule(
    period_start_time_of_day="02:00:00",
    period_end_time_of_day="04:00:00",
    valid_days_of_week=[0],  # Sunday only
    tz="UTC"
)

now = datetime.now(pytz.UTC)

# Get time until next maintenance window
time_until = maintenance_window.duration_until_next_start_datetime(now)
print(f"Time until next maintenance: {time_until}")

# Get time until current/next end (if in window)
if maintenance_window.is_in_period(now):
    time_until_end = maintenance_window.duration_until_next_end_datetime(now)
    print(f"Time until maintenance ends: {time_until_end}")
```

### Duration Calculations

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

# Work shift (9 AM - 5 PM)
work_shift = PeriodSchedule(
    period_start_time_of_day="09:00:00",
    period_end_time_of_day="17:00:00",
    valid_days_of_week=[1, 2, 3, 4, 5],
    tz="America/Chicago"
)

now = datetime.now(pytz.timezone("America/Chicago"))

# Duration since last shift start
since_start = work_shift.duration_since_last_start_datetime(now)
print(f"Time since last shift start: {since_start}")

# Duration until next shift start
until_next = work_shift.duration_until_next_start_datetime(now)
print(f"Time until next shift start: {until_next}")

# If currently in shift, get time until end
if work_shift.is_in_period(now):
    until_end = work_shift.duration_until_current_end_datetime(now)
    print(f"Time until shift ends: {until_end}")
```

### Scheduling Application

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime, timedelta
import pytz

class TaskScheduler:
    def __init__(self):
        self.task_schedule = PeriodSchedule(
            period_start_time_of_day="06:00:00",
            period_end_time_of_day="18:00:00",
            valid_days_of_week=[1, 2, 3, 4, 5],  # Weekdays
            tz="UTC"
        )

    def can_run_task(self, check_time=None):
        """Check if a task can run at the given time."""
        if check_time is None:
            check_time = datetime.now(pytz.UTC)
        return self.task_schedule.is_in_period(check_time)

    def get_next_run_time(self, from_time=None):
        """Get the next time when task can run."""
        if from_time is None:
            from_time = datetime.now(pytz.UTC)
        return self.task_schedule.get_next_start_datetime(from_time)

    def schedule_task(self, task_name, run_time=None):
        """Schedule a task to run at the appropriate time."""
        if run_time is None:
            run_time = datetime.now(pytz.UTC)

        if self.can_run_task(run_time):
            print(f"Running {task_name} immediately")
            return run_time
        else:
            next_run = self.get_next_run_time(run_time)
            print(f"Scheduling {task_name} for {next_run}")
            return next_run

# Usage
scheduler = TaskScheduler()
now = datetime.now(pytz.UTC)

# Check if we can run tasks now
can_run = scheduler.can_run_task(now)
print(f"Can run tasks now: {can_run}")

# Schedule some tasks
scheduler.schedule_task("data_backup")
scheduler.schedule_task("report_generation")
```

## Architecture

### Design Philosophy

The time package is built around these core principles:

1. **Timezone Awareness**: All time calculations respect timezone and DST rules
2. **Period Definition**: Clear definition of recurring time periods with flexible scheduling
3. **Temporal Logic**: Sophisticated handling of time periods that may span midnight
4. ** pytz Integration**: Leverages the robust `pytz` library for timezone handling
5. **Immutable Periods**: Period definitions are immutable for thread safety

### Core Components

#### PeriodSchedule Class
The `PeriodSchedule` class is the central component that encapsulates:

- **Time Range**: Start and end times within a day
- **Day Selection**: Which days of the week the period applies to
- **Timezone Context**: The timezone for all time calculations
- **Period Logic**: Complex logic for handling periods that span midnight

### Timezone Handling

#### Supported Timezone Formats
```python
# String timezone names (requires pytz)
schedule = PeriodSchedule(
    period_start_time_of_day="09:00:00",
    period_end_time_of_day="17:00:00",
    tz="America/New_York"  # String name
)

# Timezone objects
import pytz
eastern_tz = pytz.timezone("America/New_York")
schedule = PeriodSchedule(
    period_start_time_of_day="09:00:00",
    period_end_time_of_day="17:00:00",
    tz=eastern_tz  # Timezone object
)

# tzinfo objects (from datetime)
from datetime import timezone, timedelta
utc_tz = timezone(timedelta(hours=0))
schedule = PeriodSchedule(
    period_start_time_of_day="09:00:00",
    period_end_time_of_day="17:00:00",
    tz=utc_tz  # tzinfo object
)
```

#### Automatic Localization
The class automatically handles timezone conversion:

```python
# Naive datetime (no timezone) -> automatically localized to schedule timezone
naive_time = datetime(2024, 1, 15, 14, 30, 0)  # No timezone
localized_time = schedule.localize_check_datetime(naive_time)

# Aware datetime -> converted to schedule timezone
eastern_time = datetime.now(pytz.timezone("America/New_York"))
utc_time = schedule.localize_check_datetime(eastern_time)  # Converted to schedule TZ
```

### Period Logic Implementation

#### Midnight-Spanning Periods
The class handles periods that cross midnight boundary:

```python
# Night shift: 23:00 - 07:00 (spans midnight)
night_shift = PeriodSchedule("23:00:00", "07:00:00", tz="UTC")

# For a check at 01:00, this correctly identifies:
# - Start: Previous day 23:00
# - End: Current day 07:00
# - In period: True
```

#### Day of Week Validation
```python
# Check if day of week is valid for this period
check_date = datetime(2024, 1, 15, 12, 0, 0)  # Monday
day_of_week = int(check_date.strftime("%w"))  # 0=Sunday, 1=Monday, etc.

if day_of_week in schedule.valid_days_of_week:
    # This day is valid for the schedule
    pass
```

### Temporal Calculation Methods

#### Period Boundary Detection
- **`is_in_period(datetime)`**: Check if datetime falls within the period
- **`get_start_end_datetimes_for_datetime(datetime)`**: Get period boundaries for a given datetime

#### Relative Time Calculations
- **`duration_since_last_start_datetime(datetime)`**: Time elapsed since last period start
- **`duration_until_next_start_datetime(datetime)`**: Time until next period start
- **`duration_since_last_end_datetime(datetime)`**: Time elapsed since last period end
- **`duration_until_next_end_datetime(datetime)`**: Time until next period end

#### Current Period Calculations
- **`get_current_start_datetime(datetime)`**: Get start of current period (if in period)
- **`get_current_end_datetime(datetime)`**: Get end of current period (if in period)
- **`duration_until_current_start_datetime(datetime)`**: Time until current period start
- **`duration_until_current_end_datetime(datetime)`**: Time until current period end

### Performance Characteristics

#### Computational Efficiency
- **O(1) Period Checks**: Period membership checks are constant time
- **Minimal Object Creation**: Reuses datetime objects where possible
- **Efficient Caching**: Caches timezone and period information

#### Memory Usage
- **Lightweight Objects**: PeriodSchedule instances have minimal memory footprint
- **Stateless Design**: No persistent state that grows over time

### Error Handling

#### Input Validation
```python
# Invalid time format
try:
    schedule = PeriodSchedule("25:00:00", "17:00:00")  # Invalid hour
except ValueError as e:
    print(f"Invalid time format: {e}")

# Invalid day of week
try:
    schedule = PeriodSchedule(
        "09:00:00", "17:00:00",
        valid_days_of_week=[-1, 7]  # Invalid days
    )
except ValueError as e:
    print(f"Invalid days: {e}")

# Invalid timezone
try:
    schedule = PeriodSchedule(
        "09:00:00", "17:00:00",
        tz="Invalid/Timezone"
    )
except Exception as e:
    print(f"Invalid timezone: {e}")
```

#### Edge Cases
- **None Datetime**: Raises ValueError for None input
- **Naive Datetime**: Automatically localizes to schedule timezone
- **Ambiguous Times**: Uses pytz's standard resolution for DST transitions

### Best Practices

#### Timezone Selection
```python
# ✅ Good: Use specific timezone names
schedule = PeriodSchedule("09:00:00", "17:00:00", tz="America/New_York")

# ✅ Good: Use UTC for global systems
global_schedule = PeriodSchedule("14:00:00", "15:00:00", tz="UTC")

# ❌ Avoid: Local timezone in distributed systems
local_schedule = PeriodSchedule("09:00:00", "17:00:00", tz=None)  # Uses UTC
```

#### Period Definition
```python
# ✅ Good: Clear, readable period definitions
office_hours = PeriodSchedule(
    period_start_time_of_day="09:00:00",
    period_end_time_of_day="17:00:00",
    valid_days_of_week=[1, 2, 3, 4, 5],  # Explicit weekdays
    tz="America/New_York"
)

# ✅ Good: Handle overnight periods explicitly
night_processing = PeriodSchedule(
    "22:00:00", "06:00:00",  # Spans midnight
    valid_days_of_week=[0, 1, 2, 3, 4, 5, 6],
    tz="UTC"
)
```

#### Error Handling
```python
from dpn_pyutils.time.periods import PeriodSchedule

def safe_period_check(schedule, check_time):
    """Safely check if time is in period with error handling."""
    try:
        return schedule.is_in_period(check_time)
    except Exception as e:
        print(f"Error checking period: {e}")
        return False

# Usage
schedule = PeriodSchedule("09:00:00", "17:00:00", tz="UTC")
now = datetime.now(pytz.UTC)

is_in_period = safe_period_check(schedule, now)
```

### Integration Examples

#### Calendar System

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime, timedelta
import pytz

class BusinessCalendar:
    def __init__(self):
        self.business_hours = PeriodSchedule(
            "09:00:00", "17:00:00",
            valid_days_of_week=[1, 2, 3, 4, 5],
            tz="America/New_York"
        )

    def get_next_business_day(self, from_date=None):
        """Get the next business day."""
        if from_date is None:
            from_date = datetime.now(pytz.timezone("America/New_York"))

        # Start from next day
        check_date = from_date + timedelta(days=1)

        # Find next weekday
        for _ in range(7):  # Max 7 days to find next business day
            if check_date.weekday() < 5:  # Monday = 0, Friday = 4
                return check_date.replace(hour=9, minute=0, second=0, microsecond=0)
            check_date += timedelta(days=1)

        raise ValueError("No business day found in next 7 days")

    def is_business_time(self, check_time=None):
        """Check if current time is business hours."""
        if check_time is None:
            check_time = datetime.now(pytz.timezone("America/New_York"))
        return self.business_hours.is_in_period(check_time)
```

#### Scheduled Task System

```python
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

class ScheduledTaskRunner:
    def __init__(self):
        self.allowed_periods = {
            'morning': PeriodSchedule("06:00:00", "12:00:00", tz="UTC"),
            'afternoon': PeriodSchedule("12:00:00", "18:00:00", tz="UTC"),
            'night': PeriodSchedule("18:00:00", "24:00:00", tz="UTC")
        }

    def can_run_task(self, task_type, check_time=None):
        """Check if a task type can run at the given time."""
        if check_time is None:
            check_time = datetime.now(pytz.UTC)

        if task_type not in self.allowed_periods:
            return False

        return self.allowed_periods[task_type].is_in_period(check_time)

    def get_next_run_time(self, task_type):
        """Get when a task type can next run."""
        now = datetime.now(pytz.UTC)

        if task_type not in self.allowed_periods:
            raise ValueError(f"Unknown task type: {task_type}")

        schedule = self.allowed_periods[task_type]
        return schedule.get_next_start_datetime(now)

# Usage
runner = ScheduledTaskRunner()
now = datetime.now(pytz.UTC)

print(f"Can run morning task: {runner.can_run_task('morning', now)}")
print(f"Can run night task: {runner.can_run_task('night', now)}")

next_morning = runner.get_next_run_time('morning')
print(f"Next morning task: {next_morning}")
```

### Testing and Validation

```python
import pytest
from dpn_pyutils.time.periods import PeriodSchedule
from datetime import datetime
import pytz

def test_business_hours():
    """Test business hours schedule."""
    business_hours = PeriodSchedule(
        "09:00:00", "17:00:00",
        valid_days_of_week=[1, 2, 3, 4, 5],  # Weekdays
        tz="America/New_York"
    )

    # Test Monday 10 AM (should be in period)
    monday_10am = datetime(2024, 1, 15, 10, 0, 0, tzinfo=pytz.timezone("America/New_York"))
    assert business_hours.is_in_period(monday_10am) == True

    # Test Saturday 10 AM (should not be in period)
    saturday_10am = datetime(2024, 1, 20, 10, 0, 0, tzinfo=pytz.timezone("America/New_York"))
    assert business_hours.is_in_period(saturday_10am) == False

def test_midnight_spanning():
    """Test periods that span midnight."""
    night_shift = PeriodSchedule(
        "22:00:00", "06:00:00",
        tz="UTC"
    )

    # Test 11 PM (should be in period)
    evening_11pm = datetime(2024, 1, 15, 23, 0, 0, tzinfo=pytz.UTC)
    assert night_shift.is_in_period(evening_11pm) == True

    # Test 3 AM (should be in period)
    morning_3am = datetime(2024, 1, 16, 3, 0, 0, tzinfo=pytz.UTC)
    assert night_shift.is_in_period(morning_3am) == True

    # Test 10 AM (should not be in period)
    morning_10am = datetime(2024, 1, 16, 10, 0, 0, tzinfo=pytz.UTC)
    assert night_shift.is_in_period(morning_10am) == False

def test_timezone_conversion():
    """Test timezone conversion behavior."""
    schedule = PeriodSchedule("09:00:00", "17:00:00", tz="UTC")

    # Naive datetime should be localized
    naive_time = datetime(2024, 1, 15, 12, 0, 0)
    localized = schedule.localize_check_datetime(naive_time)
    assert localized.tzinfo is not None

    # Timezone-aware datetime should be converted
    eastern_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.timezone("America/New_York"))
    converted = schedule.localize_check_datetime(eastern_time)
    assert converted.tzinfo == schedule.tz
```

This comprehensive time package provides all the tools needed for sophisticated timezone-aware scheduling and temporal logic in Python applications.
