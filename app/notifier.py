# -*- coding: utf-8 -*-
import telegram
from datetime import datetime

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from utils import calc_downtime


class TelegramNotifier:
    @staticmethod
    def _send_msg_(msg):
        try:
            if any(_ is None for _ in [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
                print(f"No telegram bot token (TELEGRAM_BOT_TOKEN) or chat id (TELEGRAM_CHAT_ID) informed. "
                      f"There's no way to notify anyone. Msg: {msg}")
                return

            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        except Exception as e:
            print(f"I was not able to send a message to {TELEGRAM_CHAT_ID}.")
            print(e)

    @staticmethod
    def _get_downtime_str_(conn_history):
        disconnected_timestamp = [ch["event_timestamp"] for ch in conn_history
                                  if ch["event"].lower() == "disconnected"][0]

        connected_timestamp = [ch["event_timestamp"] for ch in conn_history
                               if ch["event"].lower() == "connected"][0]

        return calc_downtime(dt_down=disconnected_timestamp, dt_up=connected_timestamp)

    def notify(self, conn_history):
        downtime_str = self._get_downtime_str_(conn_history=conn_history)
        self._send_msg_(msg=f"Internet is back up! Downtime was: {downtime_str}")
