from datetime import datetime, timedelta
from typing import Any
import requests
from dotenv import dotenv_values


ENV_VARS: dict[str, str | None] = dotenv_values()
STOCK_ENDPOINT = "https://api.polygon.io/v1/open-close/{stocks_ticker}/{date}"
STOCK, COMPANY_NAME = "NU", "Nubank"


def get_data_from_api(date: str) -> dict[str, Any]:
    response = requests.get(
        STOCK_ENDPOINT.format(stocks_ticker=STOCK, date=date),
        params={
            "apiKey": ENV_VARS.get("STOCK_API_KEY")
        }
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    today, date_format = datetime.today(), "%Y-%m-%d"
    yesterday = (today - timedelta(days=1)).strftime(date_format)
    day_before_yesterday = (today - timedelta(days=2)).strftime(date_format)

    yesterday_stock = get_data_from_api(yesterday)
    day_before_yesterday_stock = get_data_from_api(day_before_yesterday)

    day_before_yesterday_closing_price = float(
        day_before_yesterday_stock["close"]
    )
    yesterday_closing_price = float(yesterday_stock["close"])

    percentage_change = abs(
        ((yesterday_closing_price / day_before_yesterday_closing_price) - 1)
        * 100
    )

    if percentage_change >= 5:
        print("Get news!")


if __name__ == "__main__":
    main()
