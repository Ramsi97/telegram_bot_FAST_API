from datetime import datetime, timedelta
from typing import Literal, Optional, Callable

# Define DateType as a Literal for type safety
DateType = Literal["EN", "AMH", "AO", "CUSTOM"]

# Ethiopian calendar constants
SHORT_DAYS = ["ሰ", "ማ", "ረ", "ሐ", "ዓ", "ቅ", "እ"]
ENGLISH_SHORT_DAYS = ["M", "T", "W", "T", "F", "S", "S"]
LONG_DAYS = ["ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ", "እሁድ"]
ETH_MONTHS = [
    "መስከረም", "ጥቅምት", "ህዳር", "ታህሳስ", "ጥር", "የካቲት", "መጋቢት",
    "ሚያዚያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሀሴ", "ጳጉሜ"
]
AO_MONTHS = [
    "Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajji",
    "Guraadhanala", "Bitootesa", "Ebla", "Caamsaa", "Waxabajji",
    "Adoolessa", "Hagayya", "Qaammee"
]


class EthTimeDelta:
    """Represents an Ethiopian time delta."""

    def __init__(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.microseconds = microseconds

    def __repr__(self):
        return f"EthTimeDelta(days={self.days}, hours={self.hours}, minutes={self.minutes}, seconds={self.seconds}, microseconds={self.microseconds})"


class DateDiff:
    """Represents a date difference."""

    def __init__(self, days: int = 0, months: int = 0, years: int = 0, total_days: int = 0):
        self.days = days
        self.months = months
        self.years = years
        self.total_days = total_days

    def __repr__(self):
        return f"DateDiff(days={self.days}, months={self.months}, years={self.years}, total_days={self.total_days})"


class EthDate:
    """Represents an Ethiopian date."""

    def __init__(self, day: int, month: int, year: int):
        self.day = day
        self.month = month
        self.year = year

    def __repr__(self):
        return f"EthDate(day={self.day}, month={self.month}, year={self.year})"

    @classmethod
    def from_dmy_format(cls, date: str) -> "EthDate":
        """
        Create an Ethiopian date from a date string in one of the formats:
            - DD/MM/YYYY (4-digit year)
            - D/M/YY     (2-digit year)
            - And similarly with '-', '.', ':', ' ' separators.

        Examples:
            - "3/2/23"      -> day=3, month=2, year=2023
            - "03-02-2023"  -> day=3, month=2, year=2023
            - "3.2.23"      -> day=3, month=2, year=2023
        """
        if len(date) < 5:  # e.g. "1/1/1" wouldn't be valid
            raise ValueError("Invalid date format: too short to be valid")

        possible_separators = ["/", "-", ".", ":", " "]
        parts = None

        for sep in possible_separators:
            if sep in date:
                split_parts = date.split(sep)
                if len(split_parts) == 3:
                    parts = split_parts
                    break

        if not parts or len(parts) != 3:
            raise ValueError(
                "Invalid date format: cannot parse day, month, year")

        day_str, month_str, year_str = parts

        try:
            day = int(day_str)
            month = int(month_str)
        except ValueError:
            raise ValueError("Day and month must be integers")

        if len(year_str) == 2:
            year = 2000 + int(year_str)
        elif len(year_str) == 4:
            year = int(year_str)
        else:
            raise ValueError(
                "Year must be either 2 or 4 digits for D/M/YY or D/M/YYYY format")

        return cls(day, month, year)

    @classmethod
    def now(cls) -> "EthDate":
        """Get the current Ethiopian date."""
        return to_ethiopian(datetime.now())

    def __eq__(self, other: "EthDate") -> bool:
        """Check if two Ethiopian dates are equal."""
        return self.day == other.day and self.month == other.month and self.year == other.year

    def __lt__(self, other: "EthDate") -> bool:
        """Check if this date is earlier than another date."""
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        return self.day < other.day

    def __le__(self, other: "EthDate") -> bool:
        """Check if this date is earlier than or equal to another date."""
        return self < other or self == other

    def __gt__(self, other: "EthDate") -> bool:
        """Check if this date is later than another date."""
        return not self <= other

    def __ge__(self, other: "EthDate") -> bool:
        """Check if this date is later than or equal to another date."""
        return not self < other

    def __sub__(self, other: "EthDate") -> "DateDiff":
        """Calculate the difference in days between two Ethiopian dates."""
        diff = get_day_no_ethiopian(self) - get_day_no_ethiopian(other)
        return DateDiff(
            total_days=abs(diff),
            years=abs(self.year - other.year),
            months=abs(self.month - other.month),
            days=abs(self.day - other.day)
        )

    def add_days(self, days: int) -> "EthDate":
        """Add days to this Ethiopian date."""
        return create_ethiopian_date(get_day_no_ethiopian(self) + days)

    def add_years(self, years: int) -> "EthDate":
        """Add years to this Ethiopian date."""
        new_year = self.year + years
        if self.month == 13 and self.day == 6 and not is_leap_year_et(new_year):
            return EthDate(5, 13, new_year)
        return EthDate(self.day, self.month, new_year)

    def to_gregorian(self) -> datetime:
        """Convert this Ethiopian date to a Gregorian date."""
        return to_gregorian(self)

    @property
    def is_leap_year(self) -> bool:
        """Check if the year of this Ethiopian date is a leap year."""
        return is_leap_year_et(self.year)

    @property
    def month_length(self) -> int:
        """Get the number of days in the month of this Ethiopian date."""
        return ethiopian_month_length(self.month, self.year)

    @property
    def day_of_week(self) -> str:
        """Get the day of the week for this Ethiopian date."""
        gr_date = to_gregorian(self)
        return LONG_DAYS[gr_date.weekday()]

    def weekday(self) -> int:
        """Return the day of the week as an integer, where ሰኞ is 0 and እሁድ is 6"""
        gr_date = to_gregorian(self)
        return gr_date.weekday()

    def formatted(self, locale: DateType = "AMH") -> str:
        """Format this Ethiopian date as a string (e.g., 'መስከረም 12, 2015')."""
        return f"{get_et_month_name(self.month, locale)} {self.day}, {self.year}"


def create_ethiopian_date_from_parts(day: int, month: int, year: int) -> EthDate:
    """Create an Ethiopian date from day, month, and year."""
    if not is_valid_ethiopian_date(day, month, year):
        raise ValueError("Invalid Ethiopian date")
    return EthDate(day, month, year)


def is_leap_year_et(year: int) -> bool:
    """Check if a year is a leap year in the Ethiopian calendar."""
    return year % 4 == 3


def ethiopian_month_length(month: int, year: int) -> int:
    """Get the number of days in a month in the Ethiopian calendar."""
    if month == 13:
        return 6 if is_leap_year_et(year) else 5
    return 30


def is_valid_ethiopian_date(day: int, month: int, year: int) -> bool:
    """Validate an Ethiopian date."""
    if month < 1 or month > 13:
        return False
    if day < 1 or day > ethiopian_month_length(month, year):
        return False

    if year < 8:
        return False

    return True


def get_day_no_ethiopian(et_date: EthDate) -> int:
    """Calculate the day number for an Ethiopian date."""
    num = et_date.year // 4
    num2 = et_date.year % 4
    return num * 1461 + num2 * 365 + (et_date.month - 1) * 30 + et_date.day - 1


def is_leap_year_gr(year: int) -> bool:
    """Check if a year is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def gregorian_month_length(month: int, year: int) -> int:
    """Get the number of days in a month in the Gregorian calendar."""
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    elif month == 2:
        return 29 if is_leap_year_gr(year) else 28
    return 30


def get_et_month_start_date(month: int, year: int) -> int:
    """Get the starting day of the week for a given Ethiopian month."""
    gr_date = to_gregorian(EthDate(1, month, year))
    return ((gr_date.weekday() or 7) % 7) + 1


def gregorian_date_from_day_no(day_num: int) -> datetime:
    """Convert a day number to a Gregorian date."""
    year = 1
    month = 1
    day = 1

    num400 = day_num // 146097
    day_num %= 146097
    if day_num == 0:
        return datetime(400 * num400, 12, 31)

    num100 = min(day_num // 36524, 3)
    day_num -= num100 * 36524
    if day_num == 0:
        return datetime(400 * num400 + 100 * num100, 12, 31)

    num4 = day_num // 1461
    day_num %= 1461
    if day_num == 0:
        return datetime(400 * num400 + 100 * num100 + 4 * num4, 12, 31)

    num1 = min(day_num // 365, 3)
    day_num -= num1 * 365
    if day_num == 0:
        return datetime(400 * num400 + 100 * num100 + 4 * num4 + num1, 12, 31)

    year += 400 * num400 + 100 * num100 + 4 * num4 + num1

    while True:
        days_in_month = gregorian_month_length(month, year)
        if day_num <= days_in_month:
            day = day_num
            break
        day_num -= days_in_month
        month += 1

    return datetime(year, month, day)


def create_ethiopian_date(day_num: int) -> EthDate:
    """Convert a day number to an Ethiopian date."""
    num = day_num // 1461
    num2 = day_num % 1461
    num3 = num2 // 365
    num4 = num2 % 365
    if num2 != 1460:
        return EthDate((num4 % 30) + 1, (num4 // 30) + 1, num * 4 + num3)
    else:
        return EthDate(6, 13, num * 4 + num3 - 1)


def add_gregorian_months(month: int, year: int) -> int:
    """Calculate the total days up to a given month in the Gregorian calendar."""
    return sum(gregorian_month_length(m, year) for m in range(1, month))


def get_day_no_gregorian(date: datetime) -> int:
    """Calculate the day number for a Gregorian date."""
    years = date.year - 1
    leap_years = years // 4 - years // 100 + years // 400
    non_leap_years = years - leap_years
    days_in_previous_years = leap_years * 366 + non_leap_years * 365
    days_in_current_year = add_gregorian_months(
        date.month, date.year) + date.day
    return days_in_previous_years + days_in_current_year


def to_ethiopian(date: datetime) -> EthDate:
    """Convert a Gregorian date to an Ethiopian date."""
    return create_ethiopian_date(get_day_no_gregorian(date) - 2431)


def to_gregorian(et_date: EthDate) -> datetime:
    """Convert an Ethiopian date to a Gregorian date."""
    return gregorian_date_from_day_no(get_day_no_ethiopian(et_date) + 2431)


def format_et_date(
    et_date: EthDate,
    locale: DateType = "AMH",
    get_local_month: Optional[Callable[[int], str]] = None,
    time: Optional[int] = None,
) -> str:
    """Format an Ethiopian date."""
    month = get_et_month_name(et_date.month, locale, get_local_month)
    if time:
        time_str = (datetime.fromtimestamp(time) -
                    timedelta(hours=6)).strftime("%I:%M %p")
        return f"{month} {et_date.day}/{et_date.year} {time_str}"
    return f"{month} {et_date.day}/{et_date.year}"


def get_et_month_name(
    month: int,
    locale: DateType = "AMH",
    get_local_month: Optional[Callable[[int], str]] = None,
) -> str:
    """Get the name of an Ethiopian month."""
    if 1 <= month <= 13:
        if locale == "AMH":
            return ETH_MONTHS[month - 1]
        elif locale == "AO":
            return AO_MONTHS[month - 1]
        elif locale == "CUSTOM" and get_local_month:
            return get_local_month(month)
    return ""


def get_day_of_week_name_et(day: int) -> str:
    """Get the name of the day of the week in Amharic."""
    if 1 <= day <= 7:
        return LONG_DAYS[day - 1]
    return ""


def to_named_month_string_from_et_date(et_date: EthDate) -> str:
    """Convert an Ethiopian date to a named month string."""
    return f"{get_et_month_name(et_date.month)} {et_date.day}, {et_date.year}"


def add_years(et_date: EthDate, years: int) -> EthDate:
    """Add years to an Ethiopian date."""
    if not is_valid_ethiopian_date(et_date.day, et_date.month, et_date.year):
        raise ValueError("Invalid Ethiopian date")
    new_year = et_date.year + years
    if et_date.month == 13 and et_date.day == 6 and not is_leap_year_et(new_year):
        return EthDate(5, 13, new_year)
    return EthDate(et_date.day, et_date.month, new_year)


def add_days(et_date: EthDate, days: int) -> EthDate:
    """Add days to an Ethiopian date."""
    if not is_valid_ethiopian_date(et_date.day, et_date.month, et_date.year):
        raise ValueError("Invalid Ethiopian date")
    return create_ethiopian_date(get_day_no_ethiopian(et_date) + days)


def compare_dates(date1: EthDate, date2: EthDate) -> int:
    """Compare two Ethiopian dates."""
    if date1.year != date2.year:
        return -1 if date1.year < date2.year else 1
    if date1.month != date2.month:
        return -1 if date1.month < date2.month else 1
    if date1.day != date2.day:
        return -1 if date1.day < date2.day else 1
    return 0
