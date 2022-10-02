import datetime as dt
from typing import Any

import requests
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

US_CALENDAR = USFederalHolidayCalendar()
US_BUSINESS_DAY = CustomBusinessDay(calendar=US_CALENDAR)


def get_data_from_api(**kwargs: Any) -> dict[str, Any]:
    for param in ("url", "params"):
        if kwargs.get(param) is None:
            raise ValueError(f"Parameter '{param}' not specified.")

    response = requests.get(**kwargs)
    response.raise_for_status()
    return response.json()


def subtract_days_from_date(
        date: dt.datetime,
        days: int = 0,
        skip_holidays: bool = False,
        skip_weekend: bool = False
) -> dt.datetime:
    if not skip_weekend and not skip_holidays:
        date_result = date - dt.timedelta(days=days)
    else:
        params = {
            "n": days,
            "weekmask": "Sun Mon Tue Wed Thu Fri Sat",
        }

        if skip_holidays:
            params["holidays"] = US_CALENDAR.holidays()

        if skip_weekend:
            params["weekmask"] = "Mon Tue Wed Thu Fri"

        date_result = date - CustomBusinessDay(**params)

    return date_result


def convert_date_to_iso_format(date: dt.datetime) -> str:
    return date.strftime("%Y-%m-%d")


def get_most_recent_business_day(date: dt.datetime) -> dt.date:
    return US_BUSINESS_DAY.rollback(date).date()


def count_days(
        start_date: dt.datetime | dt.date,
        end_date: dt.datetime | dt.date
) -> int:
    if isinstance(start_date, dt.datetime):
        start_date = start_date.date()
    if isinstance(end_date, dt.datetime):
        end_date = end_date.date()

    return (end_date - start_date).days


def calc_percent_change(value1: float, value2: float) -> float:
    return ((value1 / value2) - 1) * 100
