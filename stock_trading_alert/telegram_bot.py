import requests

BASE_URL = f"https://api.telegram.org"


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.bot_url = f"{BASE_URL}/bot{self.token}"

    def send_text_msg(self, msg: str, chat_id: str | int):
        response = requests.post(
            url=f"{self.bot_url}/sendMessage",
            params={
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "Markdown"
            }
        )
        response.raise_for_status()
        return response.json()
