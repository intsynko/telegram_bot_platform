import requests
import logging

logger = logging.getLogger(__name__)


class TelegramConnector:
    url = "https://api.telegram.org/bot"

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

        self._offset = 1
        
        # Проверяем, что токен установлен
        if not self.bot_token:
            logger.warning("SYSTEM_BOT_TOKEN не установлен. Уведомления не будут отправляться.")

    def send_message(self, msg):
        # Если токен не установлен, просто логируем и не отправляем
        if not self.bot_token:
            logger.info(f"Уведомление (не отправлено, нет токена): {msg}")
            return
            
        try:
            self._send_request(
                url=f"{self.url}{self.bot_token}/sendMessage?chat_id={self.chat_id}",
                json={
                    'text': msg,
                    'disable_web_page_preview': True
                }
            )
            logger.info(f"Уведомление отправлено: {msg}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    def _send_request(self, **kwargs):
        resp = requests.post(
            **kwargs
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            logger.error(f"HTTP ошибка при отправке запроса: {ex}")
            raise ex
        return resp
