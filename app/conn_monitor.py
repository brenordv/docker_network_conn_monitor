# -*- coding: utf-8 -*-
import requests
import time
import uuid

from config import TEST_SITE_LIST, DEFAULT_HEADERS, SECONDS_BETWEEN_CHECKS
from conn_monitor_logger import HistoryLogger
from notifier import TelegramNotifier
from statistics_api import start_api_in_background


class ConnectionMonitor:
    def __init__(self, callback=None):
        self.db_logger = HistoryLogger()
        self.current_index = 0
        self.delay_between_checks = SECONDS_BETWEEN_CHECKS
        self.callback_function = callback
        self.is_down = False
        self.correlation_id = None

    @staticmethod
    def _get_new_correlation_id_():
        return str(uuid.uuid4())

    def get_next_site(self):
        try:
            return TEST_SITE_LIST[self.current_index]
        except IndexError:
            self.current_index = 0
            return TEST_SITE_LIST[self.current_index]
        finally:
            self.current_index += 1

    def test_site(self, url):
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS)
            if self.is_down:
                # internet is back up.
                self.is_down = False
                self.db_logger.log_uptime(correlation_id=self.correlation_id, url=url,
                                          status_code=response.status_code)
                if self.callback_function:
                    self.callback_function(self.db_logger.get_events(self.correlation_id))

                self.correlation_id = None

        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as error:
            self.is_down = True
            if self.correlation_id is None:
                self.correlation_id = self._get_new_correlation_id_()
                self.db_logger.log_downtime(correlation_id=self.correlation_id, url=url, error_msg=str(error))

        except Exception as ex:
            if self.correlation_id is None:
                self.correlation_id = self._get_new_correlation_id_()
            self.db_logger.log_exception(correlation_id=self.correlation_id, url=url, error_msg=str(ex))

    def start_monitor(self):
        print("Connection monitor is running...")
        try:
            while True:
                self.test_site(url=self.get_next_site())
                time.sleep(self.delay_between_checks)
        except KeyboardInterrupt:
            print("Connection monitor was stopped by the user...")

        except Exception as e:
            print("Connection monitor stopped because of an fatal error. :/")
            print(e)


def main():
    notifier = TelegramNotifier()
    cm = ConnectionMonitor(callback=notifier.notify)

    start_api_in_background()
    cm.start_monitor()


if __name__ == '__main__':
    main()
