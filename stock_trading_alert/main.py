from datetime import datetime
from typing import Any

import pytz

import utils
from settings import ENV_VARS
from telegram_bot import TelegramBot


def get_stock_open_and_close_on_date(stock: str, date: str) -> dict[str, Any]:
    endpoint = "https://api.polygon.io/v1/open-close/{stock}/{date}"
    stock_data = utils.get_data_from_api(
        url=endpoint.format(stock=stock, date=date),
        params={"apiKey": ENV_VARS.STOCK_API_KEY}
    )
    return stock_data


def search_news_about_company(keywords: list[str], from_date: str) -> list:
    endpoint = "https://newsapi.org/v2/everything"
    data = utils.get_data_from_api(
        url=endpoint,
        params={
            "q": " OR ".join(keywords),
            "searchIn": "title",
            "from": from_date,
            "sortBy": "popularity",
            "apiKey": ENV_VARS.NEWS_API_KEY
        }
    )

    return data.get("articles", [])


def main() -> None:
    stock_symbol, keywords = "NU", ["Nu Holdings"]
    today = datetime.now(tz=pytz.timezone("US/Eastern"))
    check = utils.count_days(
        utils.get_most_recent_business_day(today), today) == 1

    if check:
        base_date = utils.subtract_days_from_date(
            today, 1, skip_weekend=True, skip_holidays=True
        )
        prev_date = utils.subtract_days_from_date(
            today, 2, skip_weekend=True, skip_holidays=True
        )

        base_date = utils.convert_date_to_iso_format(base_date)
        prev_date = utils.convert_date_to_iso_format(prev_date)

        current_stock = get_stock_open_and_close_on_date(
            stock=stock_symbol, date=base_date
        )
        previous_stock = get_stock_open_and_close_on_date(
            stock=stock_symbol, date=prev_date
        )

        percent_change = utils.calc_percent_change(
            float(current_stock.get("close")),
            float(previous_stock.get("close"))
        )

        if abs(percent_change) >= 5:
            my_news_bot = TelegramBot(token=ENV_VARS.BOT_TOKEN)

            up_down_emoji = "🔺" if percent_change > 0 else "🔻"
            msg = f"{stock_symbol}: {up_down_emoji} " \
                  f"{int(abs(percent_change))}%"

            related_news = search_news_about_company(keywords, prev_date)[:3]

            if len(related_news) > 0:
                msg += "\n*Headline*: {title}\n\n{description}"
                for news_data in related_news:
                    my_news_bot.send_text_msg(
                        msg=msg.format(**news_data),
                        chat_id=ENV_VARS.CHAT_ID
                    )
            else:
                msg += "\nNo news to show."
                my_news_bot.send_text_msg(
                    msg=msg,
                    chat_id=ENV_VARS.CHAT_ID
                )


if __name__ == "__main__":
    main()
