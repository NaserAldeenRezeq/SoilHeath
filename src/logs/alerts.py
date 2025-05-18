"""AlertManager for sending alerts via Telegram bot."""

import os
import sys

import requests
from src.helpers import get_settings, Settings

# Setup project root path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)



class AlertManager:  # pylint: disable=too-few-public-methods
    """Sends error alerts to a configured Telegram chat using a bot."""

    def __init__(self):
        self.app_settings: Settings = get_settings()
        self.telegram_bot_token = self.app_settings.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = self.app_settings.TELEGRAM_CHAT_ID

    def send_telegram_alert(self, subject: str, message: str) -> None:
        """Sends a formatted alert message to the configured Telegram chat."""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": f"Subject: {subject}\n\nMessage: {message}"
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            print(f"Alert sent to Telegram: {subject}")
        except requests.RequestException as exc:
            print(f"Failed to send alert to Telegram: {exc}")


# Example usage
if __name__ == "__main__":
    alert = AlertManager()
    alert.send_telegram_alert("Test Alert", "This is a test alert from the monitoring system.")
