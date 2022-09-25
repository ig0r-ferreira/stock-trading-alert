from datetime import datetime, timedelta
from typing import Any

import pytz
import requests
from dotenv import dotenv_values

ENV_VARS: dict[str, str | None] = dotenv_values()


def get_data_from_api(**kwargs: Any) -> dict[str, Any]:
    for param in ("url", "params"):
        if kwargs.get(param) is None:
            raise ValueError(f"Parameter '{param}' not specified.")

    response = requests.get(**kwargs)
    response.raise_for_status()
    return response.json()


def get_credential(credential: str) -> str:
    credential = ENV_VARS.get(credential)
    if credential is None:
        raise ValueError(f"'{credential}' environment variable not found.")

    return credential


def get_stock_open_and_close_on_date(stock: str, date: str) -> dict[str, Any]:
    endpoint = "https://api.polygon.io/v1/open-close/{stock}/{date}"
    stock_data = get_data_from_api(
        url=endpoint.format(stock=stock, date=date),
        params={
            "apiKey": get_credential("STOCK_API_KEY")
        }
    )

    return stock_data


def subtract_days_from_date(date: datetime, days: int = 0) -> datetime:
    return date - timedelta(days=days)


def convert_date_to_iso_format(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def is_business_day(date: datetime) -> bool:
    day_of_week = date.strftime("%A")
    return day_of_week not in ("Saturday", "Sunday")


def calc_percent_change(value1: float, value2: float) -> float:
    return ((value1 / value2) - 1) * 100


def search_news_about_company(keywords: list[str], from_date: str) -> list:
    endpoint = "https://newsapi.org/v2/everything"
    data = get_data_from_api(
        url=endpoint,
        params={
            "q": " OR ".join(keywords),
            "searchIn": "title",
            "from": from_date,
            "sortBy": "popularity",
            "apiKey": get_credential("NEWS_API_KEY")
        }
    )

    return data.get("articles", [])


def main() -> None:
    stock_symbol, keywords = "NU", ["Nu Holdings"]
    now = datetime.now(tz=pytz.timezone("America/New_York"))

    if is_business_day(now):
        if now.hour <= 17:
            # Get percentage of variation between yesterday and
            # the day before yesterday
            base_date = subtract_days_from_date(now, 1)
            prev_date = subtract_days_from_date(now, 2)
        else:
            # Get percentage of change between today and yesterday
            base_date = now
            prev_date = subtract_days_from_date(now, 1)

        base_date = convert_date_to_iso_format(base_date)
        prev_date = convert_date_to_iso_format(prev_date)

        current_stock = get_stock_open_and_close_on_date(
            stock=stock_symbol, date=base_date
        )
        previous_stock = get_stock_open_and_close_on_date(
            stock=stock_symbol, date=prev_date
        )

        percent_change = calc_percent_change(
            float(current_stock.get("close")),
            float(previous_stock.get("close"))
        )

        if abs(percent_change) >= 5:
            up_down_emoji = "🔺" if percent_change > 0 else "🔻"
            msg = f"{stock_symbol}: {up_down_emoji} " \
                  f"{int(abs(percent_change))}%"

            related_news = search_news_about_company(keywords, prev_date)[:3]

            if len(related_news) > 0:
                msg += "\nHeadline: {title}\nBrief: {description}"
                for news_data in related_news:
                    print(msg.format(**news_data))
            else:
                msg += "\nNo news to show."
                print(msg)


if __name__ == "__main__":
    main()
