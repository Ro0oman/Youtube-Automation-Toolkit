import os
import requests
from loguru import logger
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_slack(self, message: str):
        if not self.slack_webhook:
            logger.warning("Slack webhook URL not configured")
            return

        payload = {"text": message}
        try:
            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            logger.info("Slack notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def send_telegram(self, message: str):
        if not (self.telegram_token and self.telegram_chat_id):
            logger.warning("Telegram configuration missing")
            return

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    def notify(self, message: str, channels: Optional[list] = None):
        """Unified notify method"""
        if not channels:
            channels = ["slack", "telegram"]

        if "slack" in channels:
            self.send_slack(message)
        if "telegram" in channels:
            self.send_telegram(message)
