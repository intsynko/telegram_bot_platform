import requests


class TelegramConnector:
    url = "https://api.telegram.org/bot"

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

        self._offset = 1

    def send_message(self, msg):
        self._send_request(
            url=f"{self.url}{self.bot_token}/sendMessage?chat_id={self.chat_id}",
            json={
                'text': msg,
                'disable_web_page_preview': True
            }
        )

    def _send_request(self, **kwargs):
        resp = requests.post(
            **kwargs
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            raise NotImplementedError()
        return resp
